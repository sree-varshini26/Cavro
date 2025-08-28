"""
Resume Summary Component

This module provides functions to generate and display a clean, well-formatted
summary of the resume analysis results.
"""
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import streamlit as st

def get_summary_css() -> str:
    """
    Returns the CSS styles for the resume summary component.
    
    Returns:
        str: CSS styles as a string
    """
    return """
    .summary-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #f0f0f0;
    }
    
    .summary-header {
        color: var(--primary, #4a90e2);
        margin: 0 0 1.25rem 0;
        font-size: 1.3rem;
        font-weight: 600;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 0.75rem;
    }
    
    .summary-content {
        line-height: 1.7;
        color: #333;
        font-size: 0.95rem;
    }
    
    .highlight {
        color: var(--accent, #4a90e2);
        font-weight: 600;
    }
    
    .section-title {
        color: var(--primary, #4a90e2);
        font-size: 1.1rem;
        margin: 1.5rem 0 0.75rem 0;
        font-weight: 600;
    }
    
    .skill-tag {
        display: inline-block;
        background: #f0f7ff;
        color: var(--accent, #4a90e2);
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.85rem;
        border: 1px solid #d0e3ff;
    }
    
    .experience-item {
        margin-bottom: 1.25rem;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid #f5f5f5;
    }
    
    .experience-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    .job-title {
        font-weight: 600;
        color: #2d3748;
        margin: 0 0 0.25rem 0;
    }
    
    .company-name {
        color: #4a5568;
        font-size: 0.95rem;
        margin: 0 0 0.5rem 0;
    }
    
    .date-range {
        color: #718096;
        font-size: 0.85rem;
        margin: 0 0 0.5rem 0;
    }
    
    .job-description {
        color: #4a5568;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0.5rem 0 0 0;
    }
    
    .education-item {
        margin-bottom: 1rem;
    }
    
    .degree {
        font-weight: 600;
        color: #2d3748;
        margin: 0 0 0.25rem 0;
    }
    
    .institution {
        color: #4a5568;
        font-size: 0.95rem;
        margin: 0 0 0.25rem 0;
    }
    
    .empty-state {
        color: #718096;
        font-style: italic;
        padding: 1rem 0;
        text-align: center;
    }
    """

def render_resume_summary(resume_data: Dict[str, Any]) -> None:
    """
    Render the resume summary section with clean formatting using Streamlit components.
    
    Args:
        resume_data: Dictionary containing parsed resume data
    """
    # Apply CSS
    st.markdown(f"<style>{get_summary_css()}</style>", unsafe_allow_html=True)
    
    # Create a container with a nice card style
    with st.container():
        st.markdown("### Resume Summary")
        
        # Contact Information Section
        if resume_data.get('contact_info'):
            contact = resume_data['contact_info']
            st.markdown("---")
            st.markdown("#### Contact Information")
            
            col1, col2 = st.columns(2)
            with col1:
                if contact.get('name'):
                    st.markdown(f"**Name:** {contact['name']}")
                if contact.get('email'):
                    st.markdown(f"**Email:** {contact['email']}")
            with col2:
                if contact.get('phone'):
                    st.markdown(f"**Phone:** {contact['phone']}")
                if contact.get('location'):
                    st.markdown(f"**Location:** {contact['location']}")
        
        # Professional Summary Section
        if resume_data.get('summary'):
            st.markdown("---")
            st.markdown("#### Professional Summary")
            st.markdown(resume_data['summary'])
        
        # Skills Section
        if resume_data.get('skills'):
            st.markdown("---")
            st.markdown("#### Key Skills")
            cols = st.columns(3)  # 3 columns for skills
            for i, skill in enumerate(resume_data['skills']):
                with cols[i % 3]:
                    st.markdown(f"- {skill}")
        
        # Work Experience Section
        if resume_data.get('experiences'):
            st.markdown("---")
            st.markdown("#### Work Experience")
            
            for exp in resume_data['experiences'][:5]:  # Limit to 5 most recent
                with st.expander(f"{exp.get('title', '')} at {exp.get('company', '')}"):
                    # Format date range
                    date_range = []
                    if exp.get('start_date'):
                        date_range.append(exp['start_date'])
                    if exp.get('end_date'):
                        date_range.append('Present' if exp.get('is_current', False) else exp['end_date'])
                    
                    if date_range:
                        st.caption(" ".join(date_range))
                    
                    if exp.get('description'):
                        st.markdown(exp["description"])
        
        # Education Section
        if resume_data.get('education'):
            st.markdown("---")
            st.markdown("#### Education")
            
            for edu in resume_data['education'][:3]:  # Limit to 3 most recent
                with st.expander(edu.get('degree', '')):
                    if edu.get('institution'):
                        st.markdown(f"**Institution:** {edu['institution']}")
                    
                    # Field of study
                    if edu.get('field_of_study'):
                        st.markdown(f"**Field of Study:** {edu['field_of_study']}")
                    
                    # Date range
                    date_range = []
                    if edu.get('start_date'):
                        date_range.append(edu['start_date'])
                    if edu.get('end_date'):
                        date_range.append(edu['end_date'])
                    
                    if date_range:
                        st.markdown(f"**Period:** {' - '.join(date_range)}")
                    
                    # GPA
                    if edu.get('gpa'):
                        st.markdown(f"**GPA:** {edu['gpa']}")
                    
                    if edu.get('description'):
                        st.markdown("**Details:**")
                        st.markdown(edu['description'])

def render_empty_summary() -> None:
    """Render an empty state for the resume summary using Streamlit components."""
    with st.container():
        st.markdown("### Resume Summary")
        st.markdown("---")
        st.info("ℹ️ Upload a resume to see the analysis and summary.")
        st.markdown("""
        Once you upload a resume, you'll see:
        - Contact information
        - Professional summary
        - Key skills
        - Work experience
        - Education details
        """)
