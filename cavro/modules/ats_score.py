import re
import logging
from typing import Dict, List, Tuple, Set, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json

# Module logger
logger = logging.getLogger(__name__)

class ScoreCategory(Enum):
    KEYWORDS = "keywords"
    ACTION_VERBS = "action_verbs"
    CONTACT_INFO = "contact_info"
    WORK_EXPERIENCE = "work_experience"
    EDUCATION = "education"
    SKILLS = "skills"
    ACHIEVEMENTS = "achievements"
    FORMATTING = "formatting"

@dataclass
class ScoreResult:
    """Container for ATS scoring results and feedback."""
    score: float
    max_score: float
    details: Dict[str, Any]
    feedback: List[str]

class ATSScorer:
    """
    A comprehensive ATS (Applicant Tracking System) scoring system for resumes.
    Evaluates resumes based on various criteria important for ATS parsing.
    """
    
    def __init__(self):
        # Initialize scoring criteria with weights (out of 100)
        self.keyword_weights = {
            ScoreCategory.KEYWORDS: 30,
            ScoreCategory.ACTION_VERBS: 20,
            ScoreCategory.CONTACT_INFO: 10,
            ScoreCategory.WORK_EXPERIENCE: 20,
            ScoreCategory.EDUCATION: 10,
            ScoreCategory.SKILLS: 15,
            ScoreCategory.ACHIEVEMENTS: 15,
            ScoreCategory.FORMATTING: 10
        }
        
        # Common keywords for different categories
        self.common_keywords = {
            'languages': ['python', 'java', 'javascript', 'c++', 'c#', 'swift', 'kotlin', 'go', 'rust', 'typescript'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'node.js', '.net', 'spring', 'tensorflow', 'pytorch'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'dynamodb', 'cassandra'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins'],
            'methodologies': ['agile', 'scrum', 'devops', 'ci/cd', 'tdd', 'bdd', 'microservices', 'rest', 'graphql']
        }
        
        self.action_verbs = [
            'achieved', 'administered', 'analyzed', 'architected', 'built', 'collaborated', 'created',
            'delivered', 'designed', 'developed', 'engineered', 'enhanced', 'established', 'expanded',
            'implemented', 'improved', 'increased', 'initiated', 'innovated', 'integrated', 'introduced',
            'launched', 'led', 'managed', 'optimized', 'orchestrated', 'performed', 'pioneered',
            'produced', 'programmed', 'reduced', 'refactored', 'resolved', 'scaled', 'spearheaded',
            'streamlined', 'transformed'
        ]
        
        self.contact_info_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email'),
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'phone'),
            (r'\b(https?://)?(www\.)?linkedin\.com/[\w-]+\b', 'linkedin'),
            (r'\b(https?://)?(www\.)?github\.com/[\w-]+\b', 'github'),
        ]
        
        # Common degree types and institutions
        self.degree_types = [
            # Use raw strings to avoid invalid escape sequence warnings
            r'bs', r'b\.s\.', r'bachelor', r'ba', r'b\.a\.', r'ms', r'm\.s\.', r'master', r'phd', r'ph\.d\.', 
            r'mba', r'b\.tech', r'btech', r'm\.tech', r'mtech', r'b\.e\.', r'b\.eng', r'm\.e\.', r'm\.eng', r'bca', r'mca'
        ]
        
        # Common section headers
        self.section_headers = [
            'experience', 'work history', 'employment', 'education', 'skills', 'projects',
            'certifications', 'awards', 'publications', 'languages', 'interests'
        ]

    def calculate_score(self, text: str) -> ScoreResult:
        """
        Calculate the ATS score for the given resume text.
        
        Args:
            text: The resume text to score
            
        Returns:
            ScoreResult: Object containing the score and detailed feedback
        """
        if not text or not text.strip():
            return ScoreResult(0, 100, {}, ["Empty resume text provided"])
            
        results = {}
        total_score = 0
        max_score = sum(self.keyword_weights.values())
        feedback = []
        
        # Calculate scores for each category
        results[ScoreCategory.KEYWORDS] = self._score_keywords(text)
        results[ScoreCategory.ACTION_VERBS] = self._score_action_verbs(text)
        results[ScoreCategory.CONTACT_INFO] = self._score_contact_info(text)
        results[ScoreCategory.WORK_EXPERIENCE] = self._score_work_experience(text)
        results[ScoreCategory.EDUCATION] = self._score_education(text)
        results[ScoreCategory.SKILLS] = self._score_skills(text)
        results[ScoreCategory.ACHIEVEMENTS] = self._score_achievements(text)
        results[ScoreCategory.FORMATTING] = self._score_formatting(text)
        
        # Calculate total score
        for category, (score, max_possible, details) in results.items():
            category_weight = self.keyword_weights[category]
            normalized_score = (score / max_possible) * category_weight
            total_score += normalized_score
            
            # Add feedback for areas needing improvement
            if score < max_possible * 0.6:  # If score is less than 60%
                if 'feedback' in details:
                    feedback.append(f"{category.value.replace('_', ' ').title()}: {details['feedback']}")
        
        # Ensure score doesn't exceed 100
        final_score = min(round(total_score, 2), 100)
        
        # Add overall feedback
        if final_score < 50:
            feedback.insert(0, "Your resume needs significant improvement to pass ATS screening.")
        elif final_score < 75:
            feedback.insert(0, "Your resume is decent but could be improved for better ATS performance.")
        else:
            feedback.insert(0, "Great job! Your resume is well-optimized for ATS systems.")
        
        return ScoreResult(
            score=final_score,
            max_score=100,
            details={k.value: {'score': v[0], 'max_score': v[1], **v[2]} for k, v in results.items()},
            feedback=feedback
        )
    
    def _score_keywords(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """Score based on relevant keywords in the resume."""
        found_keywords = {category: [] for category in self.common_keywords}
        total_keywords = sum(len(keywords) for keywords in self.common_keywords.values())
        
        for category, keywords in self.common_keywords.items():
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                    found_keywords[category].append(keyword)
        
        found_count = sum(len(v) for v in found_keywords.values())
        score = (found_count / total_keywords * 100) if total_keywords > 0 else 0
        
        # Generate feedback
        missing_categories = [k for k, v in found_keywords.items() if not v]
        feedback = []
        if missing_categories:
            feedback.append(f"Consider adding keywords related to: {', '.join(missing_categories)}.")
        
        return score, 100, {
            'found_keywords': found_keywords,
            'total_possible': total_keywords,
            'feedback': "; ".join(feedback) if feedback else "Good keyword coverage across multiple categories."
        }
    
    def _score_action_verbs(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """Score based on the use of strong action verbs."""
        found_verbs = []
        
        for verb in self.action_verbs:
            if re.search(rf'\b{re.escape(verb)}\w*\b', text, re.IGNORECASE):
                found_verbs.append(verb)
        
        # Score based on number of unique action verbs found
        unique_verbs = list(set(found_verbs))
        verb_count = len(unique_verbs)
        
        # Max score for 15+ unique verbs
        score = min(verb_count * (100/15), 100)
        
        feedback = []
        if verb_count < 5:
            feedback.append("Use more action verbs to start your bullet points (e.g., 'Developed', 'Led', 'Implemented').")
        
        return score, 100, {
            'found_verbs': unique_verbs,
            'total_verbs': verb_count,
            'feedback': "; ".join(feedback) if feedback else "Good use of action-oriented language."
        }
    
    def _score_contact_info(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """Score based on presence of contact information."""
        found_items = {}
        
        for pattern, item_type in self.contact_info_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Handle different match groups from the regex
                if isinstance(matches[0], tuple):
                    # If the regex has groups, take the first non-empty match
                    match = next((m for m in matches[0] if m), '')
                    found_items[item_type] = match
                else:
                    found_items[item_type] = matches[0]
        
        # Score based on number of contact info items found
        score = (len(found_items) / len(self.contact_info_patterns)) * 100
        
        # Generate feedback
        missing = [t for p, t in self.contact_info_patterns if t not in found_items]
        feedback = []
        if missing:
            feedback.append(f"Missing: {', '.join(missing)}. ")
        
        return score, 100, {
            'found_contact_info': found_items,
            'feedback': feedback[0] + "Ensure your contact info is complete and professional." if feedback 
                       else "All essential contact information is present."
        }
    
    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience details from resume text."""
        # Enhanced date pattern with support for various formats
        date_pattern = r'(?i)(?:(?P<start_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(?P<start_year>\d{4})\s*[–-]\s*(?P<end_month>Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4})?)'
        
        # Expanded job title patterns with more roles and levels
        job_levels = r'(?:(?:Senior|Junior|Lead|Staff|Principal|Associate|Director|VP|CTO|CEO|Founder)\s+)?'
        job_roles = r'(?:Software\s+Engineer|Developer|Data\s+Scientist|ML\s+Engineer|AI\s+Engineer|'
        job_roles += r'Product\s+Manager|Project\s+Manager|Engineering\s+Manager|DevOps\s+Engineer|'
        job_roles += r'QA\s+Engineer|Test\s+Engineer|UI/UX\s+Designer|Full\s+Stack|Back\s+End|Front\s+End|'
        job_roles += r'Cloud\s+Architect|Solutions\s+Architect|Data\s+Engineer|Database\s+Admin|'
        job_roles += r'Security\s+Engineer|Network\s+Engineer|Systems\s+Administrator)'
        
        job_title_pattern = fr'\b{job_levels}{job_roles}\b'
        
        # Company name pattern (simplified)
        company_pattern = r'(?i)(?:(?:at|@|\bat\b)\s*)([A-Z][A-Za-z0-9&.\-\s]+?)(?=\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d|\n|$))'
        
        # Extract work experience sections
        work_experience = []
        current_exp = {}
        
        # Split text into lines and process
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            # Check for date range at start of line
            date_match = re.search(date_pattern, line)
            if date_match:
                if current_exp:  # Save previous experience
                    work_experience.append(current_exp)
                current_exp = {
                    'dates': date_match.group(0),
                    'start_date': f"{date_match.group('start_month')} {date_match.group('start_year')}" if date_match.group('start_month') else None,
                    'end_date': 'Present' if date_match.group('end_month') == 'Present' else 
                               f"{date_match.group('end_month')} {date_match.group('end_year')}" if date_match.group('end_month') and date_match.group('end_month') != 'Present' else None,
                    'title': None,
                    'company': None,
                    'bullet_points': []
                }
            
            # Check for job title
            title_match = re.search(job_title_pattern, line, re.IGNORECASE)
            if title_match and current_exp and not current_exp.get('title'):
                current_exp['title'] = title_match.group(0)
            
            # Check for company name
            company_match = re.search(company_pattern, line)
            if company_match and current_exp and not current_exp.get('company'):
                current_exp['company'] = company_match.group(1).strip()
            
            # Check for bullet points
            bullet_match = re.match(r'^[•\-*]\s+(.+)', line)
            if bullet_match and current_exp:
                point = bullet_match.group(1).strip()
                # Check for metrics and achievements
                metrics = re.findall(r'\b(?:increased|reduced|saved|improved|grew|optimized|decreased|boosted|achieved|delivered)\b.*?\b(?:by|to|from)?\s*\$?\d+(?:\.\d+)?[%kKmMbB]?\b', point, re.IGNORECASE)
                current_exp['bullet_points'].append({
                    'text': point,
                    'has_metrics': bool(metrics),
                    'action_verb': re.match(r'^\w+', point).group(0).lower() if re.match(r'^\w+', point) else None
                })
        
        if current_exp:  # Add the last experience
            work_experience.append(current_exp)
        
        return work_experience

    def _score_work_experience(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """
        Enhanced work experience scoring with detailed analysis.
        
        Scoring Breakdown (100 points total):
        - Position Details: 20 points (titles, companies, dates)
        - Career Progression: 20 points (increasing responsibility)
        - Achievements: 30 points (quantifiable results, action verbs)
        - Technical Depth: 20 points (relevant skills and technologies)
        - Formatting & Readability: 10 points
        """
        work_experience = self._extract_work_experience(text)
        
        if not work_experience:
            return 0, 100, {
                'positions_found': 0,
                'job_titles': [],
                'bullet_points': 0,
                'feedback': "No work experience section found. Include your work history with job titles and dates.",
                'score_breakdown': {
                    'position_details': 0,
                    'career_progression': 0,
                    'achievements': 0,
                    'technical_depth': 0,
                    'formatting': 0
                }
            }
        
        # Initialize scoring
        score_breakdown = {
            'position_details': 0,
            'career_progression': 0,
            'achievements': 0,
            'technical_depth': 0,
            'formatting': 0
        }
        
        # 1. Position Details (20 points)
        position_score = 0
        for exp in work_experience:
            if exp.get('title') and exp.get('company') and exp.get('dates'):
                position_score += 10  # Base points per complete position
        score_breakdown['position_details'] = min(20, position_score)
        
        # 2. Career Progression (20 points)
        if len(work_experience) > 1:
            # Check for increasing responsibility (simplified)
            seniority_keywords = ['junior', 'associate', '', 'senior', 'lead', 'principal', 'manager', 'director', 'vp', 'cto', 'ceo']
            previous_level = -1
            progression_score = 0
            
            for exp in work_experience:
                if not exp.get('title'):
                    continue
                    
                current_level = 0
                title_lower = exp['title'].lower()
                for i, keyword in enumerate(seniority_keywords):
                    if keyword and keyword in title_lower:
                        current_level = i
                        break
                
                if current_level > previous_level:
                    progression_score += 5  # Points for showing growth
                previous_level = current_level
            
            score_breakdown['career_progression'] = min(20, progression_score)
        
        # 3. Achievements (30 points)
        achievement_score = 0
        total_bullet_points = 0
        bullet_points_with_metrics = 0
        action_verbs_used = set()
        
        for exp in work_experience:
            for bullet in exp.get('bullet_points', []):
                total_bullet_points += 1
                if bullet['has_metrics']:
                    bullet_points_with_metrics += 1
                    achievement_score += 3  # 3 points per quantified achievement
                if bullet['action_verb'] and bullet['action_verb'] not in action_verbs_used:
                    action_verbs_used.add(bullet['action_verb'])
                    achievement_score += 1  # 1 point per unique action verb
        
        # Cap achievement score and ensure minimum for having bullet points
        if total_bullet_points >= 3:
            achievement_score = min(30, achievement_score + 5)  # Bonus for having sufficient bullet points
        score_breakdown['achievements'] = min(30, achievement_score)
        
        # 4. Technical Depth (20 points)
        # Check for technical skills in work experience
        technical_terms = 0
        for exp in work_experience:
            for bullet in exp.get('bullet_points', []):
                # Count technical terms (simplified)
                technical_terms += len(re.findall(r'\b(?:API|REST|GraphQL|AWS|Azure|GCP|Docker|Kubernetes|React|Angular|Vue|Python|Java|JavaScript|TypeScript|SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Machine Learning|AI|ML|Data Science|CI/CD|Terraform|Ansible|Git|Agile|Scrum|DevOps|Microservices)\b', 
                                                bullet['text'], re.IGNORECASE))
        
        score_breakdown['technical_depth'] = min(20, technical_terms * 2)  # 2 points per technical term, capped at 20
        
        # 5. Formatting & Readability (10 points)
        formatting_score = 0
        if len(work_experience) > 0:
            # Check for consistent formatting
            has_consistent_dates = all(exp.get('dates') for exp in work_experience)
            has_consistent_titles = all(exp.get('title') for exp in work_experience)
            has_consistent_companies = all(exp.get('company') for exp in work_experience)
            
            if has_consistent_dates and has_consistent_titles and has_consistent_companies:
                formatting_score += 5
            
            # Check for bullet points in each position
            positions_with_bullets = sum(1 for exp in work_experience if exp.get('bullet_points'))
            if positions_with_bullets == len(work_experience):
                formatting_score += 5
        
        score_breakdown['formatting'] = min(10, formatting_score)
        
        # Calculate total score
        total_score = sum(score_breakdown.values())
        
        # Generate feedback
        feedback = []
        
        if score_breakdown['position_details'] < 10:
            feedback.append("Ensure each position includes job title, company name, and dates.")
            
        if score_breakdown['career_progression'] < 10 and len(work_experience) > 1:
            feedback.append("Show career progression with increasing levels of responsibility.")
            
        if score_breakdown['achievements'] < 15:
            feedback.append("Include more quantified achievements with metrics (e.g., 'increased X by Y%').")
            
        if score_breakdown['technical_depth'] < 10:
            feedback.append("Highlight more technical skills and technologies used in each role.")
            
        if score_breakdown['formatting'] < 5:
            feedback.append("Improve formatting consistency across all work experience entries.")
        
        # Prepare results
        job_titles = [exp['title'] for exp in work_experience if exp.get('title')]
        total_bullet_points = sum(len(exp.get('bullet_points', [])) for exp in work_experience)
        
        return total_score, 100, {
            'positions_found': len(work_experience),
            'job_titles': job_titles,
            'bullet_points': total_bullet_points,
            'bullet_points_with_metrics': bullet_points_with_metrics,
            'unique_action_verbs': len(action_verbs_used),
            'technical_terms_found': technical_terms,
            'score_breakdown': score_breakdown,
            'feedback': feedback if feedback else ["Work experience section is well-structured with detailed achievements."]
        }
    
    def _score_education(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """Score based on education section."""
        # Look for degree types, institutions, and graduation years
        degree_pattern = '|'.join(map(re.escape, self.degree_types))
        institution_pattern = r'\b(?:University|College|Institute|School|Univ\.?|Inst\.?|Tech|Polytechnic)\b'
        year_pattern = r'\b(?:19|20)\d{2}\b'
        
        degrees = re.findall(degree_pattern, text, re.IGNORECASE)
        institutions = re.findall(institution_pattern, text, re.IGNORECASE)
        years = re.findall(year_pattern, text)
        
        # Calculate score
        score = 0
        feedback = []
        
        if not degrees and not institutions:
            feedback.append("Education section not found or not clearly formatted.")
        else:
            if degrees:
                score += 40
                if len(degrees) > 1:  # Multiple degrees
                    score += 20
            else:
                feedback.append("List your degree(s) (e.g., 'BS in Computer Science').")
                
            if institutions:
                score += 20
                if len(institutions) > 1:
                    score += 10
            else:
                feedback.append("Include the name of your educational institution(s).")
                
            if years:
                score += 10
            else:
                feedback.append("Add graduation year(s) or expected graduation date.")
        
        # Cap score at 100
        score = min(score, 100)
        
        return score, 100, {
            'degrees': degrees,
            'institutions': institutions,
            'graduation_years': years,
            'feedback': " ".join(feedback) if feedback else "Education section is complete with degree, institution, and dates."
        }
    
    def _score_skills(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """Score based on skills section."""
        # Look for skills section (common section headers)
        skills_section = re.search(
            r'(?i)(?:skills|technical\s+skills|technical\s+expertise|technologies)[:;\s]*(.+?)(?=\n\w|$)', 
            text, 
            re.DOTALL
        )
        
        if skills_section:
            skills_text = skills_section.group(1)
            # Count number of skills (comma/pipe separated or bullet points)
            skills = [s.strip() for s in re.split(r'[,\n\|•]', skills_text) if s.strip()]
            skill_count = len(skills)
            
            # Score based on number of skills (5-15 is ideal)
            if skill_count == 0:
                score = 0
                feedback = "No skills listed in the skills section."
            elif skill_count < 5:
                score = 30 + (skill_count * 5)
                feedback = f"Only {skill_count} skills listed. Aim for 10-15 relevant skills."
            elif skill_count > 20:
                score = 80
                feedback = "Consider focusing on the most relevant 10-15 skills."
            else:
                score = 40 + min(skill_count * 4, 60)  # Cap at 100
                feedback = "Good number of skills listed."
            
            # Check for skills organization
            categories = set()
            for line in skills_text.split('\n'):
                if ':' in line:  # Likely a category header
                    categories.add(line.split(':')[0].strip().lower())
            
            if not categories and skill_count > 5:
                feedback += " Consider grouping skills by category (e.g., 'Languages: Python, Java')."
            
            return score, 100, {
                'skills_found': skills,
                'skill_count': skill_count,
                'categories_found': list(categories),
                'feedback': feedback
            }
        
        # If no dedicated skills section, look for skills throughout the document
        all_skills = []
        for category, keywords in self.common_keywords.items():
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                    all_skills.append(keyword)
        
        if all_skills:
            return 50, 100, {
                'skills_found': all_skills,
                'skill_count': len(all_skills),
                'categories_found': [],
                'feedback': "Skills are mentioned but not in a dedicated section. Add a 'Skills' section for better visibility."
            }
        
        return 20, 100, {
            'skills_found': [],
            'skill_count': 0,
            'categories_found': [],
            'feedback': "No skills section found. Add a 'Skills' section listing your technical and soft skills."
        }
    
    def _score_achievements(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """Score based on achievements and impact statements."""
        # Look for quantifiable achievements
        quantifiers = [
            r'\b(?:increased|reduced|saved|grew|improved|decreased|optimized|boosted|expanded|delivered)\b[^.!?]*\b(?:by\s+)?(\d+%?|\$\d+[KkMm]?|\d+[KkMm]?\$?)\b',
            r'\b(?:award|certification|recognition|honor|prize|scholarship|publication|presentation|patent)\b',
            r'\b(?:led|managed|mentored|trained|supervised)\b[^.!?]*\b(?:team|group|project)\b',
            r'\b(?:presented|published|speaker|talk|workshop|conference)\b'
        ]
        
        achievements = []
        for pattern in quantifiers:
            matches = re.findall(pattern, text, re.IGNORECASE)
            achievements.extend(matches)
        
        # Remove duplicates while preserving order
        unique_achievements = []
        seen = set()
        for ach in achievements:
            if ach.lower() not in seen:
                seen.add(ach.lower())
                unique_achievements.append(ach)
        
        # Calculate score based on number of unique achievements
        achievement_count = len(unique_achievements)
        
        if achievement_count == 0:
            score = 20
            feedback = "No clear achievements or impact statements found. Add quantifiable results (e.g., 'Increased performance by 30%')."
        elif achievement_count == 1:
            score = 50
            feedback = "Found 1 achievement. Add more quantifiable results to strengthen your resume."
        elif achievement_count == 2:
            score = 70
            feedback = "Good start with achievements. Include 1-2 more for greater impact."
        else:
            score = min(90 + (achievement_count * 2), 100)
            feedback = f"Found {achievement_count} achievements. Great job highlighting your impact!"
        
        return score, 100, {
            'achievement_count': achievement_count,
            'achievement_examples': unique_achievements[:5],  # Return first 5 examples
            'feedback': feedback
        }
    
    def _score_formatting(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
        """Score based on resume formatting and structure."""
        score = 50  # Start with a baseline score
        feedback = []
        missing_sections: List[str] = []
        
        # Check for section headers
        section_headers_found = []
        for header in self.section_headers:
            if re.search(rf'\b{re.escape(header)}\b', text, re.IGNORECASE):
                section_headers_found.append(header)
        
        if not section_headers_found:
            feedback.append("No clear section headers found. Use clear section headings like 'Experience', 'Education', etc.")
        else:
            score += 10
            missing_sections = [s for s in ['experience', 'education', 'skills'] 
                              if s not in [h.lower() for h in section_headers_found]]
            if missing_sections:
                feedback.append(f"Consider adding sections for: {', '.join(missing_sections)}.")
        
        # Check length (1-2 pages is ideal)
        line_count = len([line for line in text.split('\n') if line.strip()])
        if line_count < 20:
            score -= 10
            feedback.append("Resume seems too short. Consider adding more details about your experience and skills.")
        elif line_count > 60:  # Rough estimate for 2 pages
            score -= 5
            feedback.append("Resume might be too long. Consider condensing to 1-2 pages.")
        
        # Check for consistent formatting
        bullet_styles = set(re.findall(r'^\s*([•\-*])\s+', text, re.MULTILINE))
        if len(bullet_styles) > 1:
            score -= 5
            feedback.append("Inconsistent bullet point styles. Use the same bullet style throughout.")
        
        # Check for proper spacing
        double_newlines = text.count('\n\n')
        single_newlines = text.count('\n') - (2 * double_newlines)
        if single_newlines > (double_newlines * 2):
            score -= 5
            feedback.append("Inconsistent spacing. Ensure consistent spacing between sections and paragraphs.")
        
        # Check for proper capitalization in section headers
        all_caps_headers = re.findall(r'^[A-Z\s]+$', text, re.MULTILINE)
        if all_caps_headers and len(all_caps_headers) > 3:  # More than 3 all-caps lines
            score -= 5
            feedback.append("Avoid using ALL CAPS for section headers. Use title case instead.")
        
        # Bound score and return structured result
        score = max(0, min(100, score))
        return score, 100, {
            'section_headers_found': section_headers_found,
            'missing_sections': missing_sections,
            'line_count': line_count,
            'bullet_styles': list(bullet_styles),
            'feedback': " ".join(feedback) if feedback else "Good structure and formatting detected."
        }

def _score_skills(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
    """Score based on skills section."""
    # Look for skills section (common section headers)
    skills_section = re.search(
        r'(?i)(?:skills|technical\s+skills|technical\s+expertise|technologies)[:;\s]*(.+?)(?=\n\w|$)', 
        text, 
        re.DOTALL
    )
    
    if skills_section:
        skills_text = skills_section.group(1)
        # Count number of skills (comma/pipe separated or bullet points)
        skills = [s.strip() for s in re.split(r'[,\n\|•]', skills_text) if s.strip()]
        skill_count = len(skills)
        
        # Score based on number of skills (5-15 is ideal)
        if skill_count == 0:
            score = 0
            feedback = "No skills listed in the skills section."
        elif skill_count < 5:
            score = 30 + (skill_count * 5)
            feedback = f"Only {skill_count} skills listed. Aim for 10-15 relevant skills."
        elif skill_count > 20:
            score = 80
            feedback = "Consider focusing on the most relevant 10-15 skills."
        else:
            score = 40 + min(skill_count * 4, 60)  # Cap at 100
            feedback = "Good number of skills listed."
        
        # Check for skills organization
        categories = set()
        for line in skills_text.split('\n'):
            if ':' in line:  # Likely a category header
                categories.add(line.split(':')[0].strip().lower())
        
        if not categories and skill_count > 5:
            feedback += " Consider grouping skills by category (e.g., 'Languages: Python, Java')."
        
        return score, 100, {
            'skills_found': skills,
            'skill_count': skill_count,
            'categories_found': list(categories),
            'feedback': feedback
        }
    
    # If no dedicated skills section, look for skills throughout the document
    all_skills = []
    for category, keywords in self.common_keywords.items():
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                all_skills.append(keyword)
    
    if all_skills:
        return 50, 100, {
            'skills_found': all_skills,
            'skill_count': len(all_skills),
            'categories_found': [],
            'feedback': "Skills are mentioned but not in a dedicated section. Add a 'Skills' section for better visibility."
        }
    
    return 20, 100, {
        'skills_found': [],
        'skill_count': 0,
        'categories_found': [],
        'feedback': "No skills section found. Add a 'Skills' section listing your technical and soft skills."
    }

def _score_achievements(self, text: str) -> Tuple[float, float, Dict[str, Any]]:
    """Score based on achievements and impact statements."""
    # Look for quantifiable achievements
    quantifiers = [
        r'\b(?:increased|reduced|saved|grew|improved|decreased|optimized|boosted|expanded|delivered)\b[^.!?]*\b(?:by\s+)?(\d+%?|\$\d+[KkMm]?|\d+[KkMm]?\$?)\b',
        r'\b(?:award|certification|recognition|honor|prize|scholarship|publication|presentation|patent)\b',
        r'\b(?:led|managed|mentored|trained|supervised)\b[^.!?]*\b(?:team|group|project)\b',
        r'\b(?:presented|published|speaker|talk|workshop|conference)\b'
    ]
    
    achievements = []
    for pattern in quantifiers:
        matches = re.findall(pattern, text, re.IGNORECASE)
        achievements.extend(matches)
    
    # Remove duplicates while preserving order
    unique_achievements = []
    seen = set()
    for ach in achievements:
        if ach.lower() not in seen:
            seen.add(ach.lower())
            unique_achievements.append(ach)
    
    # Calculate score based on number of unique achievements
    achievement_count = len(unique_achievements)
    
    if achievement_count == 0:
        score = 20
        feedback = "No clear achievements or impact statements found. Add quantifiable results (e.g., 'Increased performance by 30%')."
    elif achievement_count == 1:
        score = 50
        feedback = "Found 1 achievement. Add more quantifiable results to strengthen your resume."
    elif achievement_count == 2:
        score = 70
        feedback = "Good start with achievements. Include 1-2 more for greater impact."
    else:
        score = min(90 + (achievement_count * 2), 100)
        feedback = f"Found {achievement_count} achievements. Great job highlighting your impact!"
    
    return score, 100, {
        'achievement_count': achievement_count,
        'achievement_examples': unique_achievements[:5],
        'feedback': feedback
    }

def calculate_ats_score(text: str, return_full_result: bool = False) -> Union[float, ScoreResult]:
    """
    Calculate the ATS score for the given resume text.

    Args:
        text: The resume text to score
        return_full_result: If True, returns the full ScoreResult object with detailed feedback

    Returns:
        Union[float, ScoreResult]: The ATS score (0-100) or full ScoreResult object if return_full_result is True
    """
    try:
        if not text or not isinstance(text, str) or not text.strip():
            logger.warning("Empty or invalid text provided for ATS scoring")
            return ScoreResult(0, 100, {}, ["Empty or invalid resume text provided"]) if return_full_result else 0.0
            
        scorer = ATSScorer()
        result = scorer.calculate_score(text)
        
        # Ensure the score is within valid range
        result.score = max(0, min(100, result.score))
        
        # Log the score for debugging
        logger.info(f"Calculated ATS score: {result.score:.1f}")
        
        return result if return_full_result else result.score
        
    except Exception as e:
        error_msg = f"Error calculating ATS score: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Text length: {len(text) if text else 0} characters")
        logger.error(f"Text sample: {text[:200]}..." if text else "No text provided")
        
        if return_full_result:
            return ScoreResult(0, 100, {}, [error_msg])
        return 0.0
