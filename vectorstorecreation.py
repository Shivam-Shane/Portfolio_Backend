import os
from typing import List, Optional
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from itertools import chain
from langchain_chroma import Chroma
from langchain_core.documents import Document
from logger import logger

def process_markdown_files(directory: str = "readmes") -> List[List[Document]]:
    """
    Load Markdown files from a directory and return a list of documents.

    Args:
        directory (str): Directory containing Markdown files. Defaults to "readmes".

    Returns:
        List[List[Document]]: List of loaded documents.

    Raises:
        FileNotFoundError: If the specified directory doesn't exist.
        Exception: For other unexpected errors during file processing.
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
    persist_directory: str = "./chatbot_portfolio",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> Chroma:
    """
    Create and persist a Chroma vector store from documents.

    Args:
        docs (List[List[Document]]): List of documents to process.
        persist_directory (str): Directory to persist the vector store.
        chunk_size (int): Size of document chunks.
        chunk_overlap (int): Overlap between chunks.

    Returns:
        Chroma: Initialized vector store object.

    Raises:
        ValueError: If input documents are empty or invalid.
        Exception: For errors during vector store creation.
    """
    try:
        if not docs or not any(docs):
            raise ValueError("No valid documents provided")

        # Initialize embeddings with optimized parameters
        hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},  # Adjust based on available hardware
            encode_kwargs={'normalize_embeddings': True},
            cache_folder="/app/hf_cache"
        )

        # Split documents efficiently
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        
        flat_docs = list(chain.from_iterable(docs))
        splits = text_splitter.split_documents(flat_docs)
        logger.info(f"Created {len(splits)} document chunks")

        # Ensure persist directory exists
        os.makedirs(persist_directory, exist_ok=True)

        # Create and populate vector store
        vector_store = Chroma(
            collection_name="chatbot_portfolio",
            embedding_function=hf_embeddings,
            persist_directory=persist_directory
        )
        
        # Add documents in batches for better performance
        batch_size = 1000
        for i in range(0, len(splits), batch_size):
            batch = splits[i:i + batch_size]
            vector_store.add_documents(documents=batch)
            logger.info(f"Processed batch {i//batch_size + 1}")

        return vector_store

    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        raise

def load_vector_store(persist_directory: str = "./chatbot_portfolio") -> Optional[Chroma]:

    """
    Load an existing Chroma vector store from disk.

    Args:
        persist_directory (str): Directory containing the persisted vector store.

    Returns:
        Optional[Chroma]: Loaded vector store object or None if loading fails.

    Raises:
        FileNotFoundError: If the persist directory doesn't exist.
    """
    try:
        if not os.path.exists(persist_directory):
            raise FileNotFoundError(f"Persist directory '{persist_directory}' not found")

        hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            cache_folder="/app/hf_cache"
        )
        
        vector_store = Chroma(
            collection_name="chatbot_portfolio",
            embedding_function=hf_embeddings,
            persist_directory=persist_directory
        )
        
        logger.info(f"Successfully loaded vector store from {persist_directory}")
        return vector_store

    except Exception as e:
        logger.error(f"Error loading vector store: {str(e)}")
        return None
