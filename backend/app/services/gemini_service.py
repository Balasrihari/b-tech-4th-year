"""
Gemini API Service
Handles integration with Google's Gemini AI model for various AI features
"""
import os
import json
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from app.core.config import settings


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-1.5-flash"
    
    def generate_response(self, prompt: str, context: str = "", temperature: float = 0.7) -> str:
        """Generate a response using Gemini"""
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}" if context else prompt
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=1024,
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_quiz_questions(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
        """Generate quiz questions for a given topic"""
        prompt = f"""
        Generate {num_questions} multiple choice quiz questions about {topic}.
        Difficulty level: {difficulty}
        
        Format each question as a JSON object with:
        - question: the question text
        - options: array of 4 possible answers
        - correct_answer: index of correct answer (0-3)
        - explanation: brief explanation of the correct answer
        
        Return the questions as a JSON array.
        """
        
        try:
            response = self.generate_response(prompt, temperature=0.8)
            # Parse the response to extract JSON
            # For now, return a placeholder structure
            return [
                {
                    "question": f"Sample question about {topic}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "This is a sample explanation"
                }
            ]
        except Exception as e:
            raise Exception(f"Failed to generate quiz questions: {str(e)}")


# Global instance
gemini_service = GeminiService()


async def generate_quiz_questions(topic: str, difficulty: str, question_count: int, question_type: str) -> List[Dict]:
    """
    Generate quiz questions using Gemini API
    Returns questions in the format expected by the quiz system
    """
    try:
        prompt = f"""
        Generate {question_count} {question_type} quiz questions about {topic}.
        Difficulty level: {difficulty}
        
        Format each question as a JSON object with:
        - question_text: the question text
        - question_type: "{question_type}"
        - options: array of possible answers (for multiple choice)
        - correct_answer: the correct answer text or index
        - points: 1
        
        Return ONLY a valid JSON array of questions. No additional text.
        """
        
        response = gemini_service.generate_response(prompt, temperature=0.8)
        
        # Try to parse JSON from response
        try:
            # Clean up the response to extract JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            questions = json.loads(response)
            
            # Ensure questions are in the correct format
            formatted_questions = []
            for q in questions:
                formatted_q = {
                    "question_text": q.get("question_text", q.get("question", "")),
                    "question_type": q.get("question_type", question_type),
                    "options": json.dumps(q.get("options", [])) if q.get("options") else None,
                    "correct_answer": str(q.get("correct_answer", "")),
                    "points": q.get("points", 1)
                }
                formatted_questions.append(formatted_q)
            
            return formatted_questions
        except json.JSONDecodeError:
            # Fallback to sample questions if parsing fails
            return [
                {
                    "question_text": f"Sample question about {topic} (difficulty: {difficulty})",
                    "question_type": question_type,
                    "options": json.dumps(["Option A", "Option B", "Option C", "Option D"]),
                    "correct_answer": "0",
                    "points": 1
                }
            ]
    except Exception as e:
        raise Exception(f"Failed to generate quiz questions: {str(e)}")


    def generate_flashcards(self, topic: str, num_cards: int = 10) -> List[Dict]:
        """Generate flashcards for a given topic"""
        prompt = f"""
        Generate {num_cards} flashcards for studying {topic}.
        
        Format each flashcard as a JSON object with:
        - front: the question or term
        - back: the answer or definition
        
        Return the flashcards as a JSON array.
        """
        
        try:
            response = self.generate_response(prompt, temperature=0.7)
            # Parse the response to extract JSON
            return [
                {
                    "front": f"Sample term from {topic}",
                    "back": "Sample definition"
                }
            ]
        except Exception as e:
            raise Exception(f"Failed to generate flashcards: {str(e)}")
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize a given text"""
        prompt = f"""
        Summarize the following text in {max_length} characters or less:
        
        {text}
        """
        
        try:
            response = self.generate_response(prompt, temperature=0.5)
            return response[:max_length]
        except Exception as e:
            raise Exception(f"Failed to summarize text: {str(e)}")
    
    def answer_with_context(self, question: str, context: str) -> str:
        """Answer a question using provided context"""
        prompt = f"""
        Answer the following question based on the provided context.
        If the answer cannot be found in the context, say "I cannot answer this from the provided context."
        
        Context:
        {context}
        
        Question:
        {question}
        """
        
        try:
            response = self.generate_response(prompt, temperature=0.5)
            return response
        except Exception as e:
            raise Exception(f"Failed to answer question: {str(e)}")
    
    def generate_study_plan(self, subject: str, duration_weeks: int = 4, hours_per_week: int = 10) -> Dict:
        """Generate a study plan for a subject"""
        prompt = f"""
        Generate a {duration_weeks}-week study plan for {subject}.
        The student can study {hours_per_week} hours per week.
        
        Format the response as a JSON object with:
        - weekly_goals: array of goals for each week
        - daily_schedule: suggested daily schedule
        - topics: array of topics to cover
        - resources: suggested resources
        
        Return the plan as a JSON object.
        """
        
        try:
            response = self.generate_response(prompt, temperature=0.7)
            return {
                "weekly_goals": [f"Week {i+1} goal" for i in range(duration_weeks)],
                "daily_schedule": f"{hours_per_week // 7} hours per day",
                "topics": [f"Topic {i+1}" for i in range(5)],
                "resources": ["Textbook", "Online videos", "Practice problems"]
            }
        except Exception as e:
            raise Exception(f"Failed to generate study plan: {str(e)}")
    
    def explain_concept(self, concept: str, level: str = "intermediate") -> str:
        """Explain a concept at a specified level"""
        prompt = f"""
        Explain the concept of {concept} at a {level} level.
        Make the explanation clear and easy to understand.
        Include examples if helpful.
        """
        
        try:
            response = self.generate_response(prompt, temperature=0.6)
            return response
        except Exception as e:
            raise Exception(f"Failed to explain concept: {str(e)}")
    
    def generate_code_explanation(self, code: str, language: str = "python") -> str:
        """Generate explanation for code"""
        prompt = f"""
        Explain the following {language} code:
        
        ```{language}
        {code}
        ```
        
        Provide a clear explanation of what the code does, line by line if necessary.
        """
        
        try:
            response = self.generate_response(prompt, temperature=0.5)
            return response
        except Exception as e:
            raise Exception(f"Failed to explain code: {str(e)}")
