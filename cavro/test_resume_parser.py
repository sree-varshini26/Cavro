"""
Test script for the resume parser module.
This script tests the resume parser with sample resume files.
"""
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from modules.resume_parser import parse_resume, ResumeParserError, FileType
from modules.resume_parser import ResumeMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_resume_parser.log')
    ]
)
logger = logging.getLogger(__name__)

def test_parse_resume(file_path: str, expected_type: FileType) -> Tuple[bool, str]:
    """
    Test the parse_resume function with a single file.
    
    Args:
        file_path: Path to the resume file
        expected_type: Expected file type
        
    Returns:
        Tuple of (success, message)
    """
    try:
        logger.info(f"Testing file: {file_path}")
        
        # Test with file path
        text, metadata = parse_resume(file_path)
        
        # Basic validation
        if not text or not isinstance(text, str):
            return False, f"No text extracted from {file_path}"
            
        if not metadata or not isinstance(metadata, ResumeMetadata):
            return False, f"No metadata extracted from {file_path}"
            
        if metadata.file_type != expected_type:
            return False, (
                f"Incorrect file type detected for {file_path}. "
                f"Expected {expected_type}, got {metadata.file_type}"
            )
            
        logger.info(f"Successfully parsed {file_path}")
        logger.info(f"Extracted {len(text)} characters")
        logger.info(f"Metadata: {metadata}")
        
        return True, f"Successfully parsed {file_path}"
        
    except ResumeParserError as e:
        return False, f"ResumeParserError: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def run_tests():
    """Run all test cases."""
    # Test files directory
    test_dir = Path("test_resumes")
    if not test_dir.exists():
        test_dir.mkdir()
        logger.warning(f"Created test directory: {test_dir}")
        logger.info("Please add test resume files to the 'test_resumes' directory.")
        return
    
    # Expected file types
    file_types = {
        '.pdf': FileType.PDF,
        '.docx': FileType.DOCX,
        '.odt': FileType.ODT,
        '.rtf': FileType.RTF,
        '.txt': FileType.TXT,
        '.jpg': FileType.IMAGE,
        '.jpeg': FileType.IMAGE,
        '.png': FileType.IMAGE,
    }
    
    # Find test files
    test_files = []
    for ext in file_types:
        test_files.extend(list(test_dir.glob(f"*{ext}")))
    
    if not test_files:
        logger.warning("No test files found in the 'test_resumes' directory.")
        logger.info("Please add some test resume files with extensions: " + ", ".join(file_types.keys()))
        return
    
    # Run tests
    logger.info(f"Found {len(test_files)} test files")
    results = []
    
    for file_path in test_files:
        expected_type = file_types.get(file_path.suffix.lower(), FileType.UNKNOWN)
        success, message = test_parse_resume(str(file_path), expected_type)
        results.append((file_path.name, success, message))
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print(f"\nPassed: {success_count}/{total_count} tests")
    
    # Print detailed results
    for filename, success, message in results:
        status = "PASS" if success else "FAIL"
        print(f"\n[{status}] {filename}")
        print(f"  {message}")
    
    # Exit with appropriate status code
    if success_count == total_count:
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print(f"\n{total_count - success_count} tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
