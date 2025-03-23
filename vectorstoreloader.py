import os
from typing import  Optional
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from logger import logger

# Initialize Pinecone client (add your API key and environment)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # Set this in your environment
PINECONE_INDEX_NAME = "chatbot-portfolio"  # Choose your index name

def load_vector_store() -> Optional[PineconeVectorStore]:
    """
    Load an existing Pinecone vector store.

    Returns:
        Optional[PineconeVectorStore]: Loaded vector store object or None if loading fails.
    """
    try:
        # Initialize embeddings
        hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            cache_folder="/app/hf_cache"
        )

        # Initialize Pinecone client and verify index exists
        pc = Pinecone(api_key=PINECONE_API_KEY)
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            raise ValueError(f"Pinecone index '{PINECONE_INDEX_NAME}' not found")

        # Load existing vector store
        vector_store = PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            embedding=hf_embeddings
        )
        
        logger.info(f"Successfully loaded Pinecone vector store")
        return vector_store

    except Exception as e:
        logger.error(f"Error loading vector store: {str(e)}")
        return None
