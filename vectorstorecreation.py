import os
from typing import List, Optional
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from itertools import chain
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from logger import logger

# Initialize Pinecone client (add your API key and environment)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # Set this in your environment
PINECONE_INDEX_NAME = "chatbot-portfolio"  # Choose your index name

def process_markdown_files(directory: str = "readmes") -> List[List[Document]]:
    """
    Load Markdown files from a directory and return a list of documents.
    (Remains unchanged from original)
    """
    try:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory '{directory}' not found")
        
        docs = []
        for filename in os.listdir(directory):
            if filename.lower().endswith(".md"):
                filepath = os.path.join(directory, filename)
                try:
                    loader = UnstructuredMarkdownLoader(filepath)
                    docs.append(loader.load())
                    logger.info(f"Successfully loaded {filename}")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {str(e)}")
                    continue
        return docs
    
    except Exception as e:
        logger.error(f"Error processing markdown files: {str(e)}")
        raise

def vector_store_creation(
    docs: List[List[Document]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> PineconeVectorStore:
    """
    Create and populate a Pinecone vector store from documents.

    Args:
        docs (List[List[Document]]): List of documents to process.
        chunk_size (int): Size of document chunks.
        chunk_overlap (int): Overlap between chunks.

    Returns:
        PineconeVectorStore: Initialized vector store object.

    Raises:
        ValueError: If input documents are empty or invalid.
        Exception: For errors during vector store creation.
    """
    try:
        if not docs or not any(docs):
            raise ValueError("No valid documents provided")

        # Initialize embeddings
        hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            cache_folder="/app/hf_cache"
        )

        # Initialize Pinecone client
        pc = Pinecone(api_key=PINECONE_API_KEY)
        logger.info("Initialized pinecone client")
        # Create index if it doesn't exist
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=384,  # Dimension of all-MiniLM-L6-v2 embeddings
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-west-2")  # Adjust region as needed
            )

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        
        flat_docs = list(chain.from_iterable(docs))
        splits = text_splitter.split_documents(flat_docs)
        logger.info(f"Created {len(splits)} document chunks")

        # Create and populate vector store
        vector_store = PineconeVectorStore.from_documents(
            documents=splits,
            embedding=hf_embeddings,
            index_name=PINECONE_INDEX_NAME
        )
        
        logger.info("Successfully created and populated Pinecone vector store")
        return vector_store

    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        raise

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
