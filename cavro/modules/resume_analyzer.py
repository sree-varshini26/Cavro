"""
Resume Analyzer Module

This module provides functionality to extract structured information from resume text,
including contact details, skills, experience, and education.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Common patterns for extracting information
EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_PATTERN = r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
LINKEDIN_PATTERN = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?'
GITHUB_PATTERN = r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9-]+\/?'

# Common section headers
SECTION_HEADERS = [
    'experience', 'work history', 'employment history', 'professional experience',
    'education', 'academic background', 'academic qualifications',
    'skills', 'technical skills', 'professional skills', 'key skills',
    'projects', 'personal projects', 'academic projects',
    'certifications', 'licenses', 'awards', 'honors',
    'publications', 'languages', 'interests'
]

@dataclass
class ContactInfo:
    """Structured contact information extracted from a resume."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert contact info to dictionary."""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'linkedin': self.linkedin,
            'github': self.github,
            'portfolio': self.portfolio
        }

@dataclass
class Experience:
    """Structured work experience information."""
    title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False

@dataclass
class Education:
    """Structured education information."""
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[float] = None
    description: Optional[str] = None

@dataclass
class ResumeData:
    """Structured resume data container."""
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    summary: Optional[str] = None
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resume data to dictionary."""
        return {
            'contact_info': self.contact_info.to_dict(),
            'summary': self.summary,
            'experiences': [{
                'title': exp.title,
                'company': exp.company,
                'location': exp.location,
                'start_date': exp.start_date,
                'end_date': exp.end_date,
                'description': exp.description,
                'is_current': exp.is_current
            } for exp in self.experiences],
            'education': [{
                'degree': edu.degree,
                'institution': edu.institution,
                'field_of_study': edu.field_of_study,
                'start_date': edu.start_date,
                'end_date': edu.end_date,
                'gpa': edu.gpa,
                'description': edu.description
            } for edu in self.education],
            'skills': self.skills,
            'certifications': self.certifications,
            'languages': self.languages,
            'projects': self.projects
        }

def extract_contact_info(text: str) -> Dict[str, str]:
    """
    Extract contact information from resume text.
    
    Args:
        text: Raw resume text
        
    Returns:
        Dictionary containing contact information
    """
    contact_info = {}
    
    # Extract email
    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        contact_info['email'] = email_match.group(0).strip()
    
    # Extract phone number
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        contact_info['phone'] = phone_match.group(0).strip()
    
    # Extract name (simple heuristic: first two words at the start)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines and len(lines[0].split()) >= 2:
        contact_info['name'] = ' '.join(lines[0].split()[:2])
    
    # Extract LinkedIn and GitHub profiles
    linkedin_match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group(0).strip()
    
    github_match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = github_match.group(0).strip()
    
    return contact_info

def extract_skills(text: str) -> List[str]:
    """
    Extract skills from resume text using common skill patterns.
    
    Args:
        text: Raw resume text
        
    Returns:
        List of extracted skills
    """
    # This is a simplified example - in a real application, you'd want a more
    # comprehensive list of skills and better pattern matching
    common_skills = [
        # Programming Languages
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go',
        'TypeScript', 'Rust', 'Scala', 'Perl', 'HTML', 'CSS', 'SQL', 'NoSQL', 'GraphQL',
        # Frameworks
        'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Laravel', 'Ruby on Rails',
        'Node.js', 'Express', 'ASP.NET', 'TensorFlow', 'PyTorch', 'Keras', 'Hadoop', 'Spark',
        # Tools & Platforms
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'Google Cloud', 'Git', 'Jenkins', 'Ansible',
        'Terraform', 'Kafka', 'RabbitMQ', 'Redis', 'MongoDB', 'PostgreSQL', 'MySQL', 'Oracle',
        # Methodologies
        'Agile', 'Scrum', 'Kanban', 'DevOps', 'CI/CD', 'TDD', 'BDD', 'Microservices', 'REST', 'SOAP'
    ]
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    found_skills = []
    
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def extract_education(text: str) -> List[dict]:
    """
    Extract education information from resume text.
    
    Args:
        text: Raw resume text
        
    Returns:
        List of dictionaries containing education information
    """
    try:
        education = []
        
        # Look for education section using common section headers
        education_section = re.search(
            r'(?i)(?:education|academic background|academic qualifications|education & training)(.*?)(?=\n\n|$)', 
            text, 
            re.DOTALL
        )
        
        if education_section:
            # Split into individual education entries
            entries = re.split(r'\n\s*\n', education_section.group(1).strip())
            
            for entry in entries:
                if not entry.strip():
                    continue
                    
                edu = {
                    'degree': '',
                    'institution': '',
                    'field_of_study': '',
                    'start_date': '',
                    'end_date': '',
                    'gpa': None,
                    'description': ''
                }
                
                # Extract degree and institution (most common pattern: "Degree at Institution")
                degree_match = re.search(r'^(.+?)(?:\s+at\s+|,|\n)([^\n]+)', entry, re.IGNORECASE)
                if degree_match:
                    edu['degree'] = degree_match.group(1).strip()
                    edu['institution'] = degree_match.group(2).strip()
                
                # Extract field of study (common patterns)
                field_match = re.search(r'(?:in|major(?:ing)? in|field of study[:\s]+)([^\n,]+)', entry, re.IGNORECASE)
                if field_match:
                    edu['field_of_study'] = field_match.group(1).strip()
                
                # Extract dates (various formats)
                date_match = re.search(
                    r'(?P<start>(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*(?:\d{4}|\d{1,2}(?:st|nd|rd|th)?[\s,]*\d{4})?)(?:\s*(?:-|–|to)\s*)?'
                    r'(?P<end>(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*(?:\d{4}|\d{1,2}(?:st|nd|rd|th)?[\s,]*\d{4})?)|present|current|now)?',
                    entry, 
                    re.IGNORECASE
                )
                
                if date_match:
                    edu['start_date'] = date_match.group('start').strip() if date_match.group('start') else ''
                    edu['end_date'] = date_match.group('end').strip().lower() if date_match.group('end') else ''
                
                # Extract GPA
                gpa_match = re.search(r'\bGPA[:\s]*([0-9]\.[0-9]{1,2})', entry, re.IGNORECASE)
                if gpa_match:
                    try:
                        edu['gpa'] = float(gpa_match.group(1))
                    except (ValueError, TypeError):
                        pass
                
                # Add description if available
                description = entry.strip()
                if degree_match:
                    description = entry[degree_match.end():].strip()
                edu['description'] = '\n'.join(line.strip() for line in description.split('\n') if line.strip())
                
                education.append(edu)
        
        return education
    except Exception as e:
        logger.error(f"Error extracting education: {str(e)}")
        return []

def extract_experience(text: str) -> List[dict]:
    """
    Extract work experience information from resume text.
    
    Args:
        text: Raw resume text
        
    Returns:
        List of dictionaries containing work experience information
    """
    try:
        experience = []
        
        # Look for experience section using common section headers
        exp_section = re.search(
            r'(?i)(?:experience|work experience|professional experience|employment history)(.*?)(?=\n\n|$)', 
            text, 
            re.DOTALL
        )
        
        if exp_section:
            # Split into individual experience entries
            entries = re.split(r'(?=\d{4}|present|current|\n\s*\n)', exp_section.group(1).strip())
            
            for entry in entries:
                if not entry.strip() or len(entry.strip().split()) < 5:  # Skip very short entries
                    continue
                    
                exp = {
                    'title': '',
                    'company': '',
                    'location': '',
                    'start_date': '',
                    'end_date': '',
                    'is_current': False,
                    'description': ''
                }
                
                # Extract dates (various formats)
                date_match = re.search(
                    r'(?P<start>(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*(?:\d{4}|\d{1,2}(?:st|nd|rd|th)?[\s,]*\d{4})?)(?:\s*(?:-|–|to)\s*)?'
                    r'(?P<end>(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*(?:\d{4}|\d{1,2}(?:st|nd|rd|th)?[\s,]*\d{4})?)|present|current|now)?',
                    entry, 
                    re.IGNORECASE
                )
                
                if date_match:
                    exp['start_date'] = date_match.group('start').strip() if date_match.group('start') else ''
                    end_date = date_match.group('end').strip().lower() if date_match.group('end') else ''
                    exp['end_date'] = end_date
                    exp['is_current'] = end_date.lower() in ['present', 'current', 'now']
                
                # Extract title and company (common patterns)
                title_company = re.search(r'^(.*?)(?:\s+at\s+|,|\n)([^\n]+)', entry, re.IGNORECASE)
                if title_company:
                    exp['title'] = title_company.group(1).strip()
                    exp['company'] = title_company.group(2).split('\n')[0].strip()
                
                # Extract location if present
                location_match = re.search(r'\b(?:location|based in|in)[:\s]+([^\n,]+)', entry, re.IGNORECASE)
                if location_match:
                    exp['location'] = location_match.group(1).strip()
                
                # Add description (rest of the entry)
                if title_company:
                    description = entry[title_company.end():].strip()
                else:
                    description = entry.strip()
                
                # Remove date lines from description
                if date_match:
                    description = re.sub(
                        r'(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*(?:\d{4}|\d{1,2}(?:st|nd|rd|th)?[\s,]*\d{4})?\s*(?:-|–|to)\s*'
                        r'(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*(?:\d{4}|\d{1,2}(?:st|nd|rd|th)?[\s,]*\d{4})?|present|current|now)',
                        '', 
                        description
                    ).strip()
                
                exp['description'] = '\n'.join(line.strip() for line in description.split('\n') if line.strip())
                
                experience.append(exp)
        
        return experience
    except Exception as e:
        logger.error(f"Error extracting experience: {str(e)}")
        return []

def analyze_resume(text: str) -> ResumeData:
    """
    Analyze resume text and extract structured information.
    
    Args:
        text: Raw resume text
        
    Returns:
        ResumeData object with extracted information including a comprehensive professional summary
    """
    resume_data = ResumeData()
    
    try:
        # Extract contact information
        contact_info = extract_contact_info(text)
        resume_data.contact_info = ContactInfo(**contact_info)
        
        # Extract skills
        resume_data.skills = extract_skills(text)
        
        # Extract experience
        experience = extract_experience(text)
        resume_data.experiences = [
            Experience(**job) for job in experience[:5]  # Limit to 5 most recent
        ]
        
        # Extract education
        education = extract_education(text)
        resume_data.education = [
            Education(**edu) for edu in education[:3]  # Limit to 3 most recent
        ]
        
        # Generate a comprehensive professional summary
        resume_data.summary = generate_professional_summary(resume_data, experience)
        
        return resume_data
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        # Return partial data if available
        return resume_data

def generate_professional_summary(resume_data: ResumeData, experience: dict) -> str:
    """
    Generate a professional summary based on the extracted resume data.
    
    Args:
        resume_data: The ResumeData object with extracted information
        experience: Dictionary containing experience information
        
    Returns:
        A well-formatted professional summary string
    """
    summary_parts = []
    
    # Add experience summary if available
    if resume_data.experiences:
        latest_job = resume_data.experiences[0]
        exp_summary = (
            f"Experienced {latest_job.title} with {experience.get('total_years', 0)}+ years of experience "
            f"specializing in {latest_job.company if hasattr(latest_job, 'company') else 'the industry'}"
        )
        summary_parts.append(exp_summary)
    
    # Add skills summary if available
    if resume_data.skills:
        # Group skills by category for better presentation
        technical_skills = [s for s in resume_data.skills if any(tech in s.lower() for tech in 
                            ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust'])]
        framework_skills = [s for s in resume_data.skills if any(tech in s.lower() for tech in 
                            ['react', 'angular', 'django', 'flask', 'spring', 'node', 'vue', 'tensorflow', 'pytorch'])]
        
        skills_summary = []
        if technical_skills:
            skills_summary.append(f"proficient in {', '.join(technical_skills[:3])}")
        if framework_skills:
            skills_summary.append(f"experienced with {', '.join(framework_skills[:2])}")
        
        if skills_summary:
            summary_parts.append(' '.join(skills_summary).capitalize())
    
    # Add education summary if available
    if hasattr(resume_data, 'education') and resume_data.education:
        highest_degree = resume_data.education[0]
        if hasattr(highest_degree, 'degree') and hasattr(highest_degree, 'institution'):
            education_summary = f"Holds a {highest_degree.degree} from {highest_degree.institution}"
            summary_parts.append(education_summary)
    
    # Add a closing statement
    if summary_parts:
        summary_parts.append("Seeking opportunities to leverage expertise in a challenging environment.")
    
    # Join all parts with periods and ensure proper capitalization
    summary = '. '.join(summary_parts).strip()
    if summary and not summary.endswith('.'):
        summary += '.'
    
    return summary if summary else "No professional summary available."

# For backward compatibility
extract_contact_info = extract_contact_info
extract_skills = extract_skills
extract_experience = extract_experience
