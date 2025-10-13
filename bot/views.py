from turtle import mode
from django.shortcuts import render
import numpy as np
import fasttext
from .models import QAPair
from django.http import JsonResponse
import json
import re
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

# MAKE SURE TO DOWNLOAD THE MODEL FROM THE LINK BELOW AND PLACE IT IN THE ROOT DIRECTORY OF PROJECT
# https://drive.google.com/file/d/1u17AHiicxmfeDbvTyuew60SjXCr19UCu/view?usp=sharing
try:
    model = fasttext.load_model('ChatBot.bin')
except Exception as e:
    print(f"Error loading the model, download it from https://drive.google.com/file/d/1u17AHiicxmfeDbvTyuew60SjXCr19UCu/view?usp=sharing")

stopwords = {"how", "to", "my", "the", "a", "an", "is", "are", "for", "on", "in", "of"}

def preprocess(text):
    text = text.lower()
    tokens = re.findall(r'\w+', text)
    tokens = [t for t in tokens if t not in stopwords]
    return " ".join(tokens)

def sentence_vector(text):
    text = preprocess(text)
    words = text.split()
    if not words:
        return np.zeros(model.get_dimension())
    vectors = [model.get_word_vector(w) for w in words]
    return np.mean(vectors, axis=0)

def cosine_similarity(vec1, vec2):
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

def index(request):
    return render(request, 'bot/index.html')


@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        user_vec = sentence_vector(user_message)
        
        pairs = QAPair.objects.all()
        best_score = 0
        best_answer = "I didn't get it, please ask with more details!"
        
        for pair in pairs:
            question_vec = sentence_vector(pair.question)
            score = cosine_similarity(user_vec, question_vec)
            if score > best_score:
                best_score = score
                best_answer = pair.answer
                
        if best_score < 0.85:
            best_answer = "I didn't get it, please ask with more details!"
            
        return JsonResponse({'answer': best_answer})