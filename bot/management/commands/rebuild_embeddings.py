"""Recompute and store the FastText embedding for every QAPair.

Run this after first install (to backfill rows added before embeddings existed)
or whenever the model / CHATBOT_LANGUAGE changes, since stored vectors are tied
to the active model's vector space:

    python manage.py rebuild_embeddings
"""
from django.core.management.base import BaseCommand
from django.db import transaction

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

        replacements = [
            (pair.pk, embed_question_bytes(pair.question))
            for pair in QAPair.objects.all().iterator()
        ]

        with transaction.atomic():
            for pk, blob in replacements:
                # Bypass save()/signals to avoid recomputing and a per-row signal storm.
                QAPair.objects.filter(pk=pk).update(embedding_vector=blob)

        embedding_cache.mark_stale()
        self.stdout.write(
            self.style.SUCCESS(f"Re-embedded {len(replacements)} of {total} QAPair(s).")
        )
