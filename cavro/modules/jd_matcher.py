from typing import Dict, List, Tuple, Optional, Any, Union
import re
import numpy as np
from dataclasses import dataclass
import logging
import difflib
from collections import Counter
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
SEMANTIC_MATCHING_AVAILABLE = False
model = None

try:
    # First try to import torch with error handling
    try:
        import torch
        TORCH_AVAILABLE = True
    except (ImportError, OSError) as e:
        logger.warning(
            f"PyTorch not available: {str(e)}. "
            "Falling back to enhanced keyword matching. "
            "For better results, install with: pip install torch"
        )
        TORCH_AVAILABLE = False
        raise ImportError("PyTorch not available")
    
    # Only try to import sentence-transformers if torch is available
    if TORCH_AVAILABLE:
        try:
            from sentence_transformers import SentenceTransformer, util
            
            # Try to load a CPU-compatible model
            try:
                # Use a smaller model that's more likely to work without CUDA
                model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                SEMANTIC_MATCHING_AVAILABLE = True
                logger.info("Successfully loaded sentence-transformers model on CPU")
            except Exception as e:
                logger.warning(
                    f"Could not load sentence-transformers model: {str(e)}. "
                    "Falling back to enhanced keyword matching. "
                    "You can ignore this if you only need basic functionality."
                )
                SEMANTIC_MATCHING_AVAILABLE = False
                
        except ImportError as e:
            logger.warning(
                f"sentence-transformers not available: {str(e)}. "
                "Using enhanced keyword matching. "
                "For better results, install with: pip install sentence-transformers"
            )
            SEMANTIC_MATCHING_AVAILABLE = False

except ImportError:
    # This will be caught by the outer exception handler
    pass

@dataclass
class MatchResult:
    """Container for job description matching results."""
    match_score: float
    keyword_overlap: List[str]
    missing_keywords: List[str]
    semantic_matches: List[Dict[str, Any]]
    feedback: List[str]

def _preprocess_text(text: str) -> str:
    """
    Clean and preprocess text for matching.
    
    Args:
        text: Input text to preprocess
        
    Returns:
        Preprocessed text in lowercase with special characters removed
    """
    if not text or not isinstance(text, str):
        return ""
    
    try:
        # Remove URLs, emails, and special characters
        text = re.sub(r'http\S+|www\.\S+|\S+@\S+', '', text)
        # Keep only alphanumeric, spaces, and basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()\-]', ' ', text)
        
        # Normalize whitespace and convert to lowercase
        text = ' '.join(text.split()).lower()
        
        return text
    except Exception as e:
        logger.warning(f"Error preprocessing text: {str(e)}")
        return ""

def _extract_key_phrases(text: str, top_n: int = 10) -> List[str]:
    """
    Extract key phrases from text using a combination of frequency and position.
    
    Args:
        text: Input text to extract phrases from
        top_n: Number of top phrases to return
        
    Returns:
        List of top key phrases
    """
    if not text:
        return []
        
    try:
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        if not sentences:
            return []
            
        # Calculate term frequency
        words = []
        for sent in sentences:
            words.extend([w for w in sent.lower().split() if len(w) > 2])
            
        word_freq = Counter(words)
        max_freq = max(word_freq.values()) if word_freq else 1
        
        # Score sentences based on word frequency and position
        phrase_scores = {}
        for i, sent in enumerate(sentences):
            words_in_sentence = sent.lower().split()
            if not words_in_sentence:
                continue
                
            # Position score (earlier sentences get higher weight)
            position_score = 1.0 / (i + 1)
            
            # Length score (medium length sentences are preferred)
            length_score = min(len(words_in_sentence) / 10, 1.0)
            
            # Word score (sum of normalized word frequencies)
            word_score = sum(word_freq.get(w, 0) / max_freq for w in words_in_sentence)
            word_score = word_score / len(words_in_sentence) if words_in_sentence else 0
            
            # Combined score
            score = (word_score * 0.5) + (position_score * 0.3) + (length_score * 0.2)
            phrase_scores[sent] = score
            
        # Get top N phrases
        sorted_phrases = sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True)
        return [phrase for phrase, _ in sorted_phrases[:top_n]]
        
    except Exception as e:
        logger.warning(f"Error extracting key phrases: {str(e)}")
        # Fallback: return first few sentences
        return [s.strip() for s in re.split(r'[.!?]', text)[:top_n] if s.strip()]

def _calculate_keyword_overlap(
    resume_text: str, 
    jd_text: str,
    min_word_length: int = 3,
    stopwords: Optional[set] = None
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate keyword overlap between resume and job description with enhanced matching.
    
    Args:
        resume_text: Text content from the resume
        jd_text: Text content from the job description
        min_word_length: Minimum word length to consider as a keyword
        stopwords: Optional set of stopwords to exclude
        
    Returns:
        Tuple of (match_score, matched_keywords, missing_keywords)
    """
    if not resume_text or not jd_text:
        return 0.0, [], []
        
    # Default stopwords if not provided
    if stopwords is None:
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
            'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
            'will', 'with', 'i', 'me', 'my', 'we', 'our', 'you', 'your', 'they', 'them',
            'their', 'this', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'shall', 'will',
            'should', 'would', 'may', 'might', 'must', 'can', 'could', 'having', 'doing',
            'but', 'if', 'or', 'because', 'until', 'while', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down',
            'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', "don't",
            "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren',
            "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
            'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
            'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
            "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't",
            'won', "won't", 'wouldn', "wouldn't"
        }
    
    try:
        # Tokenize and clean resume text
        resume_words = set(
            word.lower() for word in re.findall(r'\b\w+\b', resume_text)
            if (word.lower() not in stopwords and 
                len(word) >= min_word_length and
                not word.isdigit())
        )
        
        # Tokenize and clean job description text
        jd_words = set(
            word.lower() for word in re.findall(r'\b\w+\b', jd_text)
            if (word.lower() not in stopwords and 
                len(word) >= min_word_length and
                not word.isdigit())
        )
        
        # Calculate exact matches
        exact_matches = resume_words.intersection(jd_words)
        
        # Calculate missing keywords
        missing_keywords = jd_words - exact_matches
        
        # Calculate match score (percentage of JD keywords found in resume)
        match_score = len(exact_matches) / len(jd_words) if jd_words else 0.0
        
        # Add partial matches using difflib for fuzzy matching
        partial_matches = set()
        remaining_jd = jd_words - exact_matches
        remaining_resume = resume_words - exact_matches
        
        for jd_word in remaining_jd:
            # Find best match in resume
            matches = difflib.get_close_matches(jd_word, remaining_resume, n=1, cutoff=0.8)
            if matches:
                partial_matches.add(jd_word)
                remaining_resume.discard(matches[0])
        
        # Update matches and score with partial matches
        if partial_matches:
            exact_matches.update(partial_matches)
            missing_keywords = jd_words - exact_matches
            match_score = len(exact_matches) / len(jd_words) if jd_words else 0.0
        
        # Ensure score is between 0 and 1
        match_score = max(0.0, min(1.0, match_score))
        
        return match_score, sorted(list(exact_matches)), sorted(list(missing_keywords))
        
    except Exception as e:
        logger.warning(f"Error calculating keyword overlap: {str(e)}")
        return 0.0, [], []

def _calculate_semantic_similarity(
    resume_text: str, 
    jd_text: str,
    model: Optional[Any] = None,
    threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Calculate semantic similarity between resume and job description.
    
    Args:
        resume_text: Text content from the resume
        jd_text: Text content from the job description
        model: Optional pre-loaded model (if None, will use keyword matching only)
        threshold: Similarity threshold for considering a match (0-1)
        
    Returns:
        List of dictionaries containing match information
    """
    # If semantic matching is not available, return empty list
    if not SEMANTIC_MATCHING_AVAILABLE:
        logger.debug("Semantic matching not available, using simple keyword matching")
        return []
        
    # Use the provided model or the global one if available
    current_model = model or globals().get('model')
    
    # If still no model, use simple keyword matching
    if current_model is None:
        logger.debug("No model available, using simple keyword matching")
        return []
        
    try:
        # Import nltk inside the function to avoid dependency issues
        try:
            from nltk.tokenize import sent_tokenize
        except ImportError:
            logger.warning("NLTK not available. Install with: pip install nltk")
            return []
        
        # Try to download NLTK data if not available
        try:
            sent_tokenize("Test sentence.")
        except LookupError:
            try:
                import nltk
                nltk.download('punkt')
            except Exception as e:
                logger.warning(f"Failed to download NLTK data: {str(e)}")
                return []
        
        # Tokenize into sentences
        jd_sentences = [s for s in sent_tokenize(jd_text) if len(s.split()) > 3]  # Filter out very short sentences
        resume_sentences = [s for s in sent_tokenize(resume_text) if len(s.split()) > 3]
        
        if not jd_sentences or not resume_sentences:
            return []
            
        try:
            # We already have current_model from the function start
            matches = []
            for jd_sent in jd_sentences:
                for resume_sent in resume_sentences:
                    # Simple word overlap as fallback
                    jd_words = set(jd_sent.lower().split())
                    resume_words = set(resume_sent.lower().split())
                    common_words = jd_words.intersection(resume_words)
                    
                    if len(common_words) > 0:
                        # Simple scoring based on word overlap
                        similarity = len(common_words) / max(len(jd_words), 1)
                        if similarity >= threshold:
                            matches.append({
                                'jd_sentence': jd_sent,
                                'resume_sentence': resume_sent,
                                'similarity': similarity,
                                'is_fallback': True
                            })
            
            # Sort by similarity score and remove duplicates
            seen = set()
            unique_matches = []
            for match in sorted(matches, key=lambda x: x['similarity'], reverse=True):
                key = (match['jd_sentence'], match['resume_sentence'])
                if key not in seen:
                    seen.add(key)
                    unique_matches.append(match)
            
            return unique_matches[:20]  # Return top 20 matches
            
        except Exception as e:
            logger.error(f"Error in semantic encoding: {str(e)}")
            return []
        
    except Exception as e:
        logger.error(f"Error in semantic similarity calculation: {str(e)}")
        return []

def match_resume_to_jd(
    resume_text: str, 
    jd_text: str,
    use_semantic_matching: bool = True,
    semantic_threshold: float = 0.6
) -> MatchResult:
    """
    Match a resume to a job description using both keyword and semantic matching.
    
    Args:
        resume_text: Text content from the resume
        jd_text: Text content from the job description
        use_semantic_matching: Whether to use semantic matching (if available)
        semantic_threshold: Similarity threshold for semantic matching (0-1)
        
    Returns:
        MatchResult object containing matching results and feedback
    """
    if not resume_text or not jd_text:
        return MatchResult(
            match_score=0.0,
            keyword_overlap=[],
            missing_keywords=[],
            semantic_matches=[],
            feedback=["Missing resume or job description text."]
        )
    
    try:
        # Preprocess texts
        resume_clean = _preprocess_text(resume_text)
        jd_clean = _preprocess_text(jd_text)
        
        # Calculate keyword overlap
        keyword_score, keyword_overlap, missing_keywords = _calculate_keyword_overlap(
            resume_clean, 
            jd_clean
        )
        
        # Calculate semantic matches if enabled and available
        semantic_matches = []
        if use_semantic_matching:
            try:
                semantic_matches = _calculate_semantic_similarity(
                    resume_text, 
                    jd_text,
                    model=model,
                    threshold=semantic_threshold
                )
            except Exception as e:
                logger.warning(f"Error during semantic matching: {str(e)}")
                semantic_matches = []
                
            # If we didn't get any semantic matches, log it for debugging
            if not semantic_matches and resume_text and jd_text:
                logger.debug("No semantic matches found, using keyword matching only")
                use_semantic_matching = False
                
        # Calculate overall score (weighted average of keyword and semantic scores)
        overall_score = keyword_score * 100  # Convert to percentage
        
        # Keyword feedback
        if keyword_score >= 0.7:
            feedback.append("✅ Strong keyword match with the job description!")
        elif keyword_score >= 0.4:
            feedback.append("ℹ️ Moderate keyword match with the job description.")
        else:
            feedback.append("⚠️ Low keyword match with the job description.")
        
        # Add top missing keywords (up to 5)
        if missing_keywords:
            feedback.append(
                "🔍 Consider adding these keywords: " + 
                ", ".join(f'"{kw}"' for kw in missing_keywords[:5]) +
                ("..." if len(missing_keywords) > 5 else "")
            )
        
        # Semantic feedback
        if semantic_matches:
            top_matches = [m for m in semantic_matches if m.get('similarity_score', 0) >= 0.8]
            if top_matches:
                feedback.append(f"✨ Found {len(top_matches)} highly relevant experience matches.")
            
            # If using fallback matching, add a note
            if any(m.get('is_fallback', False) for m in semantic_matches):
                feedback.append("💡 Using basic matching. For better results, install: pip install sentence-transformers torch")
        
        # Add key phrases from the job description that are missing
        if missing_keywords and len(missing_keywords) > 5:
            feedback.append(f"📋 Total missing keywords: {len(missing_keywords)}")
        
        # Add a tip for improving the resume
        feedback.append("💡 Tip: Tailor your resume to include more keywords from the job description.")
        
        return MatchResult(
            match_score=min(100, int(overall_score * 100)),  # Ensure score is 0-100
            keyword_overlap=keyword_overlap[:20],  # Limit to top 20 keywords
            missing_keywords=missing_keywords,
            semantic_matches=semantic_matches,
            feedback=feedback
        )
        
    except Exception as e:
        logger.error(f"Error matching resume to job description: {str(e)}")
        return MatchResult(
            match_score=0.0,
            keyword_overlap=[],
            missing_keywords=[],
            semantic_matches=[],
            feedback=["An error occurred while processing your resume. Please try again."]
        )
