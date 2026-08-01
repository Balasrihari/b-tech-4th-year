"""Query Rewriting Service for RAG"""
from typing import List, Optional
from loguru import logger
from app.services.gemini_service import gemini_service


class QueryRewritingService:
    """Service for rewriting queries to improve RAG retrieval"""
    
    def __init__(self):
        self.rewrite_templates = [
            "What is the definition of {query}?",
            "Explain {query} in detail.",
            "What are the key aspects of {query}?",
            "How does {query} work?",
            "Why is {query} important?"
        ]
    
    async def rewrite_query(
        self,
        original_query: str,
        context: Optional[str] = None,
        num_variations: int = 3
    ) -> List[str]:
        """
        Rewrite query to generate variations for better retrieval
        
        Args:
            original_query: Original user query
            context: Optional context for rewriting
            num_variations: Number of query variations to generate
            
        Returns:
            List of query variations including original
        """
        try:
            queries = [original_query]
            
            # Generate AI-powered variations
            if context:
                ai_variations = await self._ai_rewrite(original_query, context, num_variations)
                queries.extend(ai_variations)
            else:
                # Use template-based variations
                template_variations = self._template_rewrite(original_query, num_variations)
                queries.extend(template_variations)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_queries = []
            for q in queries:
                if q.lower() not in seen:
                    seen.add(q.lower())
                    unique_queries.append(q)
            
            logger.info(f"Generated {len(unique_queries)} query variations")
            return unique_queries
            
        except Exception as e:
            logger.error(f"Query rewriting failed: {e}")
            return [original_query]
    
    async def _ai_rewrite(
        self,
        query: str,
        context: str,
        num_variations: int
    ) -> List[str]:
        """
        Use AI to generate query variations
        
        Args:
            query: Original query
            context: Context for rewriting
            num_variations: Number of variations
            
        Returns:
            List of AI-generated variations
        """
        try:
            prompt = f"""
            Context: {context}
            
            Original Query: {query}
            
            Generate {num_variations} different ways to ask this question that would help retrieve relevant information.
            Return only the variations, one per line.
            """
            
            response = await gemini_service.generate_response(prompt)
            
            if response:
                variations = [line.strip() for line in response.split('\n') if line.strip()]
                return variations[:num_variations]
            
            return []
            
        except Exception as e:
            logger.warning(f"AI query rewriting failed: {e}")
            return []
    
    def _template_rewrite(self, query: str, num_variations: int) -> List[str]:
        """
        Use templates to generate query variations
        
        Args:
            query: Original query
            num_variations: Number of variations
            
        Returns:
            List of template-based variations
        """
        variations = []
        
        for template in self.rewrite_templates[:num_variations]:
            try:
                variation = template.format(query=query)
                variations.append(variation)
            except:
                continue
        
        return variations
    
    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with related terms and synonyms
        
        Args:
            query: Original query
            
        Returns:
            List of expanded queries
        """
        try:
            # Simple expansion: add related terms
            terms = query.split()
            expanded = [query]
            
            # Add variations with "and", "or"
            if len(terms) > 1:
                expanded.append(" and ".join(terms))
                expanded.append(" or ".join(terms))
            
            # Add definition-focused query
            expanded.append(f"definition of {query}")
            expanded.append(f"explain {query}")
            
            return expanded
            
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return [query]
    
    def clarify_query(self, query: str) -> str:
        """
        Clarify ambiguous query
        
        Args:
            query: Original query
            
        Returns:
            Clarified query
        """
        # Simple clarification rules
        clarifications = {
            "it": "the subject",
            "this": "the topic",
            "that": "the concept",
            "they": "the items",
            "them": "the objects"
        }
        
        words = query.split()
        clarified = []
        
        for word in words:
            if word.lower() in clarifications:
                clarified.append(clarifications[word.lower()])
            else:
                clarified.append(word)
        
        return " ".join(clarified)


# Global query rewriting service instance
query_rewriting_service = QueryRewritingService()
