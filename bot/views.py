import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .cache import embedding_cache
from .embedding import sentence_vector

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 1000
FALLBACK_ANSWER = "I didn't get it, please ask with more details!"


def index(request):
    return render(request, "bot/index.html")


@require_POST
def chat_api(request):
    """Match a user message against stored QAPairs and return the best answer.

    The corpus embeddings live in a pre-normalized in-memory matrix
    (:data:`bot.cache.embedding_cache`), so this only embeds the incoming
    message — not every stored question — on each request.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"error": "JSON body must be an object."}, status=400)

    user_message = (data.get("message") or "").strip()
    if not user_message:
        return JsonResponse({"error": "Message must not be empty."}, status=400)
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return JsonResponse(
            {"error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)."},
            status=400,
        )

    try:
        user_vec = sentence_vector(user_message)
    except Exception:
        logger.exception("Failed to embed user message")
        return JsonResponse(
            {"error": "The chatbot model is unavailable. Please try again later."},
            status=503,
        )

    answer, score = embedding_cache.search(user_vec)
    threshold = getattr(settings, "SIMILARITY_THRESHOLD", 0.85)
    if answer is None or score < threshold:
        answer = FALLBACK_ANSWER
    return JsonResponse({"answer": answer})
