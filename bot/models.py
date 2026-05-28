import logging

from django.db import models

logger = logging.getLogger(__name__)


class QAPair(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    # Raw float32 bytes of the question's FastText embedding, computed on save so
    # the chat endpoint never has to re-embed the corpus at request time.
    embedding_vector = models.BinaryField(null=True, blank=True, editable=False)

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        # Compute the question embedding here so it stays in sync with the text.
        # Imported lazily to avoid an import cycle (embedding -> settings only).
        from .embedding import embed_question_bytes

        try:
            self.embedding_vector = embed_question_bytes(self.question)
        except Exception:
            # Don't block an admin save if the model file is unavailable; the row
            # can be backfilled later with `manage.py rebuild_embeddings`.
            logger.warning(
                "Could not compute embedding for QAPair %r on save; run "
                "'manage.py rebuild_embeddings' once the model is available.",
                self.question,
            )
        super().save(*args, **kwargs)
