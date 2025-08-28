import re
import logging
from typing import List, Dict, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CareerSuggestion:
    """
    Data class for career suggestions with detailed matching information.
    
    Attributes:
        title: Job title
        match_score: Match score (0-100)
        required_skills: List of required skills for this career
        matching_skills: Skills from the resume that match required skills
        missing_skills: Required skills missing from the resume
        description: Career description
        salary_range: [min, max] salary range in USD
        growth_outlook: Job market growth outlook
        education: Recommended education paths
        certifications: Recommended certifications
        preferred_skills: List of preferred skills for this career
        matching_preferred_skills: Preferred skills from the resume
        missing_preferred_skills: Preferred skills missing from the resume
        job_market_demand: Current job market demand (High/Medium/Low)
        experience_levels: Dictionary of experience levels and their descriptions
        current_experience_level: User's current experience level
    """
    title: str
    match_score: float  # 0-100
    required_skills: List[str]
    matching_skills: List[str]
    missing_skills: List[str]
    description: str = ""
    salary_range: Optional[List[int]] = None
    growth_outlook: str = ""
    education: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    matching_preferred_skills: List[str] = field(default_factory=list)
    missing_preferred_skills: List[str] = field(default_factory=list)
    job_market_demand: str = "Medium"
    experience_levels: Dict[str, str] = field(default_factory=dict)
    current_experience_level: str = "entry"

def load_career_data() -> Dict[str, Dict]:
    """Load career data from a JSON file or return default data."""
    try:
        # Try to load from a data file if it exists
        data_file = Path(__file__).parent.parent / 'data' / 'career_paths.json'
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load career data: {str(e)}. Using default data.")
    
    # Default career data if file loading fails
    return {
        "data_scientist": {
            "title": "Data Scientist",
            "required_skills": ["python", "machine learning", "statistics", "data analysis", "sql", "pandas", "numpy", "data visualization"],
            "preferred_skills": ["deep learning", "tensorflow", "pytorch", "scikit-learn", "big data", "cloud computing"],
            "description": "Analyze and interpret complex data to help organizations make better decisions using statistical and machine learning techniques.",
            "salary_range": [95000, 165000],
            "growth_outlook": "Much faster than average (31% growth projected)",
            "education": ["Master's in Data Science", "PhD in related field"],
            "certifications": ["AWS Certified Data Analytics", "Google Data Analytics", "Microsoft Certified: Azure Data Scientist"],
            "experience_levels": {
                "entry": "0-2 years, focusing on data analysis and basic ML models",
                "mid": "3-5 years, with experience in production ML systems",
                "senior": "5+ years, leading data science initiatives"
            },
            "job_market_demand": "High demand across industries, especially in tech, finance, and healthcare"
        },
        "ml_engineer": {
            "title": "Machine Learning Engineer",
            "required_skills": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "software engineering", "mlops"],
            "preferred_skills": ["kubernetes", "docker", "aws/azure/gcp", "data pipelines", "model deployment"],
            "description": "Design, build, and deploy machine learning models and systems at scale, focusing on production-grade ML solutions.",
            "salary_range": [110000, 200000],
            "growth_outlook": "Much faster than average (22% growth projected)",
            "education": ["Master's in Computer Science", "PhD in ML/AI"],
            "certifications": ["Google Professional ML Engineer", "AWS Certified ML Specialty"],
            "experience_levels": {
                "entry": "0-2 years, focusing on ML model development",
                "mid": "3-5 years, with experience in production ML systems",
                "senior": "5+ years, leading ML architecture and strategy"
            },
            "job_market_demand": "Extremely high demand across all tech sectors"
        },
        "data_engineer": {
            "title": "Data Engineer",
            "required_skills": ["sql", "python", "etl", "data warehousing", "big data", "apache spark"],
            "preferred_skills": ["aws/azure/gcp", "airflow", "kafka", "hadoop", "data modeling"],
            "description": "Design, build, and maintain data pipelines and infrastructure for large-scale data processing and analytics.",
            "salary_range": [95000, 170000],
            "growth_outlook": "Much faster than average (25% growth projected)",
            "education": ["Bachelor's in Computer Science", "Data Engineering"],
            "certifications": ["Google Cloud Professional Data Engineer", "AWS Certified Data Analytics"],
            "experience_levels": {
                "entry": "0-2 years, focusing on ETL and data pipelines",
                "mid": "3-5 years, with experience in distributed systems",
                "senior": "5+ years, leading data architecture"
            },
            "job_market_demand": "Very high demand, especially in data-driven companies"
        },
        "devops_engineer": {
            "title": "DevOps Engineer",
            "required_skills": ["aws/azure/gcp", "docker", "kubernetes", "ci/cd", "linux", "infrastructure as code"],
            "preferred_skills": ["terraform", "ansible", "prometheus", "grafana", "gitops"],
            "description": "Bridge the gap between development and operations by automating infrastructure and deployment processes.",
            "salary_range": [100000, 180000],
            "growth_outlook": "Faster than average (21% growth projected)",
            "education": ["Bachelor's in Computer Science", "Software Engineering"],
            "certifications": ["AWS Certified DevOps Engineer", "Docker Certified Associate", "CKA (Certified Kubernetes Administrator)"],
            "experience_levels": {
                "entry": "0-2 years, focusing on CI/CD and basic infrastructure",
                "mid": "3-5 years, with experience in cloud platforms",
                "senior": "5+ years, leading DevOps strategy and architecture"
            },
            "job_market_demand": "Very high demand across all industries"
        },
        "cloud_architect": {
            "title": "Cloud Solutions Architect",
            "required_skills": ["aws/azure/gcp", "cloud architecture", "networking", "security", "infrastructure as code"],
            "preferred_skills": ["kubernetes", "serverless", "microservices", "devops", "cost optimization"],
            "description": "Design and implement secure, scalable cloud infrastructure and solutions for organizations.",
            "salary_range": [120000, 220000],
            "growth_outlook": "Much faster than average (24% growth projected)",
            "education": ["Bachelor's in Computer Science", "Cloud Computing"],
            "certifications": ["AWS Solutions Architect Professional", "Google Cloud Professional Cloud Architect", "Azure Solutions Architect Expert"],
            "experience_levels": {
                "mid": "3-5 years in cloud technologies",
                "senior": "5+ years, with architecture experience"
            },
            "job_market_demand": "High demand, especially in enterprise environments"
        },
        "cybersecurity_analyst": {
            "title": "Cybersecurity Analyst",
            "required_skills": ["security", "networking", "linux", "python", "incident response", "vulnerability assessment"],
            "preferred_skills": ["siem", "ids/ips", "penetration testing", "threat intelligence", "cloud security"],
            "description": "Protect systems and networks from cyber threats through monitoring, analysis, and incident response.",
            "salary_range": [90000, 160000],
            "growth_outlook": "Much faster than average (33% growth projected)",
            "education": ["Cybersecurity", "Computer Science"],
            "certifications": ["CISSP", "CEH", "CompTIA Security+", "CySA+"],
            "experience_levels": {
                "entry": "0-2 years in IT or security",
                "mid": "3-5 years in security operations",
                "senior": "5+ years, leading security initiatives"
            },
            "job_market_demand": "Extremely high demand across all sectors"
        },
        "ai_research_scientist": {
            "title": "AI Research Scientist",
            "required_skills": ["machine learning", "deep learning", "research", "python", "pytorch/tensorflow"],
            "preferred_skills": ["reinforcement learning", "nlp", "computer vision", "publications", "mathematics"],
            "description": "Conduct cutting-edge research in artificial intelligence and develop novel algorithms.",
            "salary_range": [120000, 220000],
            "growth_outlook": "Much faster than average (22% growth projected)",
            "education": ["PhD in Computer Science", "AI/ML"],
            "certifications": ["Deep Learning Specialization", "Advanced AI Certification"],
            "experience_levels": {
                "phd": "PhD with research experience",
                "research_scientist": "2+ years in AI research",
                "senior": "5+ years with significant publications"
            },
            "job_market_demand": "High demand in research labs and tech companies"
        },
        "data_analyst": {
            "title": "Data Analyst",
            "required_skills": ["sql", "excel", "data visualization", "statistics", "python/r"],
            "preferred_skills": ["tableau", "power bi", "google analytics", "a/b testing"],
            "description": "Interpret data and turn it into actionable business insights through analysis and visualization.",
            "salary_range": [65000, 120000],
            "growth_outlook": "Much faster than average (25% growth projected)",
            "education": ["Mathematics", "Statistics", "Business Analytics"],
            "certifications": ["Google Data Analytics Certificate", "Microsoft Certified: Data Analyst Associate"],
            "experience_levels": {
                "entry": "0-2 years in data analysis",
                "mid": "3-5 years with business domain expertise",
                "senior": "5+ years leading analytics initiatives"
            },
            "job_market_demand": "High demand across all industries"
        }
    }

def extract_skills(resume_text: str) -> Set[str]:
    """Extract skills from resume text using pattern matching."""
    if not resume_text:
        return set()
    
    # Common technical skills to look for
    technical_skills = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin',
        'ruby', 'php', 'r', 'matlab', 'scala', 'perl', 'haskell', 'dart', 'elixir', 'clojure',
        
        # Web Development
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
        'laravel', 'ruby on rails', 'asp.net', 'graphql', 'rest api', 'websockets',
        
        # Mobile Development
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'swiftui', 'kotlin multiplatform',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'data analysis', 'data visualization', 'pandas',
        'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'opencv', 'nltk', 'spacy', 'hadoop',
        'spark', 'hive', 'kafka', 'tableau', 'power bi', 'apache beam', 'apache flink',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
        'github actions', 'gitlab ci', 'circleci', 'prometheus', 'grafana', 'istio', 'helm',
        'linux', 'bash', 'shell scripting', 'infrastructure as code', 'serverless', 'lambda',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'firebase',
        'oracle', 'microsoft sql server', 'neo4j', 'elasticsearch', 'snowflake', 'bigquery',
        
        # Other Technologies
        'blockchain', 'ethereum', 'solidity', 'web3', 'iot', 'raspberry pi', 'arduino',
        'computer vision', 'nlp', 'reinforcement learning', 'quantum computing', 'robotics',
        
        # Soft Skills
        'leadership', 'teamwork', 'problem solving', 'communication', 'project management',
        'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'test driven development'
    }
    
    # Convert resume to lowercase for case-insensitive matching
    text_lower = resume_text.lower()
    
    # Find all matching skills
    found_skills = {skill for skill in technical_skills if re.search(r'\b' + re.escape(skill) + r'\b', text_lower)}
    
    # Add any skills mentioned in the experience section
    experience_section = re.search(r'(?i)(experience|work history)[^\n]*(\n\s*\-.*?)(?=\n\s*\n|\Z)', 
                                 resume_text, re.DOTALL)
    if experience_section:
        exp_text = experience_section.group(0).lower()
        found_skills.update(skill for skill in technical_skills if skill in exp_text)
    
    return found_skills

def calculate_match_score(resume_skills: Set[str], career_data: Dict) -> Tuple[float, Dict[str, List[str]], Dict[str, float]]:
    """
    Calculate match score between resume skills and career requirements.
    
    Args:
        resume_skills: Set of skills from the resume
        career_data: Dictionary containing career information including required_skills and preferred_skills
        
    Returns:
        Tuple of (match_score, skill_analysis, skill_relevance)
    """
    required_skills = career_data.get('required_skills', [])
    preferred_skills = career_data.get('preferred_skills', [])
    
    if not required_skills:
        return 0.0, {"matching": [], "missing": [], "preferred": []}, {}
    
    # Convert to lowercase for case-insensitive comparison
    resume_skills_lower = {s.lower() for s in resume_skills}
    required_skills_lower = [s.lower() for s in required_skills]
    preferred_skills_lower = [s.lower() for s in preferred_skills]
    
    # Find matching, missing, and preferred skills
    matching_required = [s for s in required_skills_lower if s in resume_skills_lower]
    matching_preferred = [s for s in preferred_skills_lower if s in resume_skills_lower]
    
    missing_required = [s for s in required_skills_lower if s not in resume_skills_lower]
    missing_preferred = [s for s in preferred_skills_lower if s not in resume_skills_lower]
    
    # Calculate base match score based on required skills (60% weight)
    required_match = len(matching_required) / len(required_skills_lower) if required_skills_lower else 0
    
    # Calculate preferred skills bonus (30% weight)
    preferred_bonus = (len(matching_preferred) / len(preferred_skills_lower) * 0.5) if preferred_skills_lower else 0
    
    # Calculate skill relevance scores
    skill_relevance = {}
    for i, skill in enumerate(required_skills_lower):
        # Earlier skills in the list are more important
        relevance = 1.0 - (i * 0.05)  # 5% reduction for each position
        skill_relevance[skill] = relevance
    
    # Calculate weighted score based on skill relevance
    weighted_score = 0.0
    total_relevance = sum(skill_relevance.values())
    
    for skill in matching_required:
        weighted_score += skill_relevance.get(skill, 0.5)
    
    weighted_match = (weighted_score / total_relevance) if total_relevance > 0 else 0
    
    # Calculate final score (60% required, 30% preferred, 10% experience level)
    final_score = (weighted_match * 0.6) + (preferred_bonus * 0.3)
    
    # Cap at 100%
    final_score = min(1.0, final_score)
    
    return final_score, {
        "matching": matching_required,
        "missing": missing_required,
        "preferred": matching_preferred,
        "missing_preferred": missing_preferred
    }, skill_relevance

def calculate_skill_relevance(skill: str, career_skills: List[str]) -> float:
    """Calculate the relevance of a skill to a career based on its position in the required skills list."""
    try:
        # Skills earlier in the list are considered more important
        position = career_skills.index(skill.lower())
        return 1.0 - (position * 0.1)  # 10% reduction for each position
    except ValueError:
        return 0.5  # Default relevance for skills not in the required list

def analyze_experience_level(resume_text: str) -> str:
    """
    Analyze the resume text to determine the experience level.
    
    Args:
        resume_text: The text content of the resume
        
    Returns:
        Experience level: 'entry', 'mid', 'senior', or 'executive'
    """
    if not resume_text:
        return "entry"
    
    # Look for experience indicators
    text_lower = resume_text.lower()
    
    # Check for years of experience
    years_exp = 0
    years_match = re.search(r'(\d+)\s*(?:year|yr)s?\s+(?:of\s+)?experience', text_lower)
    if years_match:
        years_exp = int(years_match.group(1))
    
    # Check for senior/lead/manager roles
    has_leadership = any(term in text_lower for term in [
        'senior', 'lead', 'manager', 'director', 'vp', 'cto', 'cio', 'architect',
        'principal', 'head of', 'team lead', 'tech lead'
    ])
    
    # Determine experience level
    if years_exp >= 10 or has_leadership and years_exp >= 5:
        return "senior"
    elif years_exp >= 5 or has_leadership:
        return "mid"
    elif years_exp >= 2:
        return "mid"
    return "entry"

def format_career_suggestion(suggestion: CareerSuggestion) -> Dict[str, any]:
    """Format a career suggestion for UI display."""
    return {
        "title": suggestion.title,
        "match_score": round(suggestion.match_score, 1),
        "description": suggestion.description,
        "salary_range": {
            "min": suggestion.salary_range[0] if suggestion.salary_range else None,
            "max": suggestion.salary_range[1] if suggestion.salary_range else None,
            "formatted": f"${suggestion.salary_range[0]:,}-${suggestion.salary_range[1]:,}" 
                        if suggestion.salary_range and len(suggestion.salary_range) == 2 
                        else "Not specified"
        },
        "growth_outlook": suggestion.growth_outlook,
        "job_market_demand": getattr(suggestion, 'job_market_demand', 'Medium'),
        "skills": {
            "matching": [{"name": skill, "relevance": rel} for skill, rel in suggestion.matching_skills],
            "missing": suggestion.missing_skills,
            "matching_preferred": getattr(suggestion, 'matching_preferred_skills', []),
            "missing_preferred": getattr(suggestion, 'missing_preferred_skills', [])
        },
        "education": suggestion.education,
        "certifications": suggestion.certifications,
        "experience_levels": getattr(suggestion, 'experience_levels', {}),
        "current_experience_level": getattr(suggestion, 'current_experience_level', 'entry')
    }

def suggest_career_paths(
    resume_text: str,
    top_n: int = 5,
    min_match_threshold: float = 0.2,
    min_required_skills: int = 2,
    experience_level: Optional[str] = None,
    career_interests: Optional[List[str]] = None
) -> List[Dict[str, any]]:
    """
    Suggest career paths based on skills found in the resume with enhanced matching.
    
    Args:
        resume_text: The text content of the resume
        top_n: Number of top career suggestions to return
        min_match_threshold: Minimum match score (0-1) to include a career suggestion
        min_required_skills: Minimum number of matching skills to consider a career
        experience_level: Optional experience level ('entry', 'mid', 'senior', 'executive').
                         If not provided, it will be determined from the resume.
        career_interests: Optional list of career domains of interest (e.g., ['data', 'cloud', 'ai'])
                         
    Returns:
        List of formatted career suggestions, sorted by match score (descending)
    """
    if not resume_text or not isinstance(resume_text, str):
        logger.warning("Invalid resume text provided")
        return []
    
    # Determine experience level if not provided
    if experience_level is None:
        experience_level = analyze_experience_level(resume_text)
    
    # Extract skills from resume (case-insensitive and deduplicated)
    resume_skills = list({skill.lower() for skill in extract_skills(resume_text)})
    logger.info(f"Extracted {len(resume_skills)} unique skills from resume")
    
    if not resume_skills:
        return [{
            "title": "General IT Professional",
            "match_score": 0.0,
            "description": "Consider adding more technical skills to your resume for better career matching.",
            "salary_range": {"min": None, "max": None, "formatted": "Not specified"},
            "growth_outlook": "Average (5-7% growth projected)",
            "job_market_demand": "Medium",
            "skills": {"matching": [], "missing": [], "matching_preferred": [], "missing_preferred": []},
            "education": [],
            "certifications": [],
            "experience_levels": {},
            "current_experience_level": experience_level
        }]
    
    # Load career data
    career_data = load_career_data()
    
    suggestions = []
    for career_id, career_info in career_data.items():
        # Skip if career doesn't match user's interests (if specified)
        if career_interests and not any(
            interest.lower() in career_info['title'].lower() or 
            any(interest.lower() in skill.lower() for skill in career_info['required_skills'])
            for interest in career_interests
        ):
            continue
            
        # Calculate match score and get skill analysis
        match_score, skill_analysis, _ = calculate_match_score(set(resume_skills), career_info)
        
        # Skip if below minimum thresholds
        if (match_score < min_match_threshold or 
            len(skill_analysis.get('matching', [])) < min_required_skills):
            continue
            
        # Adjust score based on experience level
        exp_levels = career_info.get('experience_levels', {})
        if experience_level in exp_levels and experience_level != 'entry':
            match_score = min(match_score * 1.1, 1.0)
        
        # Create career suggestion
        suggestion = CareerSuggestion(
            title=career_info['title'],
            match_score=min(match_score * 100, 100),  # Convert to percentage
            required_skills=career_info.get('required_skills', []),
            matching_skills=skill_analysis.get('matching', []),
            missing_skills=skill_analysis.get('missing', []),
            description=career_info.get('description', ''),
            salary_range=career_info.get('salary_range'),
            growth_outlook=career_info.get('growth_outlook', 'Not specified'),
            education=career_info.get('education', []),
            certifications=career_info.get('certifications', [])
        )
        
        # Add additional metadata
        setattr(suggestion, 'preferred_skills', career_info.get('preferred_skills', []))
        setattr(suggestion, 'matching_preferred_skills', skill_analysis.get('preferred', []))
        setattr(suggestion, 'missing_preferred_skills', skill_analysis.get('missing_preferred', []))
        setattr(suggestion, 'job_market_demand', career_info.get('job_market_demand', 'Medium'))
        setattr(suggestion, 'experience_levels', exp_levels)
        setattr(suggestion, 'current_experience_level', experience_level)
        
        suggestions.append(suggestion)
    
    # Sort by match score (descending) and then by number of matching skills
    suggestions.sort(
        key=lambda x: (
            x.match_score, 
            len(x.matching_skills) + len(getattr(x, 'matching_preferred_skills', [])) * 0.5
        ), 
        reverse=True
    )
    
    # Format suggestions for UI and limit to top N
    return [format_career_suggestion(s) for s in suggestions[:top_n]]

def get_skill_development_plan(resume_text: str, target_role: str) -> Dict[str, Any]:
    """
    Get a comprehensive skill development plan for transitioning to a target role.
    
    Args:
        resume_text: The text content of the resume
        target_role: The target career role
        
    Returns:
        Dictionary with detailed skill development recommendations including:
        - Match score and market readiness
        - Missing skills by priority
        - Learning resources (courses, books, projects)
        - Certification recommendations
        - Career progression path
        - Timeline and next steps
    """
    if not resume_text or not target_role:
        return {"error": "Resume text and target role are required"}
        
    resume_skills = list({skill.lower() for skill in extract_skills(resume_text)})
    career_data = load_career_data()
    
    # Format the response to be UI-friendly
    def format_skill(skill: str) -> Dict[str, str]:
        return {"name": skill, "resource": f"Learn {skill}"}
        
    def format_learning_resource(resource_type: str, items: List[Dict]) -> List[Dict]:
        return [{"type": resource_type, **item} for item in items]
    
    # Find the target career
    target_career = None
    for career_info in career_data.values():
        if career_info['title'].lower() == target_role.lower():
            target_career = career_info
            break
    
    if not target_career:
        return {"error": f"Target role '{target_role}' not found in career database"}
    
    # Get detailed skill analysis
    match_score, skill_analysis, skill_relevance = calculate_match_score(
        resume_skills, target_career
    )
    
    # Get experience level
    experience_level = analyze_experience_level(resume_text)
    
    # Categorize missing skills by priority (based on relevance)
    missing_skills_ranked = sorted(
        skill_analysis['missing'],
        key=lambda x: skill_relevance.get(x, 0.5),
        reverse=True
    )
    
    # Split into priority levels
    high_priority = missing_skills_ranked[:3]  # Top 3 most relevant missing skills
    medium_priority = missing_skills_ranked[3:6]
    low_priority = missing_skills_ranked[6:]
    
    # Calculate market readiness score (0-100)
    base_score = match_score * 80  # Max 80% from skill match
    preferred_bonus = len(skill_analysis.get('preferred', [])) * 2  # Up to 20% bonus
    market_readiness = min(100, base_score + preferred_bonus)
    
    # Get recommended learning resources with more specific suggestions
    learning_resources = {
        "online_courses": [
            {
                "skill": skill,
                "courses": [
                    f"{skill} Specialization on Coursera",
                    f"Udacity Nanodegree in {target_role} (covers {skill})",
                    f"edX Professional Certificate in {skill}"
                ][:2]  # Keep top 2 course recommendations
            } for skill in high_priority
        ] if high_priority else [],
        "books": [
            {
                "skill": skill,
                "books": [
                    f"Best Practices in {skill}",
                    f"Mastering {skill} for {target_role}s"
                ]
            } for skill in medium_priority[:2]  # Top 2 medium priority skills
        ] if medium_priority else [],
        "projects": [
            {
                "skill": skill,
                "project_ideas": [
                    f"Build a {skill} portfolio project",
                    f"Contribute to open-source projects using {skill}",
                    f"Create a tutorial on {skill}"
                ]
            } for skill in (high_priority + medium_priority[:1])  # All high + 1 medium
        ] if high_priority or medium_priority else [],
        "certifications": target_career.get('certifications', [])[:2],  # Top 2 certs
        "communities": [
            f"Join the {target_role} subreddit",
            f"Attend local {target_role} meetups",
            f"Participate in {target_role} Discord communities"
        ]
    }
    
    # Create a timeline based on experience level and skill gap
    skill_gap = len(missing_skills_ranked)
    if experience_level == 'entry':
        timeline = "6-12 months" if skill_gap > 3 else "3-6 months"
    elif experience_level == 'mid':
        timeline = "3-6 months" if skill_gap > 3 else "1-3 months"
    else:  # senior+
        timeline = "1-3 months" if skill_gap > 3 else "1 month or less"
    
    # Generate next steps based on priority
    next_steps = []
    if high_priority:
        next_steps.append(f"Focus on mastering {high_priority[0]} first")
    if high_priority or medium_priority:
        next_steps.append(f"Work on a project using {', '.join(high_priority[:2])}")
    if target_career.get('certifications'):
        next_steps.append(f"Consider getting certified in {target_career['certifications'][0]}")
    
    # Add experience-specific recommendations
    if experience_level == 'entry':
        next_steps.append("Build a portfolio of projects to demonstrate your skills")
    elif experience_level == 'mid':
        next_steps.append("Seek mentorship opportunities to accelerate your growth")
    else:  # senior+
        next_steps.append("Consider mentoring others to solidify your expertise")
    
    return {
        "target_role": target_role,
        "match_analysis": {
            "match_score": round(match_score * 100, 1),
            "market_readiness": round(market_readiness, 1),
            "experience_level": experience_level,
            "job_market_demand": target_career.get('job_market_demand', 'Medium')
        },
        "missing_skills": {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "preferred_skills": skill_analysis.get('missing_preferred', [])[:3]
        },
        "strengths": {
            "matching_skills": skill_analysis.get('matching', []),
            "matching_preferred_skills": skill_analysis.get('preferred', [])
        },
        "learning_resources": learning_resources,
        "career_progression": [
            f"{level}: {desc}" 
            for level, desc in target_career.get('experience_levels', {}).items()
        ],
        "salary_expectations": {
            "entry_level": target_career.get('salary_range'),
            "next_level": [
                int(target_career.get('salary_range', [0, 0])[1] * 1.2),
                int(target_career.get('salary_range', [0, 0])[1] * 1.5)
            ] if target_career.get('salary_range') else None,
            "growth_outlook": target_career.get('growth_outlook', 'Not specified')
        },
        "timeline_suggestion": f"{timeline} to gain necessary skills for {target_role} role",
        "next_steps": next_steps
    }
