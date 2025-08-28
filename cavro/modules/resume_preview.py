"""
Resume Preview Component

This module contains the HTML and CSS for the resume preview component.
"""

def get_resume_preview_html(file_name: str, file_size: int, skills_matched: int = 0, experience_years: int = 0) -> str:
    """
    Generate HTML for the resume preview component.
    
    Args:
        file_name: Name of the uploaded file
        file_size: Size of the file in bytes
        skills_matched: Percentage of skills matched (0-100)
        experience_years: Number of years of experience
        
    Returns:
        str: HTML string for the resume preview
    """
    return f"""
    <div class="resume-preview">
        <div class="file-info">
            <div class="file-info-item">
                <span class="file-info-label">File Name:</span>
                <span class="file-info-value">{file_name}</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">File Size:</span>
                <span class="file-info-value">{file_size / 1024:.1f} KB</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">Last Updated:</span>
                <span class="file-info-value">Today</span>
            </div>
        </div>
        
        <h4 class="preview-title">Quick Stats</h4>
        
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-header">
                    <span class="stat-label">Skills Matched:</span>
                    <span class="stat-value">{skills_matched}%</span>
                </div>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: {skills_matched}%;"></div>
                </div>
            </div>
            
            <div class="stat-item">
                <div class="stat-header">
                    <span class="stat-label">Experience:</span>
                    <span class="stat-value">{experience_years} {'year' if experience_years == 1 else 'years'}</span>
                </div>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: {min(experience_years * 10, 100)}%; background: #4CAF50;"></div>
                </div>
            </div>
        </div>
        
        <div class="preview-actions">
            <button class="download-button" onclick="window.print()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                Download Resume
            </button>
        </div>
    </div>
    """

def get_resume_preview_css() -> str:
    """
    Get the CSS styles for the resume preview component.
    
    Returns:
        str: CSS styles for the resume preview
    """
    return """
    .resume-preview {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #f0f0f0;
    }
    
    .file-info {
        margin-bottom: 1.5rem;
    }
    
    .file-info-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .file-info-label {
        color: var(--text-secondary, #666);
    }
    
    .file-info-value {
        font-weight: 500;
        color: var(--text, #333);
    }
    
    .preview-title {
        color: var(--primary, #4a90e2);
        margin: 1.5rem 0 1rem 0;
        font-size: 1.1rem;
    }
    
    .stats-container {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        margin-bottom: 1.75rem;
    }
    
    .stat-item {
        margin-bottom: 0.5rem;
    }
    
    .stat-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        align-items: center;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: var(--text-secondary, #666);
    }
    
    .stat-value {
        font-weight: 600;
        color: var(--text, #333);
        font-size: 0.95rem;
    }
    
    .stat-bar {
        height: 6px;
        background-color: #f0f2f5;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .stat-bar-fill {
        height: 100%;
        border-radius: 3px;
        background: linear-gradient(90deg, var(--accent, #4a90e2), var(--highlight, #2c3e50));
        transition: width 0.3s ease;
    }
    
    .preview-actions {
        margin-top: 1.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid #f0f0f0;
    }
    
    .download-button {
        width: 100%;
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, var(--accent, #4a90e2) 0%, var(--highlight, #2c3e50) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .download-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .download-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .download-button svg {
        width: 16px;
        height: 16px;
    }
"""
