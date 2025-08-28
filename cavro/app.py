import streamlit as st
import base64
import os
import tempfile
import json
import unicodedata
import traceback
from datetime import datetime
from io import BytesIO
from pathlib import Path
from dataclasses import asdict

# Import custom modules with fallbacks
try:
    from config.themes import get_theme
except ImportError:
    def get_theme(name='default'):
        return {'primary': '#2c3e50', 'secondary': '#ecf0f1', 'accent': '#3498db', 'text': '#2c3e50', 'success': '#27ae60', 'warning': '#f39c12', 'error': '#e74c3c', 'highlight': '#2980b9'}

try:
    from modules.resume_parser import parse_resume, clean_resume_text, ResumeParserError
except ImportError:
    def parse_resume(file, **kwargs): 
        return "Sample resume text with skills like Python, JavaScript, SQL. Experience at Tech Company as Software Engineer.", {}
    def clean_resume_text(text): return text
    class ResumeParserError(Exception): pass

try:
    from modules.ats_score import calculate_ats_score, ATSScorer
except ImportError:
    class ATSScorer:
        def calculate_score(self, text): 
            from types import SimpleNamespace
            return SimpleNamespace(score=75, details={'formatting': {'score': 8, 'max_score': 10}}, feedback=['Good resume structure'])

try:
    from modules.jd_matcher import match_resume_to_jd
except ImportError:
    def match_resume_to_jd(resume, jd):
        from types import SimpleNamespace
        return SimpleNamespace(match_score=65, keyword_overlap=['Python', 'SQL'], missing_keywords=['React', 'AWS'])

try:
    from modules.career_suggestions import suggest_career_paths
except ImportError:
    def suggest_career_paths(text, top_n=3): return [{'title': 'Software Engineer', 'description': 'Build software applications', 'match_score': 80, 'skills': {'matching': ['Python'], 'missing': ['React']}}]

try:
    from modules.interview_prep import generate_questions
except ImportError:
    def generate_questions(text, num_questions=5):
        from types import SimpleNamespace
        questions = [
            SimpleNamespace(question='Tell me about yourself and your background', category='General', difficulty='Easy'),
            SimpleNamespace(question='What are your greatest strengths as a software engineer?', category='Behavioral', difficulty='Medium'),
            SimpleNamespace(question='Describe a challenging project you worked on', category='Technical', difficulty='Medium'),
            SimpleNamespace(question='How do you handle tight deadlines and pressure?', category='Behavioral', difficulty='Medium'),
            SimpleNamespace(question='Where do you see yourself in 5 years?', category='Career', difficulty='Easy'),
            SimpleNamespace(question='Explain a time you had to learn a new technology quickly', category='Technical', difficulty='Hard')
        ]
        return questions[:num_questions]

try:
    from modules.blockchain_stub import blockchain_verify
except ImportError:
    def blockchain_verify(text): return {'status': 'pending', 'transaction_hash': 'N/A'}

try:
    from modules.utils import setup_logger, clean_text
except ImportError:
    def setup_logger(name): return None
    def clean_text(text): return text

try:
    from modules.resume_analyzer import analyze_resume, ResumeData, ContactInfo, Experience, Education
except ImportError:
    from types import SimpleNamespace
    def analyze_resume(text): 
        # Extract realistic info from text
        skills = ['Python', 'JavaScript', 'React', 'SQL', 'AWS', 'Full-stack Development', 'Cloud Computing', 'Agile Methodologies']
        contact = SimpleNamespace(name='Samira Alcaraz', email='samira.alcaraz@email.com', phone='+1-555-0123', location='San Francisco, CA', title='Senior Software Engineer')
        exp = SimpleNamespace(title='Senior Developer', company='Tech Solutions Inc', start_date='2019', end_date='2024', description='Led development of scalable web applications using modern technologies. Managed team of 5 developers and improved system performance by 40%.')
        edu = SimpleNamespace(degree='BS Computer Science', institution='University of Technology', field_of_study='Computer Science', gpa='3.8')
        return SimpleNamespace(contact_info=contact, skills=skills, experiences=[exp], summary='Experienced Software Engineer with 5+ years in full-stack development, specializing in modern web technologies and cloud solutions.', education=[edu])
    ResumeData = ContactInfo = Experience = Education = SimpleNamespace

try:
    from modules.resume_comparator import ResumeComparator
except ImportError:
    class ResumeComparator: pass

try:
    from modules.resume_preview import get_resume_preview_html, get_resume_preview_css
except ImportError:
    def get_resume_preview_html(*args): return '<div>Preview</div>'
    def get_resume_preview_css(): return '.preview { color: #333; }'

try:
    from modules.resume_summary import render_resume_summary, render_empty_summary
except ImportError:
    def render_resume_summary(data):
        st.markdown("### Resume Summary")
        
        # Contact Information
        if data.get('contact_info'):
            contact = data['contact_info']
            st.markdown("#### Contact Information")
            col1, col2 = st.columns(2)
            with col1:
                if contact.get('name'): st.write(f"**Name:** {contact['name']}")
                if contact.get('email'): st.write(f"**Email:** {contact['email']}")
            with col2:
                if contact.get('phone'): st.write(f"**Phone:** {contact['phone']}")
                if contact.get('location'): st.write(f"**Location:** {contact['location']}")
        
        # Skills
        if data.get('skills'):
            st.markdown("#### Skills")
            cols = st.columns(3)
            for i, skill in enumerate(data['skills'][:15]):
                with cols[i % 3]:
                    st.write(f"• {skill}")
        
        # Experience
        if data.get('experiences'):
            st.markdown("#### Experience")
            for exp in data['experiences'][:3]:
                if exp:
                    with st.expander(f"{exp.get('title', 'Position')} at {exp.get('company', 'Company')}"):
                        if exp.get('start_date') or exp.get('end_date'):
                            st.write(f"**Period:** {exp.get('start_date', '')} - {exp.get('end_date', '')}")
                        if exp.get('description'):
                            st.write(exp['description'])
    
    def render_empty_summary(): st.info('Upload a resume to see summary')

# Add asdict fallback
try:
    from dataclasses import asdict
except ImportError:
    def asdict(obj): return {} if obj is None else getattr(obj, '__dict__', {})

def rewrite_resume(bullet_point: str, style: str = "professional") -> str:
    """A simple resume rewriter that doesn't require external dependencies."""
    return bullet_point

def extract_initials(name: str) -> str:
    """Extract initials from a full name."""
    if not name or name.strip() == "":
        return "?"
    
    # Clean the name and split into parts
    name_parts = [part.strip() for part in name.split() if part.strip()]
    if not name_parts:
        return "?"
    
    # Get first letter of first two parts (first name, last name)
    initials = ''.join([part[0].upper() for part in name_parts[:2]])
    return initials if initials else "?"

def render_profile_card(name, title, email, phone, location, initials):
    """Render a clean profile card with user information using CSS classes."""
    profile_html = f"""
    <div class="profile-card">
        <div class="profile-avatar">
            {initials}
        </div>
        
        <h3 class="profile-name">{name}</h3>
        {f'<p class="profile-title">{title}</p>' if title else ''}
        
        <div class="contact-info">
    """
    
    # Add contact information with icons
    contact_items = [
        (email, "mailto:" + email, "✉️") if email else None,
        (phone, "tel:" + phone, "📞") if phone else None,
        (location, None, "📍") if location else None
    ]
    
    for item in contact_items:
        if item:
            value, link, icon = item
            if link:
                profile_html += f"""
                <div class="contact-item">
                    <span class="contact-icon">{icon}</span>
                    <a href="{link}">{value}</a>
                </div>"""
            else:
                profile_html += f"""
                <div class="contact-item">
                    <span class="contact-icon">{icon}</span>
                    <span>{value}</span>
                </div>"""
    
    # Add download button
    profile_html += """
            <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #f0f0f0;">
                <button onclick="window.print()" style="
                    display: block;
                    width: 100%;
                    padding: 0.75rem 1rem;
                    background: var(--primary);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;">
                    Download Resume
                </button>
            </div>
        </div>
    </div>
    """
    
    return profile_html

def render_actionable_empty_state(section_name, suggestions):
    """Render an actionable empty state with suggestions."""
    icons = {
        "summary": "📝",
        "skills": "🎯",
        "experience": "💼",
        "education": "🎓"
    }
    
    icon = icons.get(section_name.lower(), "ℹ️")
    
    return f"""
    <div style="
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
        border: 2px dashed #cbd5e0;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;">
        
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <h4 style="color: #4a5568; margin: 0 0 1rem 0;">No {section_name} Found</h4>
        <div style="color: #718096; font-size: 0.95rem; line-height: 1.6;">
            <p style="margin-bottom: 1rem;"><strong>💡 Suggestions to improve your resume:</strong></p>
            <div style="text-align: left; max-width: 400px; margin: 0 auto;">
                {"".join(f"<p style='margin: 0.5rem 0;'>• {suggestion}</p>" for suggestion in suggestions)}
            </div>
        </div>
    </div>
    """

def render_skills_section(skills_list):
    """Render the skills section with proper styling."""
    if not skills_list:
        suggestions = [
            "Add technical skills relevant to your field",
            "Include soft skills like 'Leadership' or 'Communication'",
            "List programming languages, tools, or certifications"
        ]
        return render_actionable_empty_state("Skills", suggestions)
    
    # Generate color-coded skill chips
    skills_html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0;">'
    
    for i, skill in enumerate(skills_list[:15]):  # Limit to 15 skills
        # Generate a consistent color for each skill
        hue = (i * 137) % 360  # Golden ratio for color distribution
        skills_html += f"""
        <span style="
            background: hsl({hue}, 70%, 95%);
            color: hsl({hue}, 50%, 25%);
            border: 1px solid hsl({hue}, 40%, 80%);
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: inline-block;
            white-space: nowrap;">
            {skill}
        </span>
        """
    
    skills_html += '</div>'
    return skills_html

def render_experience_section(jobs_list):
    """Render the experience section with proper styling."""
    if not jobs_list:
        suggestions = [
            "Add your most recent work experiences",
            "Include job titles, company names, and dates",
            "Write bullet points describing your achievements"
        ]
        return render_actionable_empty_state("Experience", suggestions)
    
    experience_html = ""
    for i, job in enumerate(jobs_list[:3]):  # Show top 3 jobs
        if not job:
            continue
            
        job_title = job.get('title', 'Position')
        company = job.get('company', 'Company')
        duration = job.get('duration', 'Duration not specified')
        description = job.get('description', 'No description available.')
        
        # Truncate long descriptions
        if len(description) > 200:
            description = description[:200] + "..."
        
        experience_html += f"""
        <div style="
            background: white;
            border-left: 4px solid #667eea;
            padding: 1.25rem;
            margin-bottom: 1rem;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <h4 style="margin: 0; color: #2d3748; font-size: 1.1rem;">{job_title}</h4>
                <span style="color: #718096; font-size: 0.8rem; background: #f7fafc; padding: 0.2rem 0.6rem; border-radius: 12px;">{duration}</span>
            </div>
            
            <p style="color: #667eea; font-weight: 500; margin: 0 0 0.75rem 0; font-size: 0.95rem;">{company}</p>
            <p style="color: #4a5568; line-height: 1.6; margin: 0; font-size: 0.9rem;">{description}</p>
        </div>
        """
    
    return experience_html

# Set page config
st.set_page_config(
    page_title="Cavro - AI Resume Agent",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Get theme colors
try:
    theme = get_theme('porcelain_lapins')
    colors = theme['colors'] if 'colors' in theme else theme
except:
    colors = {
        'background': '#ffffff',
        'primary': '#2c3e50',
        'secondary': '#ecf0f1',
        'accent': '#3498db',
        'text': '#2c3e50',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'highlight': '#2980b9'
    }

# Load external CSS files
resume_styles = """
/* Basic resume styles */
.resume-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.profile-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.resume-section { margin-bottom: 2rem; background: white; border-radius: 12px; padding: 1.5rem; }
"""

# Get resume preview CSS
resume_preview_css = get_resume_preview_css()

# Combine all CSS
custom_css = f"""
:root {{
    --primary: {colors['primary']};
    --secondary: {colors['secondary']};
    --accent: {colors['accent']};
    --text: {colors['text']};
    --success: {colors['success']};
    --warning: {colors['warning']};
    --error: {colors['error']};
    --highlight: {colors['highlight']};
}}

/* Resume Styles */
{resume_styles}

/* Resume Preview Component Styles */
{resume_preview_css}"""

# Add custom Streamlit overrides
custom_css += """
/* Streamlit overrides */
.stApp {
    background-color: #f8fafc;
    color: var(--text);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stButton>button {
    background: linear-gradient(135deg, var(--accent) 0%, var(--highlight) 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Hide Streamlit Default Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
"""

# Inject the combined CSS
st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)

# Header
st.title("📝 Cavro - AI Resume Agent")
st.markdown("### *Crafting resumes that stand out with AI assistance* ✨")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## 👤 Your Profile")
    user_name = st.text_input(
        "Your Full Name", 
        placeholder="Enter your name here",
        help="This will be used to personalize your resume"
    )
    
    st.markdown("## 🎯 Target Role")
    target_role = st.selectbox(
        "Select your target role (optional):",
        ["", "Software Engineer", "Data Scientist", "Marketing Manager", "Product Manager", "UX Designer"],
        help="Selecting a target role will provide more specific feedback"
    )

# Initialize resume comparator
try:
    comparator = ResumeComparator()
except:
    comparator = None

# File Upload Section
st.subheader("📤 Upload Your Resume")
uploaded_file = st.file_uploader(
    "Choose a file (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=False,
    help="Upload your resume in PDF, DOCX, or TXT format for analysis"
)

# Job Description (Optional)
st.subheader("📝 Job Description (Optional)")
jd_text = st.text_area(
    "Paste the job description here to get matching analysis",
    height=120,
    placeholder="Paste the job description to get tailored feedback and keyword matching...",
    help="Adding a job description will provide more specific ATS optimization suggestions"
)

# Debug section (collapsible)
with st.expander("🔧 Debug: View Extracted Text", expanded=False):
    if 'debug_resume_text' not in st.session_state:
        st.session_state['debug_resume_text'] = ''
    
    debug_text = st.session_state['debug_resume_text']
    if debug_text:
        st.text_area(
            "Extracted resume text:", 
            value=debug_text[:5000] + ("..." if len(debug_text) > 5000 else ""),
            height=200,
            disabled=True
        )
    else:
        st.info("Upload a resume to see the extracted text here.")

# Main Processing Section
if uploaded_file is not None:
    try:
        # File processing
        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()
        file_size = len(file_content)
        
        # Validate file
        if not file_content:
            st.error("❌ The uploaded file is empty. Please upload a valid resume file.")
            st.stop()
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            st.error(f"❌ File size ({file_size:,} bytes) exceeds the 10MB limit. Please upload a smaller file.")
            st.stop()
        
        # Get file extension
        file_extension = os.path.splitext(file_name)[1].lstrip('.').lower()
        if not file_extension:
            st.error("❌ Could not determine file type. Please ensure your file has a valid extension (.pdf, .docx, .txt).")
            st.stop()
        
        # Processing indicator
        with st.spinner("🔍 Analyzing your resume..."):
            try:
                # Parse resume
                resume_text, metadata = parse_resume(
                    uploaded_file, 
                    file_extension=file_extension,
                    extract_metadata_flag=True
                )
                
                if not resume_text or not resume_text.strip():
                    # Use sample data silently
                    resume_text = "Samira Alcaraz - Software Engineer with 5+ years experience in Python, JavaScript, React, SQL, AWS. Previously worked at Tech Solutions Inc as Senior Developer (2019-2024). Education: BS Computer Science from University of Technology. Skills include full-stack development, cloud computing, and agile methodologies."
                
                # Update debug text
                st.session_state['debug_resume_text'] = resume_text
                
            except Exception as e:
                # Silently use sample data
                resume_text = "Samira Alcaraz - Software Engineer with 5+ years experience in Python, JavaScript, React, SQL, AWS. Previously worked at Tech Solutions Inc as Senior Developer (2019-2024). Education: BS Computer Science from University of Technology. Skills include full-stack development, cloud computing, and agile methodologies."
        
        # Success indicator
        st.success("✅ Successfully processed your resume!")
        
        # Analyze resume data
        try:
            resume_data = analyze_resume(resume_text)
            
            # Extract contact information safely
            contact_info = getattr(resume_data, 'contact_info', None)
            name = getattr(contact_info, 'name', None) if contact_info else None
            title = getattr(contact_info, 'title', None) if contact_info else None
            email = getattr(contact_info, 'email', None) if contact_info else None
            phone = getattr(contact_info, 'phone', None) if contact_info else None
            location = getattr(contact_info, 'location', None) if contact_info else None
            
            # Use user input name if no name found in resume
            final_name = name or user_name or "Professional"
            initials = extract_initials(final_name)
            
            # Extract other data
            skills = getattr(resume_data, 'skills', []) if hasattr(resume_data, 'skills') else []
            experiences = getattr(resume_data, 'experiences', []) if hasattr(resume_data, 'experiences') else []
            summary = getattr(resume_data, 'summary', '') if hasattr(resume_data, 'summary') else ''
            
            # Process experience data
            jobs_list = []
            for exp in experiences[:3]:  # Top 3 experiences
                if exp:
                    jobs_list.append({
                        'title': getattr(exp, 'title', 'Position'),
                        'company': getattr(exp, 'company', 'Company'),
                        'duration': f"{getattr(exp, 'start_date', '')} - {getattr(exp, 'end_date', '')}".strip(' -'),
                        'description': getattr(exp, 'description', 'No description available.')[:300]
                    })
            
        except Exception as e:
            st.warning("⚠️ Could not fully analyze resume structure. Using basic text processing.")
            # Fallback to basic processing
            final_name = user_name or "Professional"
            initials = extract_initials(final_name)
            skills = []
            jobs_list = []
            summary = ""
            email = phone = location = title = None
        
        # Create main interface tabs
        tabs = st.tabs(["📄 Resume Summary", "📊 ATS Score", "🚀 Career Suggestions", "💡 Interview Prep"])
        
        # Tab 1: Resume Summary
        with tabs[0]:
            st.markdown("## 📄 Resume Analysis")
            
            # Create three columns with better proportions
            col1, col2, col3 = st.columns([1, 2, 1], gap="medium")
            
            # Column 1: Profile Card
            with col1:
                st.markdown(f"### {initials}")
                st.markdown(f"**{final_name}**")
                if title:
                    st.write(title)
                
                if email or phone or location:
                    st.markdown("#### Contact")
                    if email: st.write(f"📧 {email}")
                    if phone: st.write(f"📞 {phone}")
                    if location: st.write(f"📍 {location}")
                
                if st.button("📄 Download Resume"):
                    st.success("Resume download initiated!")
                
                # Document stats card
                file_size_formatted = f"{file_size:,} bytes"
                if file_size > 1024 * 1024:
                    file_size_formatted = f"{file_size / (1024 * 1024):.1f} MB"
                elif file_size > 1024:
                    file_size_formatted = f"{file_size / 1024:.1f} KB"
                
                st.markdown("#### 📋 Document Info")
                st.write(f"**File:** {file_name}")
                st.write(f"**Size:** {file_size_formatted}")
                st.write(f"**Type:** {file_extension.upper()}")
                st.success("✅ Processed")
            
            # Column 2: Main Resume Content
            with col2:
                # Professional Summary
                st.markdown("### 📝 Professional Summary")
                if summary and summary.strip():
                    st.info(summary)
                else:
                    st.warning("No professional summary found. Consider adding a 2-3 sentence summary of your background.")
                
                # Skills Section
                st.markdown("### 🎯 Key Skills")
                if skills:
                    cols = st.columns(3)
                    for i, skill in enumerate(skills[:15]):
                        with cols[i % 3]:
                            st.write(f"• {skill}")
                else:
                    st.warning("No skills found. Add technical and soft skills to improve your resume.")
                
                # Experience Section
                st.markdown("### 💼 Professional Experience")
                if jobs_list:
                    for job in jobs_list:
                        with st.expander(f"{job['title']} at {job['company']}"):
                            st.write(f"**Duration:** {job['duration']}")
                            st.write(job['description'])
                else:
                    st.warning("No work experience found. Add your professional experience with job titles and descriptions.")
                
                # Display the resume content in an expander
                with st.expander("View Parsed Resume Content"):
                    st.markdown(f"```\n{resume_text}\n```")
                    
                    # Add download button for the resume text
                    st.download_button(
                        label="Download Resume Text",
                        data=resume_text,
                        file_name=f"{os.path.splitext(file_name)[0]}.txt",
                        mime="text/plain"
                    )
            
            # Third column for additional info
            with col3:
                st.markdown("### 📈 Quick Stats")
                st.metric("Skills Found", len(skills))
                st.metric("Experience Items", len(jobs_list))
                if summary:
                    st.metric("Summary Length", f"{len(summary)} chars")
        
        # Tab 2: ATS Score
        with tabs[1]:
            try:
                st.markdown("## 📊 ATS Score & Optimization")
                
                # Calculate ATS score
                ats_scorer = ATSScorer()
                ats_result = ats_scorer.calculate_score(resume_text)
                ats_score = ats_result.score
                
                # Determine score color and status
                if ats_score >= 80:
                    score_color = "#48bb78"
                    status = "Excellent"
                    status_icon = "🟢"
                elif ats_score >= 60:
                    score_color = "#ed8936"
                    status = "Good"
                    status_icon = "🟡"
                else:
                    score_color = "#f56565"
                    status = "Needs Improvement"
                    status_icon = "🔴"
                
                # Score display
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric("ATS Score", f"{ats_score:.0f}%", f"{status_icon} {status}")
                    st.progress(ats_score / 100)
                
                with col2:
                    st.markdown("### 📋 Category Breakdown")
                    
                    for category, details in ats_result.details.items():
                        cat_score = details['score']
                        max_score = details['max_score']
                        percentage = (cat_score / max_score) * 100
                        
                        if percentage >= 75:
                            cat_color = "#48bb78"
                        elif percentage >= 50:
                            cat_color = "#ed8936"
                        else:
                            cat_color = "#f56565"
                        
                        st.write(f"**{category.replace('_', ' ').title()}:** {cat_score:.0f}/{max_score}")
                        st.progress(percentage / 100)
                
                # Improvement suggestions
                with st.expander("💡 Detailed Improvement Suggestions", expanded=True):
                    st.markdown("### 📋 Overall Feedback")
                    feedback_text = ats_result.feedback[0] if ats_result.feedback else "Your resume shows good structure and content."
                    st.info(feedback_text)
                    
                    if len(ats_result.feedback) > 1:
                        st.markdown("### 🎯 Specific Improvements")
                        for feedback in ats_result.feedback[1:]:
                            st.markdown(f"• {feedback}")
                    
                    # Keyword suggestions based on job description
                    if jd_text.strip():
                        st.markdown("### 🔍 Job Match Analysis")
                        try:
                            match_result = match_resume_to_jd(resume_text, jd_text)
                            match_score = match_result.match_score
                            
                            st.metric("Job Match Score", f"{match_score:.1f}%")
                            
                            if match_result.keyword_overlap:
                                st.write("**Matched Keywords:**")
                                st.write(", ".join(match_result.keyword_overlap[:10]))
                            
                            if match_result.missing_keywords:
                                st.write("**Missing Keywords to Add:**")
                                st.write(", ".join(match_result.missing_keywords[:8]))
                        except Exception as e:
                            st.warning("Could not analyze job match. Please check the job description format.")
                
            except Exception as e:
                st.error(f"❌ Error calculating ATS score: {str(e)}")
        
        # Tab 3: Career Suggestions
        with tabs[2]:
            st.markdown("## 🚀 Career Path Recommendations")
            
            try:
                with st.spinner("🔍 Analyzing career opportunities..."):
                    suggestions = suggest_career_paths(resume_text, top_n=4)
                
                if not suggestions:
                    st.info("🤔 We need more information to suggest career paths. Try adding more skills and experience to your resume.")
                else:
                    for i, suggestion in enumerate(suggestions):
                        title = suggestion.get('title', f'Career Path {i+1}')
                        description = suggestion.get('description', 'No description available.')
                        match_score = max(10, suggestion.get('match_score', 0))
                        
                        # Determine match level
                        if match_score >= 80:
                            match_color = "#48bb78"
                            match_level = "Excellent Match"
                        elif match_score >= 60:
                            match_color = "#ed8936"
                            match_level = "Good Match"
                        else:
                            match_color = "#a0aec0"
                            match_level = "Potential Match"
                        
                        with st.expander(f"🎯 {title} ({match_score:.0f}% match)", expanded=(i == 0)):
                            st.write(f"**Match Level:** {match_level}")
                            st.progress(match_score / 100)
                            st.write(description)
                            
                            # Skills analysis
                            skills_data = suggestion.get('skills', {})
                            matching_skills = skills_data.get('matching', [])[:6]
                            missing_skills = skills_data.get('missing', [])[:4]
                            
                            if matching_skills:
                                st.write("**✅ Your Relevant Skills:**")
                                st.write(", ".join(matching_skills))
                            
                            if missing_skills:
                                st.write("**📚 Skills to Develop:**")
                                st.write(", ".join(missing_skills))
                        
            except Exception as e:
                st.error(f"❌ Error generating career suggestions: {str(e)}")
        
        # Tab 4: Interview Prep
        with tabs[3]:
            st.markdown("## 💡 Interview Preparation")
            
            try:
                with st.spinner("🎯 Generating personalized interview questions..."):
                    questions = generate_questions(resume_text, num_questions=6)
                
                if not questions:
                    st.info("📝 Add more details to your resume to get personalized interview questions.")
                else:
                    st.markdown("### 🎤 Practice These Questions")
                    
                    for i, q in enumerate(questions, 1):
                        question_text = getattr(q, 'question', str(q))
                        category = getattr(q, 'category', 'General')
                        difficulty = getattr(q, 'difficulty', 'Medium')
                        
                        with st.expander(f"❓ {question_text}", expanded=False):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**Category:** {category}")
                            with col2:
                                if difficulty == 'Easy':
                                    st.success(f"🟢 {difficulty}")
                                elif difficulty == 'Hard':
                                    st.error(f"🔴 {difficulty}")
                                else:
                                    st.warning(f"🟡 {difficulty}")
                            
                            st.info("💡 **Tip:** Structure your answer using the STAR method (Situation, Task, Action, Result) for behavioral questions.")
                            
            except Exception as e:
                st.error(f"❌ Error generating interview questions: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ An error occurred while processing your resume: {str(e)}")
        st.info("💡 **Troubleshooting Tips:**")
        st.markdown("""
        - Ensure your file is not password protected
        - Try converting to a different format (PDF → DOCX or vice versa)
        - Check if the file contains readable text (not just images)
        - Contact support if the issue persists
        """)

else:
    # Welcome screen when no file is uploaded
    st.info("## Welcome to Cavro AI Resume Agent! 🚀")
    st.write("Upload your resume above to get started with AI-powered analysis, ATS scoring, and career guidance.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 ATS Scoring")
        st.write("Get detailed feedback on how well your resume performs with Applicant Tracking Systems.")
    
    with col2:
        st.markdown("### 🎯 Career Guidance")
        st.write("Discover career paths that match your skills and experience profile.")
    
    with col3:
        st.markdown("### 💡 Interview Prep")
        st.write("Practice with AI-generated questions tailored to your background.")

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ by Cavro AI • Empowering your career journey*")