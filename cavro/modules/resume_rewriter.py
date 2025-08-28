import os
import re
import json
import logging
import time
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from config import settings

# Import Gemini lazily to avoid hard dependency at import time
try:
    import google.generativeai as genai
    _HAS_GENAI = True
except Exception:
    _HAS_GENAI = False

__all__ = ['rewrite_bullet_point', 'ResumeRewriter', 'RewriteResult']

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL = settings.GEMINI_MODEL
MAX_RETRIES = 3
DEFAULT_TEMPERATURE = 0.7

# Initialize Gemini if available and configured
if _HAS_GENAI and settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

@dataclass
class RewriteResult:
    """Container for rewrite results."""
    original: str
    rewritten: str
    improvements: List[str]
    success: bool
    error: Optional[str] = None

class ResumeRewriter:
    """
    A class for enhancing resume bullet points using AI.
    Handles bullet point rewriting with configurable AI models and styles.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        """
        Initialize the ResumeRewriter.
        
        Args:
            api_key: Gemini API key. If not provided, will use from settings.
            model: The Gemini model to use for rewriting.
        """
        self.model = model or settings.GEMINI_MODEL
        
        if not (api_key or settings.GEMINI_API_KEY):
            raise ValueError(
                "No Gemini API key provided. Set GEMINI_API_KEY or pass api_key."
            )
        if not _HAS_GENAI:
            raise ImportError("google-generativeai is not installed. Install to use AI rewrite.")

        genai.configure(api_key=api_key or settings.GEMINI_API_KEY)
        self.client = genai.GenerativeModel(self.model)
    
    def _generate_rewrite_prompt(self, bullet_point: str, style: str = "professional") -> str:
        """Generate the prompt for the Gemini model."""
        style_instructions = {
            "professional": "Maintain a professional tone suitable for most industries.",
            "ats_optimized": "Optimize for Applicant Tracking Systems with relevant keywords.",
            "executive": "Use more sophisticated language suitable for executive-level positions.",
            "technical": "Emphasize technical skills and specific technologies used."
        }.get(style.lower(), "")
        
        prompt = f"""
        You are an expert resume writer with 10+ years of experience helping job seekers land their dream jobs.
        Rewrite the following resume bullet point to be more impactful, specific, and achievement-oriented.
        Focus on using strong action verbs and quantifiable results where possible.
        
        Style: {style_instructions}
        
        Original: {bullet_point}
        
        Please provide your response in this exact format:
        
        Rewritten: [Your rewritten bullet point here]
        
        Improvements: [Brief explanation of the improvements made]
        """
        
        return prompt
    
    def _parse_ai_response(self, response: Any) -> Dict[str, Any]:
        """Parse the AI response and extract the rewritten content."""
        try:
            content = response.content.strip()
            # Remove any surrounding quotes if present
            content = re.sub(r'^["\']|["\']$', '', content)
            
            rewritten = ""
            improvements = []
            lines = content.splitlines()
            for line in lines:
                if line.startswith("Rewritten:"):
                    rewritten = line.replace("Rewritten:", "").strip()
                elif line.startswith("Improvements:"):
                    improvements = line.replace("Improvements:", "").strip().split(",")
            
            return {
                "rewritten": rewritten,
                "improvements": improvements
            }
        except (AttributeError, IndexError, KeyError) as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            raise ValueError("Failed to parse AI response") from e
    
    def _call_ai_api(self, prompt: str, max_tokens: int = 150) -> Any:
        """Make the API call to Gemini with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": DEFAULT_TEMPERATURE,
                        "max_output_tokens": max_tokens,
                    },
                    safety_settings=settings.GEMINI_SAFETY_SETTINGS
                )
                return response
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"API call failed after {MAX_RETRIES} attempts: {str(e)}")
                    raise
                logger.warning(f"API call failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                time.sleep(1)  # Simple backoff
    
    def rewrite_bullet_point(
        self, 
        bullet_point: str, 
        style: str = "professional",
        max_tokens: int = 150
    ) -> RewriteResult:
        """
        Rewrite a single bullet point using Gemini AI.
        
        Args:
            bullet_point: The bullet point text to rewrite
            style: The writing style to use (professional, ats_optimized, executive, technical)
            max_tokens: Maximum number of tokens for the AI response
            
        Returns:
            RewriteResult containing the original and rewritten text, improvements, and status
        """
        if not bullet_point or not bullet_point.strip():
            return RewriteResult(
                original="",
                rewritten="",
                improvements="No text provided",
                success=False
            )
            
        try:
            prompt = self._generate_rewrite_prompt(bullet_point, style)
            response = self._call_ai_api(prompt, max_tokens)
            
            # Parse the response
            result = self._parse_ai_response(response)
            
            return RewriteResult(
                original=bullet_point,
                rewritten=result["rewritten"],
                improvements=result["improvements"],
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error rewriting bullet point: {str(e)}")
            return RewriteResult(
                original=bullet_point,
                rewritten="",
                improvements=f"Error: {str(e)}",
                success=False
            ) 
    
    def rewrite_bullet_points(
        self, 
        bullet_points: List[str], 
        style: str = "professional",
        max_tokens: int = 150,
        batch_size: int = 5
    ) -> List[RewriteResult]:
        """
        Rewrite multiple bullet points using Gemini AI.
        
        Args:
            bullet_points: List of bullet point texts to rewrite
            style: The writing style to use
            max_tokens: Maximum tokens per response
            batch_size: Number of bullet points to process in parallel (not yet implemented)
            
        Returns:
            List of RewriteResult objects
        """
        if not bullet_points:
            return []
            
        results = []
        for point in bullet_points:
            try:
                result = self.rewrite_bullet_point(point, style, max_tokens)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing bullet point: {str(e)}")
                results.append(RewriteResult(
                    original=point,
                    rewritten="",
                    improvements=f"Error: {str(e)}",
                    success=False
                ))
        
        return results

def rewrite_bullet_point(
    bullet_point: str, 
    api_key: Optional[str] = None, 
    style: str = "professional"
) -> str:
    """
    Convenience function to rewrite a single bullet point using Gemini AI.
    
    Returns empty string if AI rewriting is disabled or dependencies are missing.
    """
    if not settings.GEMINI_API_KEY or not _HAS_GENAI:
        logger.warning("AI rewriting is disabled (missing API key or dependency)")
        return ""
    try:
        rewriter = ResumeRewriter(api_key=api_key)
        result = rewriter.rewrite_bullet_point(bullet_point, style=style)
        return result.rewritten if result.success else ""
    except Exception as e:
        logger.error(f"Error in rewrite_bullet_point: {str(e)}")
        return ""
