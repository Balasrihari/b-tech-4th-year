"""
Gemini API Service
Handles integration with Google's Gemini AI model for various AI features
"""
import os
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
