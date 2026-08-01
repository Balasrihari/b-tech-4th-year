"""BM25 Keyword Search Service"""
from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple, Any
from loguru import logger
import re


class BM25Service:
    """Service for BM25 keyword search"""
    
    def __init__(self):
        self.indexes: Dict[str, BM25Okapi] = {}
        self.documents: Dict[str, List[str]] = {}
        self.metadata: Dict[str, List[Dict[str, Any]]] = {}
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25 indexing
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Split into tokens
        tokens = text.split()
        
        return tokens
    
    def create_index(
        self,
        collection_name: str,
        documents: List[str],
        metadata: List[Dict[str, Any]] = None
    ) -> None:
        """
        Create BM25 index for a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadata: Optional metadata for each document
        """
        try:
            # Tokenize documents
            tokenized_docs = [self.tokenize(doc) for doc in documents]
            
            # Create BM25 index
            self.indexes[collection_name] = BM25Okapi(tokenized_docs)
            self.documents[collection_name] = documents
            self.metadata[collection_name] = metadata or [{}] * len(documents)
            
            logger.info(f"Created BM25 index for {collection_name} with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to create BM25 index for {collection_name}: {e}")
            raise
    
    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Search using BM25
        
        Args:
            collection_name: Name of the collection
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (doc_index, score) tuples
        """
        try:
            if collection_name not in self.indexes:
                logger.warning(f"Collection {collection_name} not found")
                return []
            
            # Tokenize query
            tokenized_query = self.tokenize(query)
            
            # Search
            scores = self.indexes[collection_name].get_scores(tokenized_query)
            
            # Get top-k results
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            
            results = [(idx, scores[idx]) for idx in top_indices if scores[idx] > 0]
            
            logger.info(f"BM25 search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            raise
    
    def search_with_metadata(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search using BM25 and return results with metadata
        
        Args:
            collection_name: Name of the collection
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with document content, score, and metadata
        """
        try:
            results = self.search(collection_name, query, top_k)
            
            formatted_results = []
            for doc_idx, score in results:
                formatted_results.append({
                    'content': self.documents[collection_name][doc_idx],
                    'score': score,
                    'metadata': self.metadata[collection_name][doc_idx],
                    'index': doc_idx
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"BM25 search with metadata failed: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadata: List[Dict[str, Any]] = None
    ) -> None:
        """
        Add documents to existing collection (rebuilds index)
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts to add
            metadata: Optional metadata for each document
        """
        try:
            # Get existing documents if collection exists
            existing_docs = self.documents.get(collection_name, [])
            existing_metadata = self.metadata.get(collection_name, [])
            
            # Add new documents
            all_docs = existing_docs + documents
            all_metadata = existing_metadata + (metadata or [{}] * len(documents))
            
            # Rebuild index
            self.create_index(collection_name, all_docs, all_metadata)
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {e}")
            raise
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection
        
        Args:
            collection_name: Name of the collection
        """
        try:
            if collection_name in self.indexes:
                del self.indexes[collection_name]
                del self.documents[collection_name]
                del self.metadata[collection_name]
                logger.info(f"Deleted BM25 collection {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection statistics
        """
        if collection_name not in self.indexes:
            return {"name": collection_name, "count": 0}
        
        return {
            "name": collection_name,
            "count": len(self.documents[collection_name])
        }


# Global BM25 service instance
bm25_service = BM25Service()
