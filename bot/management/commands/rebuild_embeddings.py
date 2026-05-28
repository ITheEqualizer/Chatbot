"""Recompute and store the FastText embedding for every QAPair.

Run this after first install (to backfill rows added before embeddings existed)
or whenever the model / CHATBOT_LANGUAGE changes, since stored vectors are tied
to the active model's vector space:

    python manage.py rebuild_embeddings
"""
from django.core.management.base import BaseCommand

from bot.cache import embedding_cache
from bot.embedding import embed_question_bytes
from bot.models import QAPair


class Command(BaseCommand):
    help = "Recompute and store the FastText embedding for every QAPair."

    def handle(self, *args, **options):
        total = QAPair.objects.count()
        if not total:
            self.stdout.write("No QAPairs to embed.")
            return

        updated = 0
        for pair in QAPair.objects.all().iterator():
            blob = embed_question_bytes(pair.question)
            # Bypass save()/signals to avoid recomputing and a per-row signal storm.
            QAPair.objects.filter(pk=pair.pk).update(embedding_vector=blob)
            updated += 1

        embedding_cache.mark_stale()
        self.stdout.write(self.style.SUCCESS(f"Re-embedded {updated} of {total} QAPair(s)."))
