import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateStyle(Enum):
    """Available template styles for resume formatting."""
    MINIMAL = auto()
    PROFESSIONAL = auto()
    MODERN = auto()
    EXECUTIVE = auto()
    TECHNICAL = auto()
    CREATIVE = auto()

@dataclass
class ContactInfo:
    """Contact information for the resume header."""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    address: str = ""
    
    def format(self, include_icons: bool = False) -> str:
        """Format contact information as a single line."""
        parts = []
        if self.email:
            prefix = "✉️ " if include_icons else ""
            parts.append(f"{prefix}{self.email}")
        if self.phone:
            prefix = "📞 " if include_icons else ""
            parts.append(f"{prefix}{self.phone}")
        if self.linkedin:
            prefix = "🔗 " if include_icons else ""
            parts.append(f"{prefix}{self.linkedin}")
        if self.github:
            prefix = "🐙 " if include_icons else ""
            parts.append(f"{prefix}{self.github}")
        if self.portfolio:
            prefix = "🌐 " if include_icons else ""
            parts.append(f"{prefix}{self.portfolio}")
        if self.address:
            prefix = "📍 " if include_icons else ""
            parts.append(f"{prefix}{self.address}")
        return " | ".join(parts)

class ResumeSection(Enum):
    """Standard resume sections."""
    SUMMARY = "Professional Summary"
    EXPERIENCE = "Professional Experience"
    EDUCATION = "Education"
    SKILLS = "Skills"
    PROJECTS = "Projects"
    CERTIFICATIONS = "Certifications"
    LANGUAGES = "Languages"
    ACHIEVEMENTS = "Achievements"
    VOLUNTEER = "Volunteer Experience"
    PUBLICATIONS = "Publications"
    
    @classmethod
    def from_text(cls, text: str) -> Optional['ResumeSection']:
        """Convert section text to enum if it matches a standard section."""
        text_lower = text.lower().strip()
        for section in cls:
            if section.value.lower() in text_lower or text_lower in section.value.lower():
                return section
        return None

class ResumeFormatter:
    """Formats resume content with different templates and styles."""
    
    def __init__(self, contact_info: Optional[ContactInfo] = None):
        self.contact_info = contact_info or ContactInfo()
        self.sections: Dict[ResumeSection, str] = {}
        self._extract_contact_info = True
        
    def add_section(self, section_name: str, content: str) -> None:
        """Add a section to the resume."""
        section = ResumeSection.from_text(section_name)
        if section is None:
            logger.warning(f"Unknown section: {section_name}. Adding as custom section.")
            section_name = section_name.strip()
        else:
            section_name = section.value
            
        self.sections[section_name] = content.strip()
    
    def apply_template(
        self, 
        template: str = "professional",
        include_icons: bool = False,
        page_size: str = "A4",
        font_family: str = "Arial",
        font_size: int = 11,
        line_spacing: float = 1.15,
        margin: float = 1.0,
        primary_color: str = "#2c3e50",
        secondary_color: str = "#7f8c8d",
    ) -> str:
        """
        Apply the specified template to the resume content.
        
        Args:
            template: Template style to apply (minimal, professional, modern, executive, technical, creative)
            include_icons: Whether to include icons in the contact information
            page_size: Page size (A4, Letter, etc.)
            font_family: Font family to use
            font_size: Base font size in points
            line_spacing: Line spacing multiplier
            margin: Page margin in inches
            primary_color: Primary color for headings and accents (hex code)
            secondary_color: Secondary color for subheadings (hex code)
            
        Returns:
            Formatted resume as a string
        """
        try:
            template_style = TemplateStyle[template.upper()]
        except KeyError:
            logger.warning(f"Unknown template: {template}. Using 'professional' instead.")
            template_style = TemplateStyle.PROFESSIONAL
        
        # Start building the formatted resume
        formatted = []
        
        # Add header with contact information
        if self.contact_info and any(
            getattr(self.contact_info, field.name) 
            for field in self.contact_info.__dataclass_fields__.values()
        ):
            formatted.append(self._format_header(template_style, include_icons))
        
        # Add sections in a standard order, falling back to the order they were added
        standard_order = [
            ResumeSection.SUMMARY,
            ResumeSection.EXPERIENCE,
            ResumeSection.EDUCATION,
            ResumeSection.SKILLS,
            ResumeSection.PROJECTS,
            ResumeSection.CERTIFICATIONS,
            ResumeSection.LANGUAGES,
            ResumeSection.ACHIEVEMENTS,
            ResumeSection.VOLUNTEER,
            ResumeSection.PUBLICATIONS,
        ]
        
        # Add sections in standard order if they exist
        for section in standard_order:
            if section.value in self.sections:
                formatted.append(self._format_section(section.value, template_style))
        
        # Add any remaining custom sections
        for section_name, content in self.sections.items():
            if not any(s.value == section_name for s in standard_order):
                formatted.append(self._format_section(section_name, template_style))
        
        # Join all parts with appropriate spacing
        return "\n\n".join(part for part in formatted if part.strip())
    
    def _format_header(self, template_style: TemplateStyle, include_icons: bool = False) -> str:
        """Format the resume header with contact information."""
        parts = []
        
        # Add name as the main heading
        if self.contact_info.full_name:
            name = self.contact_info.full_name.upper()
            if template_style in [TemplateStyle.MODERN, TemplateStyle.CREATIVE]:
                parts.append(f"{name}\n{'=' * len(name)}")
            elif template_style == TemplateStyle.TECHNICAL:
                parts.append(f"# {name}")
            else:
                parts.append(name)
        
        # Add contact information
        contact_line = self.contact_info.format(include_icons)
        if contact_line:
            if template_style in [TemplateStyle.MODERN, TemplateStyle.CREATIVE]:
                parts.append(contact_line)
            elif template_style == TemplateStyle.TECHNICAL:
                parts.append(f"*{contact_line}*")
            else:
                parts.append(contact_line)
        
        return "\n".join(parts)
    
    def _format_section(self, section_name: str, template_style: TemplateStyle) -> str:
        """Format a single section of the resume."""
        content = self.sections[section_name]
        
        if template_style == TemplateStyle.TECHNICAL:
            return f"## {section_name.upper()}\n\n{content}"
        elif template_style in [TemplateStyle.MODERN, TemplateStyle.CREATIVE]:
            return f"{section_name.upper()}\n{'-' * len(section_name)}\n\n{content}"
        else:  # Default professional style
            return f"{section_name.upper()}\n{content}"

def apply_template(
    resume_text: str, 
    template: str = "professional",
    **kwargs
) -> str:
    """
    Apply a template to the given resume text.
    
    Args:
        resume_text: The raw resume text to format
        template: Template style to apply (minimal, professional, modern, executive, technical, creative)
        **kwargs: Additional formatting options to pass to the formatter
        
    Returns:
        Formatted resume text
    """
    formatter = ResumeFormatter()
    
    # Simple parsing of the resume text into sections
    # This is a basic implementation - a real implementation would parse the resume more thoroughly
    sections = re.split(r'\n\s*\n', resume_text.strip())
    
    # Assume the first line is the name if it looks like a name
    if sections and len(sections[0].split()) <= 4 and not any(c.isdigit() for c in sections[0]):
        formatter.contact_info.full_name = sections.pop(0).strip()
    
    # Try to parse contact information from the first section
    if sections and formatter.contact_info.full_name:
        first_section = sections[0].lower()
        if 'email' in first_section or 'phone' in first_section or '@' in first_section:
            contact_lines = sections.pop(0).split('\n')
            for line in contact_lines:
                line = line.strip()
                if not line:
                    continue
                if '@' in line and 'email' not in formatter.contact_info.email.lower():
                    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
                    if email:
                        formatter.contact_info.email = email.group(0)
                elif any(phone in line.lower() for phone in ['phone', 'mobile', 'tel']):
                    phone = re.search(r'\+?[\d\s\-\(\)]{7,}', line)
                    if phone:
                        formatter.contact_info.phone = phone.group(0).strip()
                elif 'linkedin.com' in line.lower():
                    formatter.contact_info.linkedin = line.strip()
                elif 'github.com' in line.lower():
                    formatter.contact_info.github = line.strip()
    
    # Add remaining content as sections
    current_section = "Summary"
    current_content = []
    
    for section in sections:
        lines = section.split('\n')
        section_name = lines[0].strip('\n\r\t :')
        
        # Check if this line is a section header (all caps, ends with colon, or has a special format)
        if (
            len(lines) > 1 and 
            (section_name.isupper() or 
             section_name.endswith(':') or 
             re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', section_name))
        ):
            # Save the previous section
            if current_content:
                formatter.add_section(current_section, '\n'.join(current_content))
                current_content = []
            
            current_section = section_name.rstrip(':')
            current_content.extend(lines[1:])  # Add the rest of the lines to the section
        else:
            current_content.extend(lines)
    
    # Add the last section
    if current_content:
        formatter.add_section(current_section, '\n'.join(current_content))
    
    # Apply the template
    return formatter.apply_template(template=template, **kwargs)
