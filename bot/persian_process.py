import re
from hazm import Normalizer, word_tokenize, Stemmer, Lemmatizer

normalizer = Normalizer()
stemmer = Stemmer()
lemmatizer = Lemmatizer()

def preprocess_persian(text):
    text = normalizer.normalize(text)
    
    text = re.sub(fr'(.)\1{2,}', r'1', text) # Remove repeated characters
    text = re.sub(r'-+', '', text) # Remove hyphens
    
    text = re.sub(r'[^\w\sآ-ی]', '', text) # Remove non-Persian characters
    
    tokens = word_tokenize(text)
    
    processed_tokens = []
    for token in tokens:
        stemmed = stemmer.stem(token)
        lemmatized = lemmatizer.lemmatize(stemmed)
        processed_tokens.append(lemmatized)
        
    return " ".join(processed_tokens)