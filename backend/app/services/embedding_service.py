"""
Embedding Service
Handles text embedding generation using sentence-transformers
"""
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class EmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize ChromaDB client if available
        self.chroma_client = None
        if CHROMADB_AVAILABLE:
            try:
                self.chroma_client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="./chroma_db"
                ))
            except Exception as e:
                print(f"Warning: Could not initialize ChromaDB: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            return [0.0] * self.embedding_dim
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def store_embeddings(self, collection_name: str, documents: List[str], 
                        metadatas: List[dict], ids: List[str]) -> None:
        """Store embeddings in ChromaDB"""
        if not self.chroma_client:
            print("Warning: ChromaDB not available, skipping storage")
            return
        
        # Generate embeddings
        embeddings = self.generate_embeddings(documents)
        
        # Get or create collection
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Add embeddings to collection
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query_embeddings(self, collection_name: str, query_text: str, 
                       n_results: int = 5) -> dict:
        """Query embeddings for similar documents"""
        if not self.chroma_client:
            return {"documents": [], "metadatas": [], "distances": []}
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        
        # Get collection
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            return {"documents": [], "metadatas": [], "distances": []}
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from ChromaDB"""
        if not self.chroma_client:
            return
        try:
            self.chroma_client.delete_collection(name=collection_name)
        except:
            pass
    
    def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a collection"""
        if not self.chroma_client:
            return {"name": collection_name, "count": 0}
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
            count = collection.count()
            return {"name": collection_name, "count": count}
        except:
            return {"name": collection_name, "count": 0}
