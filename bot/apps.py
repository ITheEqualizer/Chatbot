from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot"

    def ready(self):
        # Invalidate the in-memory embedding cache whenever a QAPair changes, so
        # the similarity matrix stays consistent with the database without a
        # restart. Connecting signals is cheap and touches neither the DB nor the
        # FastText model, so it's safe to do at startup (including under migrate).
        from django.db.models.signals import post_delete, post_save

        from .cache import embedding_cache
        from .models import QAPair

        post_save.connect(
            embedding_cache.mark_stale, sender=QAPair, dispatch_uid="qapair_cache_invalidate_save"
        )
        post_delete.connect(
            embedding_cache.mark_stale, sender=QAPair, dispatch_uid="qapair_cache_invalidate_delete"
        )
