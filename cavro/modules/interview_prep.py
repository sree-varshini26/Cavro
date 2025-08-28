import re
import logging
import random
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InterviewQuestion:
    """Represents an interview question with metadata."""
    question: str
    category: str
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    tags: List[str]
    answer_guidance: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None

def load_question_bank() -> Dict[str, Dict[str, List[Dict]]]:
    """Load interview questions from a JSON file or return default questions."""
    try:
        # Try to load from a data file if it exists
        data_file = Path(__file__).parent.parent / 'data' / 'interview_questions.json'
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load question bank: {str(e)}. Using default questions.")
    
    # Default question bank if file loading fails
    return {
        "programming_languages": {
            "python": [
                {
                    "question": "Explain Python's Global Interpreter Lock (GIL) and its implications.",
                    "difficulty": "intermediate",
                    "tags": ["concurrency", "performance", "cpython"],
                    "answer_guidance": "Discuss what GIL is, why it exists, and how it affects multi-threaded Python programs."
                },
                {
                    "question": "What are Python decorators and how would you use them?",
                    "difficulty": "intermediate",
                    "tags": ["functions", "syntax", "design patterns"],
                    "answer_guidance": "Explain the concept of decorators, their syntax, and common use cases like logging, timing, and access control."
                },
                {
                    "question": "How does Python manage memory?",
                    "difficulty": "advanced",
                    "tags": ["memory management", "performance"],
                    "answer_guidance": "Discuss reference counting, garbage collection, and memory allocation in Python."
                }
            ],
            "javascript": [
                {
                    "question": "Explain the event loop in JavaScript.",
                    "difficulty": "intermediate",
                    "tags": ["asynchronous", "concurrency"],
                    "answer_guidance": "Describe how the call stack, callback queue, and event loop work together."
                }
            ],
            "java": [
                {
                    "question": "What is the difference between an interface and an abstract class in Java?",
                    "difficulty": "intermediate",
                    "tags": ["OOP", "inheritance", "abstraction"]
                }
            ]
        },
        "data_science": {
            "machine_learning": [
                {
                    "question": "Explain the bias-variance tradeoff.",
                    "difficulty": "intermediate",
                    "tags": ["modeling", "theory"]
                },
                {
                    "question": "What is the difference between bagging and boosting?",
                    "difficulty": "intermediate",
                    "tags": ["ensemble methods", "algorithms"]
                }
            ],
            "deep_learning": [
                {
                    "question": "What is the vanishing gradient problem and how can it be addressed?",
                    "difficulty": "advanced",
                    "tags": ["neural networks", "training", "optimization"]
                }
            ]
        },
        "system_design": [
            {
                "question": "How would you design a URL shortening service like bit.ly?",
                "difficulty": "advanced",
                "tags": ["distributed systems", "scalability"],
                "follow_up_questions": [
                    "How would you handle URL collisions?",
                    "How would you scale this to handle millions of requests per second?",
                    "How would you track click analytics?"
                ]
            },
            {
                "question": "Design a distributed key-value store.",
                "difficulty": "advanced",
                "tags": ["distributed systems", "storage"]
            }
        ],
        "algorithms": [
            {
                "question": "Implement an LRU cache.",
                "difficulty": "medium",
                "tags": ["data structures", "caching"]
            },
            {
                "question": "Find the kth largest element in an unsorted array.",
                "difficulty": "medium",
                "tags": ["arrays", "sorting", "searching"]
            }
        ],
        "behavioral": [
            {
                "question": "Tell me about a time you faced a difficult technical challenge and how you overcame it.",
                "difficulty": "all",
                "tags": ["experience", "problem-solving"]
            },
            {
                "question": "Describe a situation where you had to work with a difficult team member.",
                "difficulty": "all",
                "tags": ["teamwork", "communication"]
            }
        ]
    }

def extract_technologies(resume_text: str) -> Dict[str, List[str]]:
    """Extract technologies and skills from resume text."""
    if not resume_text:
        return {}
    
    # Define technology categories and keywords
    tech_categories = {
        'programming_languages': {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 
            'swift', 'kotlin', 'ruby', 'php', 'r', 'matlab', 'scala', 'perl'
        },
        'frameworks': {
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 
            'ruby on rails', 'tensorflow', 'pytorch', 'scikit-learn', 'hadoop', 'spark'
        },
        'databases': {
            'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle', 
            'microsoft sql server', 'dynamodb', 'firebase', 'elasticsearch'
        },
        'cloud_platforms': {
            'aws', 'amazon web services', 'azure', 'google cloud', 'gcp', 
            'docker', 'kubernetes', 'terraform', 'ansible'
        },
        'data_science': {
            'machine learning', 'deep learning', 'data analysis', 'data visualization',
            'natural language processing', 'nlp', 'computer vision', 'reinforcement learning'
        }
    }
    
    # Convert resume to lowercase for case-insensitive matching
    text_lower = resume_text.lower()
    
    # Find matching technologies in each category
    technologies = {}
    for category, tech_set in tech_categories.items():
        found = [tech for tech in tech_set if re.search(r'\b' + re.escape(tech) + r'\b', text_lower)]
        if found:
            technologies[category] = found
    
    return technologies

def generate_questions(
    resume_text: str,
    num_questions: int = 10,
    difficulty: str = "all",
    categories: Optional[List[str]] = None
) -> List[InterviewQuestion]:
    """
    Generate interview questions based on the resume content.
    
    Args:
        resume_text: Text content of the resume
        num_questions: Number of questions to generate
        difficulty: Filter by difficulty level ('beginner', 'intermediate', 'advanced', 'all')
        categories: List of categories to include (e.g., ['programming', 'algorithms', 'system_design'])
        
    Returns:
        List of InterviewQuestion objects
    """
    if not resume_text or not isinstance(resume_text, str):
        logger.warning("Invalid resume text provided")
        return []
    
    # Load question bank
    question_bank = load_question_bank()
    
    # Extract technologies from resume
    technologies = extract_technologies(resume_text)
    logger.info(f"Extracted technologies: {technologies}")
    
    # Collect relevant questions based on technologies
    relevant_questions = []
    
    # 1. Add questions for specific programming languages
    for lang in technologies.get('programming_languages', []):
        if lang in question_bank.get('programming_languages', {}):
            relevant_questions.extend([
                InterviewQuestion(
                    question=q["question"],
                    category=f"{lang.capitalize()} Programming",
                    difficulty=q.get("difficulty", "intermediate"),
                    tags=q.get("tags", []),
                    answer_guidance=q.get("answer_guidance"),
                    follow_up_questions=q.get("follow_up_questions")
                )
                for q in question_bank['programming_languages'][lang]
            ])
    
    # 2. Add data science questions if relevant
    if 'data_science' in technologies or any('data' in cat.lower() for cat in technologies.values()):
        for topic, questions in question_bank.get('data_science', {}).items():
            relevant_questions.extend([
                InterviewQuestion(
                    question=q["question"],
                    category=f"Data Science - {topic.replace('_', ' ').title()}",
                    difficulty=q.get("difficulty", "intermediate"),
                    tags=q.get("tags", []),
                    answer_guidance=q.get("answer_guidance")
                )
                for q in questions
            ])
    
    # 3. Add system design questions for senior roles
    experience_match = re.search(r'(\d+\+?\s*(years?|yrs?)\.?\s+.*?experience)', resume_text, re.IGNORECASE)
    senior_keywords = {'senior', 'lead', 'principal', 'architect', 'manager', 'director', 'head of'}
    has_senior_role = any(keyword in resume_text.lower() for keyword in senior_keywords)
    
    if has_senior_role or (experience_match and int(re.search(r'\d+', experience_match.group(1)).group()) >= 3):
        relevant_questions.extend([
            InterviewQuestion(
                question=q["question"],
                category="System Design",
                difficulty=q.get("difficulty", "advanced"),
                tags=q.get("tags", []),
                follow_up_questions=q.get("follow_up_questions")
            )
            for q in question_bank.get('system_design', [])
        ])
    
    # 4. Add algorithm questions for software engineering roles
    relevant_questions.extend([
        InterviewQuestion(
            question=q["question"],
            category="Algorithms",
            difficulty=q.get("difficulty", "intermediate"),
            tags=q.get("tags", [])
        )
        for q in question_bank.get('algorithms', [])
    ])
    
    # 5. Always include some behavioral questions
    relevant_questions.extend([
        InterviewQuestion(
            question=q["question"],
            category="Behavioral",
            difficulty=q.get("difficulty", "all"),
            tags=q.get("tags", [])
        )
        for q in question_bank.get('behavioral', [])
    ])
    
    # Filter by difficulty if specified
    if difficulty.lower() != 'all':
        relevant_questions = [q for q in relevant_questions 
                            if q.difficulty.lower() == difficulty.lower() or q.difficulty.lower() == 'all']
    
    # Filter by categories if specified
    if categories:
        categories_lower = [c.lower() for c in categories]
        relevant_questions = [
            q for q in relevant_questions
            if any(cat in q.category.lower() for cat in categories_lower) or
            any(tag in categories_lower for tag in q.tags)
        ]
    
    # Shuffle and limit the number of questions
    random.shuffle(relevant_questions)
    
    return relevant_questions[:num_questions]

def get_question_categories() -> List[str]:
    """Get a list of available question categories."""
    question_bank = load_question_bank()
    categories = set()
    
    # Add programming languages
    categories.update([f"{lang.capitalize()} Programming" for lang in question_bank.get('programming_languages', {})])
    
    # Add data science topics
    categories.update([f"Data Science - {topic.replace('_', ' ').title()}" 
                      for topic in question_bank.get('data_science', {})])
    
    # Add other main categories
    categories.update(["System Design", "Algorithms", "Behavioral"])
    
    return sorted(list(categories))

def get_questions_by_category(category: str, difficulty: str = "all") -> List[InterviewQuestion]:
    """
    Get questions filtered by category and optionally by difficulty.
    
    Args:
        category: The category of questions to retrieve
        difficulty: Filter by difficulty level ('beginner', 'intermediate', 'advanced', 'all')
        
    Returns:
        List of InterviewQuestion objects
    """
    question_bank = load_question_bank()
    questions = []
    
    # Check programming languages
    if category.lower() in [lang.lower() for lang in question_bank.get('programming_languages', {})]:
        lang = next((k for k in question_bank['programming_languages'] 
                    if k.lower() == category.lower()), None)
        if lang:
            questions.extend([
                InterviewQuestion(
                    question=q["question"],
                    category=f"{lang.capitalize()} Programming",
                    difficulty=q.get("difficulty", "intermediate"),
                    tags=q.get("tags", []),
                    answer_guidance=q.get("answer_guidance")
                )
                for q in question_bank['programming_languages'][lang]
            ])
    
    # Check data science categories
    elif category.lower().startswith("data science"):
        topic = category.lower().replace("data science", "").strip().replace(" ", "_")
        if topic in question_bank.get('data_science', {}):
            questions.extend([
                InterviewQuestion(
                    question=q["question"],
                    category=f"Data Science - {topic.replace('_', ' ').title()}",
                    difficulty=q.get("difficulty", "intermediate"),
                    tags=q.get("tags", [])
                )
                for q in question_bank['data_science'][topic]
            ])
    
    # Check other main categories
    elif category.lower() == "system design":
        questions.extend([
            InterviewQuestion(
                question=q["question"],
                category="System Design",
                difficulty=q.get("difficulty", "advanced"),
                tags=q.get("tags", [])
            )
            for q in question_bank.get('system_design', [])
        ])
    elif category.lower() == "algorithms":
        questions.extend([
            InterviewQuestion(
                question=q["question"],
                category="Algorithms",
                difficulty=q.get("difficulty", "intermediate"),
                tags=q.get("tags", [])
            )
            for q in question_bank.get('algorithms', [])
        ])
    elif category.lower() == "behavioral":
        questions.extend([
            InterviewQuestion(
                question=q["question"],
                category="Behavioral",
                difficulty=q.get("difficulty", "all"),
                tags=q.get("tags", [])
            )
            for q in question_bank.get('behavioral', [])
        ])
    
    # Filter by difficulty if specified
    if difficulty.lower() != 'all':
        questions = [q for q in questions 
                    if q.difficulty.lower() == difficulty.lower() or q.difficulty.lower() == 'all']
    
    return questions
