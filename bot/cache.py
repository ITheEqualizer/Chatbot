"""In-memory cache of QAPair question embeddings for fast similarity search.

Holds every stored question vector in a single, pre-normalized matrix so a chat
request costs one user-message embedding plus one matrix-vector product, instead
of re-embedding the entire corpus on every request. The cache is invalidated by
``post_save``/``post_delete`` signals (wired up in :mod:`bot.apps`) and rebuilt
lazily on the next search, so it stays consistent with the database without a
server restart.
"""
import logging
import threading

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingCache:
    def __init__(self):
        self._ids = []
        self._answers = []
        self._matrix_norm = None  # (N, D) L2-normalized rows, or None when empty
        self._dimension = None
        self._stale = True
        self._lock = threading.Lock()

    def mark_stale(self, *args, **kwargs):
        """Invalidate the cache (signal handler) so it rebuilds on next search."""
        # Serialize invalidation with rebuild completion. Without the lock, a
        # signal arriving mid-rebuild can set this flag before rebuild() resets
        # it to False, losing the newer database change indefinitely.
        with self._lock:
            self._stale = True

    def rebuild(self, expected_dimension):
        """Reload compatible question embeddings into a normalized matrix."""
        from .embedding import decode_embedding
        from .models import QAPair

        ids, answers, vectors = [], [], []
        for pk, answer, blob in QAPair.objects.values_list("id", "answer", "embedding_vector"):
            if not blob:
                continue
            try:
                vector = decode_embedding(blob)
            except Exception:
                logger.warning("Skipping QAPair %s: undecodable embedding", pk)
                continue
            if vector.size != expected_dimension:
                logger.warning(
                    "Skipping QAPair %s: embedding dimension %d does not match "
                    "active model dimension %d",
                    pk,
                    vector.size,
                    expected_dimension,
                )
                continue
            vectors.append(vector)
            ids.append(pk)
            answers.append(answer)

        if vectors:
            matrix = np.vstack(vectors).astype(np.float32)
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0  # avoid divide-by-zero for zero vectors
            self._matrix_norm = matrix / norms
        else:
            self._matrix_norm = None
        self._ids = ids
        self._answers = answers
        self._dimension = expected_dimension
        self._stale = False
        logger.info("EmbeddingCache rebuilt: %d entr%s", len(ids), "y" if len(ids) == 1 else "ies")

    def _ensure_fresh(self, expected_dimension):
        dimension_changed = self._dimension is not None and self._dimension != expected_dimension
        if self._stale or dimension_changed:
            with self._lock:
                dimension_changed = (
                    self._dimension is not None and self._dimension != expected_dimension
                )
                if self._stale or dimension_changed:
                    self.rebuild(expected_dimension)

    def search(self, query_vec):
        """Return ``(best_answer, best_score)`` for a query vector.

        ``best_score`` is cosine similarity in [-1, 1]. ``query_vec`` need not be
        normalized. Returns ``(None, 0.0)`` for an empty corpus or zero query.
        """
        query = np.asarray(query_vec, dtype=np.float32)
        if query.ndim != 1 or query.size == 0:
            return None, 0.0
        self._ensure_fresh(query.size)
        if self._matrix_norm is None or not self._ids:
            return None, 0.0
        magnitude = np.linalg.norm(query)
        if magnitude == 0:
            return None, 0.0
        scores = self._matrix_norm @ (query / magnitude)
        best = int(np.argmax(scores))
        return self._answers[best], float(scores[best])


# Module-level singleton shared across requests within a process.
embedding_cache = EmbeddingCache()
