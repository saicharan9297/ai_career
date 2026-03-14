from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from rag.knowledge_base import CAREER_KNOWLEDGE

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

docs = []
for item in CAREER_KNOWLEDGE:
    doc = Document(
        page_content=item["text"],
        metadata={"role": item["role"], "education": item["education"]}
    )
    docs.append(doc)

vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})