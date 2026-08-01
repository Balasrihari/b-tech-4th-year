"""Context Compression Service for RAG"""
from typing import List, Dict, Any
from loguru import logger


class ContextCompressionService:
    """Service for compressing retrieved context for RAG"""
    
    def __init__(self, max_tokens: int = 2000, compression_ratio: float = 0.7):
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
    
    def compress_context(
        self,
        documents: List[Dict[str, Any]],
        query: str,
        max_tokens: int = None
    ) -> List[Dict[str, Any]]:
        """
        Compress retrieved context to fit within token limits
        
        Args:
            documents: List of retrieved documents with content and metadata
            query: Original query for relevance scoring
            max_tokens: Maximum tokens for compressed context
            
        Returns:
            Compressed list of documents
        """
        try:
            max_toks = max_tokens or self.max_tokens
            
            # Calculate current token count
            current_tokens = sum(self._estimate_tokens(doc['content']) for doc in documents)
            
            if current_tokens <= max_toks:
                logger.info("Context within token limits, no compression needed")
                return documents
            
            # Calculate target tokens
            target_tokens = int(max_toks * self.compression_ratio)
            
            logger.info(f"Compressing context from {current_tokens} to {target_tokens} tokens")
            
            # Re-rank by relevance to query
            ranked_docs = self._rank_by_relevance(documents, query)
            
            # Select documents until token limit
            compressed = []
            total_tokens = 0
            
            for doc in ranked_docs:
                doc_tokens = self._estimate_tokens(doc['content'])
                
                if total_tokens + doc_tokens <= target_tokens:
                    compressed.append(doc)
                    total_tokens += doc_tokens
                else:
                    # Try to add partial content
                    remaining = target_tokens - total_tokens
                    if remaining > 100:  # Only add if meaningful content
                        partial_content = self._truncate_to_tokens(doc['content'], remaining)
                        compressed.append({
                            **doc,
                            'content': partial_content,
                            'truncated': True
                        })
                    break
            
            logger.info(f"Compressed to {len(compressed)} documents, {total_tokens} tokens")
            return compressed
            
        except Exception as e:
            logger.error(f"Context compression failed: {e}")
            return documents[:5]  # Fallback to first 5 documents
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens
            
        Returns:
            Truncated text
        """
        target_chars = max_tokens * 4
        if len(text) <= target_chars:
            return text
        
        # Truncate at word boundary
        truncated = text[:target_chars]
        last_space = truncated.rfind(' ')
        
        if last_space > target_chars * 0.8:
            return truncated[:last_space] + "..."
        
        return truncated + "..."
    
    def _rank_by_relevance(
        self,
        documents: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Rank documents by relevance to query
        
        Args:
            documents: List of documents
            query: Search query
            
        Returns:
            Ranked list of documents
        """
        query_terms = set(query.lower().split())
        
        scored_docs = []
        for doc in documents:
            content = doc['content'].lower()
            
            # Calculate relevance score
            score = 0
            for term in query_terms:
                if term in content:
                    score += content.count(term)
            
            # Boost documents with higher existing scores
            if 'score' in doc:
                score += doc['score'] * 0.5
            
            scored_docs.append({
                **doc,
                'relevance_score': score
            })
        
        # Sort by relevance
        return sorted(scored_docs, key=lambda x: x['relevance_score'], reverse=True)
    
    def merge_overlapping_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge overlapping document chunks
        
        Args:
            documents: List of document chunks
            
        Returns:
            Merged documents
        """
        if len(documents) <= 1:
            return documents
        
        merged = [documents[0]]
        
        for doc in documents[1:]:
            last_doc = merged[-1]
            
            # Check for overlap (simple heuristic)
            if self._has_overlap(last_doc['content'], doc['content']):
                # Merge
                merged_content = last_doc['content'] + " " + doc['content']
                merged[-1] = {
                    **last_doc,
                    'content': merged_content,
                    'merged': True
                }
            else:
                merged.append(doc)
        
        return merged
    
    def _has_overlap(self, text1: str, text2: str, threshold: int = 50) -> bool:
        """
        Check if two texts have overlapping content
        
        Args:
            text1: First text
            text2: Second text
            threshold: Minimum overlap characters
            
        Returns:
            True if texts overlap
        """
        # Simple check: if end of text1 matches start of text2
        for i in range(threshold, 0, -10):
            if text1[-i:] == text2[:i]:
                return True
        return False


# Global context compression service instance
context_compression_service = ContextCompressionService()
