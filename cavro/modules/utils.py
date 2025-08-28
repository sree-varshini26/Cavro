import re
import logging
import unicodedata
import os
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Type
from datetime import datetime, date
from pathlib import Path

def setup_logger(name=__name__, log_level=logging.INFO):
    """
    Set up a logger with a standard configuration.
    
    Args:
        name: Name for the logger
        log_level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_dir / 'app.log')
    
    # Set log levels
    console_handler.setLevel(log_level)
    file_handler.setLevel(log_level)
    
    # Create formatters and add it to the handlers
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Set up default logger
logger = setup_logger()

T = TypeVar('T')

def clean_text(text: str, preserve_case: bool = False) -> str:
    """
    Clean and normalize text by removing extra whitespace and normalizing unicode.
    
    Args:
        text: The input text to clean
        preserve_case: If False, convert text to lowercase
        
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Normalize unicode (e.g., convert é to e)
    text = unicodedata.normalize('NFKD', text)
    
    # Remove non-printable characters except basic whitespace
    text = ''.join(char for char in text if char.isprintable() or char.isspace())
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Optionally convert to lowercase
    if not preserve_case:
        text = text.lower()
    
    return text

def extract_emails(text: str) -> List[str]:
    """
    Extract all email addresses from the given text.
    
    Args:
        text: The text to search for email addresses
        
    Returns:
        List of unique email addresses found in the text
    """
    if not text:
        return []
    
    # Simple email regex pattern (covers most common cases)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    
    # Remove duplicates while preserving order
    seen = set()
    return [email.lower() for email in emails if not (email in seen or seen.add(email))]

def extract_phone_numbers(text: str) -> List[str]:
    """
    Extract phone numbers from the given text.
    
    Args:
        text: The text to search for phone numbers
        
    Returns:
        List of unique phone numbers found in the text
    """
    if not text:
        return []
    
    # Common phone number patterns
    patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US/Canada
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # US/Canada without parentheses
        r'\d{5}[-.\s]?\d{6}',  # India (10-11 digits)
    ]
    
    phone_numbers = []
    for pattern in patterns:
        phone_numbers.extend(re.findall(pattern, text))
    
    # Remove duplicates while preserving order
    seen = set()
    return [num for num in phone_numbers if not (num in seen or seen.add(num))]

def extract_links(text: str) -> List[str]:
    """
    Extract URLs from the given text.
    
    Args:
        text: The text to search for URLs
        
    Returns:
        List of unique URLs found in the text
    """
    if not text:
        return []
    
    # Simple URL pattern (covers http, https, ftp, etc.)
    url_pattern = r'https?://[^\s\n\r\(\)\[\]\{\}\<\>"]+'
    urls = re.findall(url_pattern, text)
    
    # Remove duplicates while preserving order
    seen = set()
    return [url for url in urls if not (url in seen or seen.add(url))]

def parse_date(date_str: str, formats: Optional[List[str]] = None) -> Optional[date]:
    """
    Parse a date string into a date object using multiple possible formats.
    
    Args:
        date_str: The date string to parse
        formats: List of date format strings to try (defaults to common formats)
        
    Returns:
        A date object if parsing succeeds, None otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    if formats is None:
        formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
            '%d-%b-%Y', '%d %b %Y', '%b %d, %Y',
            '%d-%B-%Y', '%d %B %Y', '%B %d, %Y',
            '%Y', '%m/%Y', '%b %Y', '%B %Y'
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    
    return None

def format_date(date_obj: Union[date, datetime, str], fmt: str = '%Y-%m-%d') -> str:
    """
    Format a date object or date string into the specified format.
    
    Args:
        date_obj: The date to format (can be date, datetime, or string)
        fmt: The output format string (default: YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ""
    
    if isinstance(date_obj, str):
        parsed = parse_date(date_obj)
        if not parsed:
            return date_obj  # Return original if parsing fails
        date_obj = parsed
    
    try:
        return date_obj.strftime(fmt)
    except (AttributeError, ValueError):
        return str(date_obj)

def safe_get(dictionary: Dict, *keys, default: Any = None) -> Any:
    """
    Safely get a value from a nested dictionary without raising KeyError.
    
    Args:
        dictionary: The dictionary to search
        *keys: One or more keys to traverse the dictionary
        default: Default value to return if any key is not found
        
    Returns:
        The value if found, otherwise the default value
    """
    current = dictionary
    for key in keys:
        try:
            current = current[key]
        except (KeyError, TypeError, AttributeError):
            return default
    return current

def chunk_text(text: str, max_length: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into chunks of specified length with optional overlap.
    
    Args:
        text: The text to chunk
        max_length: Maximum length of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or max_length <= 0:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + max_length, text_length)
        
        # Try to find a good breaking point (whitespace or punctuation)
        if end < text_length:
            # Look backward for whitespace
            break_pos = text.rfind(' ', start, end)
            if break_pos == -1 or break_pos < start + max_length // 2:
                # If no good break found, look forward for whitespace
                break_pos = text.find(' ', end - 1, min(end + 100, text_length))
                if break_pos == -1:
                    # If still no break found, just break at max_length
                    break_pos = end
            end = break_pos
        
        chunks.append(text[start:end].strip())
        start = end - overlap if end - overlap > start else end
    
    return chunks

def get_file_extension(filename: str, lower: bool = True) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename: The filename or path
        lower: Whether to return the extension in lowercase
        
    Returns:
        The file extension (without the dot), or empty string if none
    """
    if not filename:
        return ""
    
    # Handle hidden files and paths with dots in directory names
    name_parts = Path(filename).suffixes
    if not name_parts:
        return ""
    
    # Get the last suffix (handles .tar.gz, etc.)
    ext = name_parts[-1].lstrip('.')
    return ext.lower() if lower and ext else ext

def safe_cast(value: Any, target_type: Type[T], default: T = None) -> T:
    """
    Safely cast a value to the specified type, returning a default if the cast fails.
    
    Args:
        value: The value to cast
        target_type: The target type (e.g., int, float, str)
        default: Default value to return if casting fails
        
    Returns:
        The cast value, or the default if casting fails
    """
    if value is None:
        return default
    
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return default

def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if the email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Simple but effective email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def remove_special_chars(text: str, keep_chars: str = '') -> str:
    """
    Remove special characters from a string, keeping only alphanumeric and specified characters.
    
    Args:
        text: The text to process
        keep_chars: Additional characters to keep (e.g., ' -_')
        
    Returns:
        The cleaned text
    """
    if not text:
        return ""
    
    # Keep alphanumeric, whitespace, and specified characters
    pattern = rf'[^\w\s{re.escape(keep_chars)}]'
    return re.sub(pattern, '', text)

def truncate_text(text: str, max_length: int = 100, ellipsis: str = '...') -> str:
    """
    Truncate text to a maximum length, adding an ellipsis if truncated.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the result (including ellipsis if added)
        ellipsis: The ellipsis string to add if text is truncated
        
    Returns:
        The truncated text, with ellipsis if it was truncated
    """
    if not text or len(text) <= max_length:
        return text
    
    if max_length <= len(ellipsis):
        return ellipsis[:max_length]
    
    return text[:max_length - len(ellipsis)] + ellipsis
