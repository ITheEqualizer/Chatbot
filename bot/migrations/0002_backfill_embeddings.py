"""Backfill embedding_vector for any QAPairs created before embeddings existed.

No-ops on a fresh install (no rows) and degrades gracefully if the FastText model
is unavailable (e.g. in CI) — those rows stay NULL and can be filled later with
`manage.py rebuild_embeddings`.
"""
from django.db import migrations


def backfill_embeddings(apps, schema_editor):
    QAPair = apps.get_model("bot", "QAPair")
    pending = QAPair.objects.filter(embedding_vector__isnull=True)
    if not pending.exists():
        return

    try:
        from bot.embedding import embed_question_bytes
    except Exception:
        return

    for pair in pending.iterator():
        try:
            blob = embed_question_bytes(pair.question)
        except Exception:
            # Model unavailable; leave remaining rows for rebuild_embeddings.
            return
        QAPair.objects.filter(pk=pair.pk).update(embedding_vector=blob)


class Migration(migrations.Migration):

    dependencies = [("bot", "0001_initial")]

    operations = [migrations.RunPython(backfill_embeddings, migrations.RunPython.noop)]
