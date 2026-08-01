"""Cross-Encoder Reranking Service for RAG"""
from typing import List, Dict, Any, Tuple
from loguru import logger
import torch
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """Service for reranking retrieved documents using cross-encoder model"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize cross-encoder reranker
        
        Args:
            model_name: HuggingFace model name for cross-encoder
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.model = CrossEncoder(model_name, device=self.device)
            logger.info(f"Cross-encoder model loaded: {model_name} on {self.device}")
        except Exception as e:
            logger.warning(f"Failed to load cross-encoder model: {e}. Reranking will be disabled.")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using cross-encoder
        
        Args:
            query: Search query
            documents: List of documents with content and metadata
            top_k: Number of top results to return
            
        Returns:
            Reranked list of documents
        """
        if self.model is None:
            logger.warning("Cross-encoder model not available, returning original order")
            return documents
        
        try:
            # Prepare query-document pairs
            pairs = []
            for doc in documents:
                content = doc.get('content', '')
                pairs.append([query, content])
            
            # Get cross-encoder scores
            scores = self.model.predict(pairs)
            
            # Add scores to documents
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
            
            # Sort by rerank score
            reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
            
            # Return top-k if specified
            if top_k:
                reranked = reranked[:top_k]
            
            logger.info(f"Reranked {len(documents)} documents to top-{len(reranked)}")
            return reranked
            
        except Exception as e:
            logger.error(f"Cross-encoder reranking failed: {e}")
            return documents
    
    def rerank_with_threshold(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents and filter by threshold
        
        Args:
            query: Search query
            documents: List of documents
            threshold: Minimum score threshold
            
        Returns:
            Reranked and filtered documents
        """
        reranked = self.rerank(query, documents)
        
        # Filter by threshold
        filtered = [doc for doc in reranked if doc.get('rerank_score', 0) >= threshold]
        
        logger.info(f"Filtered to {len(filtered)} documents above threshold {threshold}")
        return filtered
    
    def get_top_k_with_scores(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Get top-k documents with their rerank scores
        
        Args:
            query: Search query
            documents: List of documents
            top_k: Number of top results
            
        Returns:
            List of (document, score) tuples
        """
        reranked = self.rerank(query, documents, top_k)
        
        results = []
        for doc in reranked:
            results.append((doc, doc.get('rerank_score', 0)))
        
        return results
    
    def batch_rerank(
        self,
        queries: List[str],
        documents_list: List[List[Dict[str, Any]]],
        top_k: int = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Batch rerank multiple queries
        
        Args:
            queries: List of queries
            documents_list: List of document lists for each query
            top_k: Number of top results per query
            
        Returns:
            List of reranked document lists
        """
        results = []
        
        for query, documents in zip(queries, documents_list):
            reranked = self.rerank(query, documents, top_k)
            results.append(reranked)
        
        return results


# Global cross-encoder reranker instance
cross_encoder_reranker = CrossEncoderReranker()
