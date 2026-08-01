"""Vector Store Service using ChromaDB"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from loguru import logger
import os


class VectorStore:
    """Service for managing vector embeddings with ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Collection names
        self.documents_collection = "documents"
        self.quizzes_collection = "quizzes"
        self.flashcards_collection = "flashcards"
        
        logger.info(f"Vector store initialized at {persist_directory}")
    
    def get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_or_create_collection(name)
        except Exception as e:
            logger.error(f"Failed to get/create collection {name}: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        collection_name: str = "documents"
    ) -> None:
        """
        Add documents to vector store
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique IDs
            collection_name: Name of the collection
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {e}")
            raise
    
    def query_documents(
        self,
        query_text: str,
        collection_name: str = "documents",
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query documents from vector store
        
        Args:
            query_text: Query text
            collection_name: Name of the collection
            n_results: Number of results to return
            where: Metadata filter
            where_document: Document content filter
            
        Returns:
            Dictionary with query results
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            logger.info(f"Query returned {len(results['ids'][0])} results from {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to query {collection_name}: {e}")
            raise
    
    def delete_documents(
        self,
        ids: List[str],
        collection_name: str = "documents"
    ) -> None:
        """
        Delete documents from vector store
        
        Args:
            ids: List of document IDs to delete
            collection_name: Name of the collection
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete documents from {collection_name}: {e}")
            raise
    
    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        collection_name: str = "documents"
    ) -> None:
        """
        Update documents in vector store
        
        Args:
            ids: List of document IDs to update
            documents: List of updated document texts
            metadatas: List of updated metadata
            collection_name: Name of the collection
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Updated {len(ids)} documents in {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to update documents in {collection_name}: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str = "documents") -> Dict[str, Any]:
        """
        Get statistics for a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for {collection_name}: {e}")
            raise
    
    def reset_collection(self, collection_name: str = "documents") -> None:
        """
        Reset/delete a collection
        
        Args:
            collection_name: Name of the collection
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Reset collection {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to reset collection {collection_name}: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise


# Global vector store instance
vector_store = VectorStore()
