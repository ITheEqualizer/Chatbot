import json
import threading
from unittest import mock

import numpy as np
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from bot import embedding
from bot.cache import EmbeddingCache, embedding_cache
from bot.models import QAPair


class FakeFastText:
    """Deterministic stand-in for a FastText model (4-d, fixed vocabulary).

    Lets the suite exercise embedding/cache/view logic without the multi-GB
    model file or the fasttext package installed.
    """

    DIM = 4
    VOCAB = {
        "reset": [1, 0, 0, 0],
        "password": [0, 1, 0, 0],
        "track": [0, 0, 1, 0],
        "order": [0, 0, 0, 1],
    }

    def get_dimension(self):
        return self.DIM

    def get_word_vector(self, word):
        return np.array(self.VOCAB.get(word, [0, 0, 0, 0]), dtype=np.float32)


class BotTestCase(TestCase):
    """Base case that injects the fake model and resets the shared cache."""

    def setUp(self):
        self._orig_model = embedding._model
        embedding._model = FakeFastText()
        embedding_cache.mark_stale()

    def tearDown(self):
        embedding._model = self._orig_model
        embedding_cache.mark_stale()


class PreprocessTests(TestCase):
    def test_lowercases_and_strips_stopwords(self):
        self.assertEqual(embedding.preprocess("How to RESET my Password"), "reset password")

    def test_strips_punctuation(self):
        self.assertEqual(embedding.preprocess("track, order!"), "track order")

    def test_all_stopwords_or_empty(self):
        self.assertEqual(embedding.preprocess(""), "")
        self.assertEqual(embedding.preprocess("the a an is"), "")


class IndexAccessibilityTests(TestCase):
    def test_question_input_has_persistent_label(self):
        response = self.client.get(reverse("index"))

        self.assertContains(
            response,
            '<label class="is-sr-only" for="user-input">Question</label>',
            html=True,
        )


class CosineTests(TestCase):
    def test_identical_vectors(self):
        v = np.array([1.0, 2.0, 3.0])
        self.assertAlmostEqual(embedding.cosine_similarity(v, v), 1.0, places=5)

    def test_orthogonal_vectors(self):
        self.assertAlmostEqual(
            embedding.cosine_similarity([1, 0, 0], [0, 1, 0]), 0.0, places=5
        )

    def test_zero_vector(self):
        self.assertEqual(embedding.cosine_similarity([0, 0, 0], [1, 2, 3]), 0.0)


class EmbeddingTests(BotTestCase):
    def test_sentence_vector_dimension(self):
        self.assertEqual(embedding.sentence_vector("reset password").shape, (4,))

    def test_unknown_words_are_zero(self):
        self.assertTrue(np.allclose(embedding.sentence_vector("banana mango"), 0.0))

    def test_serialize_round_trip(self):
        original = embedding.sentence_vector("reset password")
        decoded = embedding.decode_embedding(embedding.embed_question_bytes("reset password"))
        self.assertTrue(np.allclose(original, decoded))


class ModelSaveTests(BotTestCase):
    def test_save_populates_embedding(self):
        pair = QAPair.objects.create(question="reset password", answer="A")
        self.assertIsNotNone(pair.embedding_vector)
        decoded = embedding.decode_embedding(pair.embedding_vector)
        self.assertTrue(np.allclose(decoded, embedding.sentence_vector("reset password")))

    def test_failed_reembedding_clears_stale_vector(self):
        pair = QAPair.objects.create(question="reset password", answer="A")
        pair.question = "track order"

        with mock.patch(
            "bot.embedding.embed_question_bytes", side_effect=RuntimeError("model unavailable")
        ):
            pair.save()

        pair.refresh_from_db()
        self.assertIsNone(pair.embedding_vector)
        self.assertEqual(
            embedding_cache.search(embedding.sentence_vector("reset password")),
            (None, 0.0),
        )

    def test_partial_question_save_persists_new_embedding(self):
        pair = QAPair.objects.create(question="reset password", answer="A")
        pair.question = "track order"
        pair.save(update_fields={"question"})

        pair.refresh_from_db()
        decoded = embedding.decode_embedding(pair.embedding_vector)
        self.assertTrue(np.allclose(decoded, embedding.sentence_vector("track order")))

    def test_partial_answer_save_does_not_reembed_unchanged_question(self):
        pair = QAPair.objects.create(question="reset password", answer="A")
        pair.answer = "B"

        with mock.patch("bot.embedding.embed_question_bytes") as embed:
            pair.save(update_fields={"answer"})

        embed.assert_not_called()


class CacheTests(BotTestCase):
    def test_invalidation_waits_for_rebuild_lock(self):
        cache = EmbeddingCache()
        cache._stale = False
        started = threading.Event()
        completed = threading.Event()

        def invalidate():
            started.set()
            cache.mark_stale()
            completed.set()

        cache._lock.acquire()
        thread = threading.Thread(target=invalidate)
        try:
            thread.start()
            self.assertTrue(started.wait(timeout=1))
            self.assertFalse(completed.wait(timeout=0.1))
        finally:
            cache._lock.release()

        self.assertTrue(completed.wait(timeout=1))
        thread.join(timeout=1)
        self.assertFalse(thread.is_alive())
        self.assertTrue(cache._stale)

    def test_search_returns_best_match(self):
        QAPair.objects.create(question="reset password", answer="reset-answer")
        QAPair.objects.create(question="track order", answer="track-answer")
        answer, score = embedding_cache.search(embedding.sentence_vector("reset password"))
        self.assertEqual(answer, "reset-answer")
        self.assertAlmostEqual(score, 1.0, places=5)

    def test_search_skips_embeddings_from_a_different_model_dimension(self):
        QAPair.objects.create(question="reset password", answer="reset-answer")
        QAPair.objects.bulk_create(
            [
                QAPair(
                    question="incompatible",
                    answer="wrong-answer",
                    embedding_vector=np.ones(3, dtype=np.float32).tobytes(),
                )
            ]
        )

        answer, score = embedding_cache.search(embedding.sentence_vector("reset password"))

        self.assertEqual(answer, "reset-answer")
        self.assertAlmostEqual(score, 1.0, places=5)

    def test_invalidation_on_create_and_delete(self):
        QAPair.objects.create(question="reset password", answer="reset-answer")
        embedding_cache.search(embedding.sentence_vector("reset password"))  # warm cache

        pair = QAPair.objects.create(question="track order", answer="track-answer")
        answer, _ = embedding_cache.search(embedding.sentence_vector("track order"))
        self.assertEqual(answer, "track-answer")  # new row visible without restart

        pair.delete()
        answer, _ = embedding_cache.search(embedding.sentence_vector("track order"))
        self.assertEqual(answer, "reset-answer")  # falls back to the remaining row

    def test_empty_corpus(self):
        self.assertEqual(embedding_cache.search(embedding.sentence_vector("reset")), (None, 0.0))


@override_settings(SIMILARITY_THRESHOLD=0.85)
class ChatApiTests(BotTestCase):
    def setUp(self):
        super().setUp()
        QAPair.objects.create(question="reset password", answer="Go to settings to reset it.")
        QAPair.objects.create(question="track order", answer="Use the tracking page.")
        self.url = reverse("chat_api")

    def _post(self, payload, **kwargs):
        return self.client.post(self.url, data=json.dumps(payload), content_type="application/json", **kwargs)

    def test_match_above_threshold(self):
        res = self._post({"message": "reset password"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["answer"], "Go to settings to reset it.")

    def test_below_threshold_falls_back(self):
        res = self._post({"message": "reset track"})  # cosine 0.5 to each, < 0.85
        self.assertEqual(res.status_code, 200)
        self.assertIn("didn't get it", res.json()["answer"])

    def test_unknown_words_fall_back(self):
        res = self._post({"message": "banana mango"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("didn't get it", res.json()["answer"])

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_invalid_json(self):
        res = self.client.post(self.url, data="not json", content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_non_object_json(self):
        for payload in ([], "message"):
            with self.subTest(payload=payload):
                res = self._post(payload)
                self.assertEqual(res.status_code, 400)
                self.assertEqual(res.json(), {"error": "JSON body must be an object."})

    def test_non_string_message(self):
        for message in (123, True, [], {}):
            with self.subTest(message=message):
                res = self._post({"message": message})
                self.assertEqual(res.status_code, 400)
                self.assertEqual(res.json(), {"error": "Message must be a string."})

    def test_empty_message(self):
        self.assertEqual(self._post({"message": "   "}).status_code, 400)

    def test_missing_message(self):
        self.assertEqual(self._post({}).status_code, 400)


class CsrfTests(BotTestCase):
    def setUp(self):
        super().setUp()
        QAPair.objects.create(question="reset password", answer="answer")
        self.url = reverse("chat_api")

    def test_post_without_token_is_forbidden(self):
        client = Client(enforce_csrf_checks=True)
        res = client.post(self.url, data=json.dumps({"message": "reset password"}), content_type="application/json")
        self.assertEqual(res.status_code, 403)

    def test_post_with_token_succeeds(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("index"))  # renders {% csrf_token %} -> sets csrftoken cookie
        token = client.cookies["csrftoken"].value
        res = client.post(
            self.url,
            data=json.dumps({"message": "reset password"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(res.status_code, 200)
