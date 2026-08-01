"""Hybrid Retrieval Service combining BM25 and Vector Search"""
from typing import List, Dict, Any, Optional
from loguru import logger
from app.services.vector_store import vector_store
from app.services.bm25_service import bm25_service


class HybridRetrievalService:
    """Service for hybrid retrieval combining BM25 and vector search"""
    
    def __init__(self):
        self.vector_weight = 0.7  # Weight for vector search
        self.bm25_weight = 0.3    # Weight for BM25 search
    
    def hybrid_search(
        self,
        query: str,
        collection_name: str = "documents",
        top_k: int = 10,
        where: Optional[Dict[str, Any]] = None,
        alpha: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining BM25 and vector search
        
        Args:
            query: Search query
            collection_name: Name of the collection
            top_k: Number of results to return
            where: Metadata filter for vector search
            alpha: Weight for vector search (0-1), overrides default
            
        Returns:
            List of ranked results with combined scores
        """
        try:
            # Use provided alpha or default
            vector_w = alpha if alpha is not None else self.vector_weight
            bm25_w = 1 - vector_w
            
            logger.info(f"Performing hybrid search with vector weight: {vector_w}, BM25 weight: {bm25_w}")
            
            # Get vector search results
            vector_results = self._get_vector_results(query, collection_name, top_k * 2, where)
            
            # Get BM25 search results
            bm25_results = self._get_bm25_results(query, collection_name, top_k * 2)
            
            # Combine and rerank results
            combined_results = self._combine_results(
                vector_results,
                bm25_results,
                vector_w,
                bm25_w
            )
            
            # Return top-k results
            return combined_results[:top_k]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise
    
    def _get_vector_results(
        self,
        query: str,
        collection_name: str,
        top_k: int,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get vector search results"""
        try:
            results = vector_store.query_documents(
                query_text=query,
                collection_name=collection_name,
                n_results=top_k,
                where=where
            )
            
            formatted = []
            for i, (doc_id, distance, metadata) in enumerate(zip(
                results['ids'][0],
                results['distances'][0],
                results['metadatas'][0]
            )):
                formatted.append({
                    'id': doc_id,
                    'content': results['documents'][0][i],
                    'score': 1 - distance,  # Convert distance to similarity
                    'metadata': metadata,
                    'source': 'vector'
                })
            
            return formatted
            
        except Exception as e:
            logger.warning(f"Vector search failed, returning empty: {e}")
            return []
    
    def _get_bm25_results(
        self,
        query: str,
        collection_name: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Get BM25 search results"""
        try:
            results = bm25_service.search_with_metadata(query, collection_name, top_k)
            
            # Add source information
            for result in results:
                result['source'] = 'bm25'
                result['id'] = result.get('metadata', {}).get('id', f"bm25_{result['index']}")
            
            return results
            
        except Exception as e:
            logger.warning(f"BM25 search failed, returning empty: {e}")
            return []
    
    def _combine_results(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        vector_weight: float,
        bm25_weight: float
    ) -> List[Dict[str, Any]]:
        """
        Combine and rerank results from both search methods
        
        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            vector_weight: Weight for vector scores
            bm25_weight: Weight for BM25 scores
            
        Returns:
            Combined and reranked results
        """
        # Normalize scores
        vector_scores = self._normalize_scores([r['score'] for r in vector_results])
        bm25_scores = self._normalize_scores([r['score'] for r in bm25_results])
        
        # Create score map
        score_map = {}
        
        # Add vector scores
        for i, result in enumerate(vector_results):
            doc_id = result['id']
            score_map[doc_id] = {
                'result': result,
                'vector_score': vector_scores[i],
                'bm25_score': 0.0,
                'combined_score': vector_scores[i] * vector_weight
            }
        
        # Add BM25 scores and combine
        for i, result in enumerate(bm25_results):
            doc_id = result['id']
            if doc_id in score_map:
                # Document in both results
                score_map[doc_id]['bm25_score'] = bm25_scores[i]
                score_map[doc_id]['combined_score'] = (
                    score_map[doc_id]['vector_score'] * vector_weight +
                    bm25_scores[i] * bm25_weight
                )
                # Merge metadata
                score_map[doc_id]['result']['metadata'].update(result.get('metadata', {}))
            else:
                # Document only in BM25
                score_map[doc_id] = {
                    'result': result,
                    'vector_score': 0.0,
                    'bm25_score': bm25_scores[i],
                    'combined_score': bm25_scores[i] * bm25_weight
                }
        
        # Sort by combined score
        sorted_results = sorted(
            score_map.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        # Format final results
        final_results = []
        for item in sorted_results:
            result = item['result']
            result['combined_score'] = item['combined_score']
            result['vector_score'] = item['vector_score']
            result['bm25_score'] = item['bm25_score']
            final_results.append(result)
        
        return final_results
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """
        Normalize scores to 0-1 range
        
        Args:
            scores: List of scores to normalize
            
        Returns:
            Normalized scores
        """
        if not scores:
            return []
        
        max_score = max(scores)
        min_score = min(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [(s - min_score) / (max_score - min_score) for s in scores]
    
    def set_weights(self, vector_weight: float, bm25_weight: float) -> None:
        """
        Set weights for hybrid search
        
        Args:
            vector_weight: Weight for vector search (0-1)
            bm25_weight: Weight for BM25 search (0-1)
        """
        total = vector_weight + bm25_weight
        if total != 1.0:
            vector_weight = vector_weight / total
            bm25_weight = bm25_weight / total
        
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        
        logger.info(f"Updated weights: vector={vector_weight}, bm25={bm25_weight}")


# Global hybrid retrieval service instance
hybrid_retrieval_service = HybridRetrievalService()
