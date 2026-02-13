import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load knowledge base
def load_knowledge():
    with open("rag/knowledge_base/roles_data.json", "r") as f:
        data = json.load(f)
    return data

# Prepare embeddings once
data = load_knowledge()
texts = [item["content"] for item in data]
embeddings = model.encode(texts)

# Retrieve most relevant content
def retrieve(query):
    query_vector = model.encode([query])
    similarities = cosine_similarity(query_vector, embeddings)
    best_match_index = np.argmax(similarities)
    return texts[best_match_index]
