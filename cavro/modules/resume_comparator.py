import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .resume_parser import parse_resume, clean_resume_text

class ResumeComparator:
    def __init__(self, samples_dir: str = "data/sample_resumes"):
        """Initialize the ResumeComparator with a directory containing sample resumes.
        
        Args:
            samples_dir: Directory containing subdirectories of sample resumes by role
        """
        self.samples_dir = Path(samples_dir)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.sample_data = self._load_sample_resumes()
        self._fit_vectorizer()
    
    def _load_sample_resumes(self) -> Dict[str, List[Dict]]:
        """Load all sample resumes from the samples directory."""
        sample_data = {}
        
        for role_dir in self.samples_dir.iterdir():
            if role_dir.is_dir():
                role_name = role_dir.name
                sample_data[role_name] = []
                
                for resume_file in role_dir.glob('*.*'):
                    try:
                        with open(resume_file, 'rb') as f:
                            text, _ = parse_resume(f, file_extension=resume_file.suffix[1:])
                            if text:
                                sample_data[role_name].append({
                                    'path': str(resume_file),
                                    'text': clean_resume_text(text),
                                    'role': role_name
                                })
                    except Exception as e:
                        print(f"Error loading {resume_file}: {str(e)}")
        
        return sample_data
    
    def _fit_vectorizer(self):
        """Fit the TF-IDF vectorizer on all sample resumes."""
        all_texts = []
        for role_samples in self.sample_data.values():
            all_texts.extend([s['text'] for s in role_samples])
        
        if all_texts:
            self.vectorizer.fit(all_texts)
    
    def compare_to_samples(self, resume_text: str, top_n: int = 3) -> List[Dict]:
        """Compare the given resume text to all sample resumes.
        
        Args:
            resume_text: Text content of the resume to compare
            top_n: Number of top matches to return
            
        Returns:
            List of dictionaries containing match information
        """
        if not resume_text or not resume_text.strip():
            return []
        
        # Clean and vectorize the input resume
        cleaned_text = clean_resume_text(resume_text)
        input_vec = self.vectorizer.transform([cleaned_text])
        
        # Calculate similarity with all samples
        similarities = []
        for role, samples in self.sample_data.items():
            for sample in samples:
                sample_vec = self.vectorizer.transform([sample['text']])
                similarity = cosine_similarity(input_vec, sample_vec)[0][0]
                similarities.append({
                    'similarity': float(similarity),
                    'role': role,
                    'sample_path': sample['path']
                })
        
        # Sort by similarity (descending) and return top_n
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_n]
    
    def get_improvement_suggestions(self, resume_text: str, target_role: str = None) -> Dict:
        """Get suggestions for improving the resume based on samples.
        
        Args:
            resume_text: Text content of the resume
            target_role: Optional specific role to compare against
            
        Returns:
            Dictionary containing improvement suggestions
        """
        if not resume_text or not resume_text.strip():
            return {"error": "No resume text provided"}
        
        cleaned_text = clean_resume_text(resume_text)
        
        # If target role is specified, only compare with that role's samples
        samples_to_compare = []
        if target_role and target_role in self.sample_data:
            samples_to_compare = self.sample_data[target_role]
        else:
            # Otherwise use all samples
            samples_to_compare = [s for role_samples in self.sample_data.values() for s in role_samples]
        
        if not samples_to_compare:
            return {"error": "No sample resumes available for comparison"}
        
        # Vectorize the input and samples
        all_texts = [s['text'] for s in samples_to_compare] + [cleaned_text]
        vectors = self.vectorizer.fit_transform(all_texts)
        
        # Calculate average vector for samples
        sample_vectors = vectors[:-1]
        avg_sample_vector = sample_vectors.mean(axis=0)
        
        # Get input vector
        input_vector = vectors[-1]
        
        # Calculate similarity to average sample
        similarity = cosine_similarity(input_vector, avg_sample_vector)[0][0]
        
        # Simple keyword analysis (this could be expanded)
        input_words = set(cleaned_text.lower().split())
        common_keywords = set()
        
        for sample in samples_to_compare:
            sample_words = set(sample['text'].lower().split())
            common_keywords.update(sample_words.intersection(input_words))
        
        # Generate suggestions
        suggestions = {
            "overall_similarity": float(similarity),
            "common_keywords": list(common_keywords)[:20],  # Limit number of keywords
            "suggested_improvements": [
                "Consider adding more industry-specific keywords",
                "Highlight measurable achievements with numbers and metrics",
                "Ensure consistent formatting throughout the resume"
            ]
        }
        
        return suggestions
