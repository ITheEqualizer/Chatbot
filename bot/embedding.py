"""FastText embedding utilities for the Q&A chatbot.

Central, import-cycle-free home for everything embedding-related: lazy model
loading, language-aware text preprocessing, and vector (de)serialization. Keeping
this separate from ``views`` lets ``models`` and ``cache`` reuse it without
circular imports, and keeps ``fasttext``/``hazm`` imports lazy so the module can
be imported (and unit-tested with a mocked model) without those packages present.
"""
import logging
import re

import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

# English stopwords removed during preprocessing.
_STOPWORDS = {"how", "to", "my", "the", "a", "an", "is", "are", "for", "on", "in", "of"}

# Cached FastText model, loaded lazily on first use.
_model = None


def get_model():
    """Return the FastText model named by ``settings.MODEL_PATH``, cached.

    ``fasttext`` is imported lazily so this module imports cleanly without the
    package installed (e.g. in tests, where the model is mocked). Raises a clear
    ``RuntimeError`` if the model file is missing instead of leaving a dangling
    global that would surface as a ``NameError`` on every request.
    """
    global _model
    if _model is None:
        import fasttext

        model_path = settings.MODEL_PATH
        try:
            _model = fasttext.load_model(model_path)
        except Exception as exc:  # pragma: no cover - exercised manually
            raise RuntimeError(
                f"Could not load the FastText model at '{model_path}'. Download it "
                "(see README), set MODEL_PATH, or change CHATBOT_LANGUAGE. "
                f"Original error: {exc}"
            ) from exc
    return _model


def reset_model_cache():
    """Drop the cached model so the next call reloads it (after a path change)."""
    global _model
    _model = None


def preprocess(text):
    """Lowercase, tokenize on word characters, and drop English stopwords."""
    tokens = re.findall(r"\w+", text.lower())
    return " ".join(t for t in tokens if t not in _STOPWORDS)


def preprocess_for_language(text):
    """Dispatch to the preprocessor for ``settings.CHATBOT_LANGUAGE``."""
    if getattr(settings, "CHATBOT_LANGUAGE", "en").lower() == "fa":
        from .persian_process import preprocess_persian

        return preprocess_persian(text)
    return preprocess(text)


def sentence_vector(text):
    """Return the mean word vector for ``text`` (zero vector if it has no words)."""
    model = get_model()
    words = preprocess_for_language(text).split()
    if not words:
        return np.zeros(model.get_dimension(), dtype=np.float32)
    vectors = [model.get_word_vector(w) for w in words]
    return np.mean(vectors, axis=0).astype(np.float32)


def embed_question_bytes(text):
    """Embed ``text`` and serialize the vector to raw float32 bytes for storage."""
    return np.asarray(sentence_vector(text), dtype=np.float32).tobytes()


def decode_embedding(blob):
    """Deserialize raw float32 bytes back into a numpy vector."""
    return np.frombuffer(blob, dtype=np.float32)


def cosine_similarity(vec1, vec2):
    """Cosine similarity of two vectors; 0.0 if either has zero magnitude."""
    vec1 = np.asarray(vec1, dtype=np.float32)
    vec2 = np.asarray(vec2, dtype=np.float32)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))
