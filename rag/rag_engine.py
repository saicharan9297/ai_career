from rag.retriever import retrieve
from rag.generator import generate_response

def generate_question(role, topic, difficulty):
    # Create search query
    query = f"{role} {topic}"

    # Retrieve relevant context from knowledge base
    context = retrieve(query)

    # Generate question using LLM
    response = generate_response(context, difficulty)

    return response
