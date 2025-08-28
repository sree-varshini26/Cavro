"""
Theme configuration for the Cavro Resume Agent application.

This module provides a collection of color themes and helper functions
to manage the application's visual appearance.
"""
from typing import Dict, Literal, TypedDict

class ThemeColors(TypedDict):
    """Type definition for theme color configuration."""
    background: str
    primary: str
    secondary: str
    accent: str
    text: str
    highlight: str

# Available themes
theme_presets = {
    'porcelain_lapins': {
        'name': 'Porcelain & Lapins',
        'colors': {
            "background": "#F9F9F9",   # Porcelain White
            "primary": "#3A4E7A",      # Lapins Blue
            "secondary": "#E8E8E8",    # Light Gray
            "accent": "#6FAED9",       # Sky Blue
            "text": "#2C3E50",        # Dark Blue-Gray
            "highlight": "#4A6DA7",    # Darker Blue
            "success": "#27AE60",     # Green
            "warning": "#F39C12",     # Orange
            "error": "#E74C3C"        # Red
        }
    },
    'midnight_sky': {
        'name': 'Midnight Sky',
        'colors': {
            "background": "#0F172A",   # Dark Blue
            "primary": "#60A5FA",      # Light Blue
            "secondary": "#1E293B",    # Dark Slate
            "accent": "#818CF8",       # Periwinkle
            "text": "#E2E8F0",        # Light Gray
            "highlight": "#38BDF8",    # Sky Blue
            "success": "#34D399",     # Emerald
            "warning": "#FBBF24",     # Yellow
            "error": "#F87171"        # Light Red
        }
    },
    'minimal_gray': {
        'name': 'Minimal Gray',
        'colors': {
            "background": "#F9FAFB",   # Off-White
            "primary": "#374151",      # Dark Gray
            "secondary": "#E5E7EB",    # Light Gray
            "accent": "#6B7280",       # Medium Gray
            "text": "#111827",        # Almost Black
            "highlight": "#4F46E5",    # Indigo
            "success": "#10B981",     # Green
            "warning": "#F59E0B",     # Amber
            "error": "#EF4444"        # Red
        }
    },
    'ocean_breeze': {
        'name': 'Ocean Breeze',
        'colors': {
            "background": "#F0F9FF",   # Ice Blue
            "primary": "#0369A1",      # Deep Blue
            "secondary": "#E0F2FE",    # Light Blue
            "accent": "#0EA5E9",       # Sky Blue
            "text": "#0C4A6E",        # Dark Blue
            "highlight": "#38BDF8",    # Light Blue
            "success": "#10B981",     # Green
            "warning": "#F59E0B",     # Amber
            "error": "#EF4444"        # Red
        }
    }
}

def get_theme(theme_name: str = 'porcelain_lapins') -> Dict[str, str]:
    """
    Get a theme by name.
    
    Args:
        theme_name: Name of the theme to retrieve
        
    Returns:
        Dictionary containing the theme colors
        
    Raises:
        KeyError: If the specified theme doesn't exist
    """
    if theme_name not in theme_presets:
        raise KeyError(f"Theme '{theme_name}' not found. Available themes: {', '.join(theme_presets.keys())}")
    return theme_presets[theme_name]['colors']

def list_themes() -> Dict[str, str]:
    """
    List all available themes.
    
    Returns:
        Dictionary mapping theme IDs to their display names
    """
    return {theme_id: theme_data['name'] for theme_id, theme_data in theme_presets.items()}

# Default theme
theme = theme_presets['porcelain_lapins']['colors']
