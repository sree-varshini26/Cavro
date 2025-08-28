import os
import re
import logging
import unicodedata
import tempfile
import mimetypes
import traceback
from typing import Union, Optional, Tuple, BinaryIO, List, Dict, Any
from pathlib import Path
from io import BytesIO, StringIO
from enum import Enum, auto
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from io import BytesIO, StringIO
from typing import Dict, List, Optional, Tuple, Union, BinaryIO, Any
from dataclasses import dataclass

# Third-party imports (with fallbacks)
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    import docx2txt
    DOCX2TXT_AVAILABLE = True
except ImportError:
    DOCX2TXT_AVAILABLE = False

try:
    import odf.opendocument
    import odf.text
    ODFPY_AVAILABLE = True
except ImportError:
    ODFPY_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

# Configure logging with more detailed format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
LOG_LEVEL = logging.INFO

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/resume_parser.log', encoding='utf-8')
    ]
)

# Module logger
logger = logging.getLogger('resume_parser')
logger.setLevel(LOG_LEVEL)

class FileType(Enum):
    """Supported file types for resume parsing."""
    PDF = auto()
    DOCX = auto()
    ODT = auto()
    RTF = auto()
    TXT = auto()
    IMAGE = auto()
    UNKNOWN = auto()

@dataclass
class ResumeMetadata:
    """Metadata extracted from a resume."""
    file_type: Optional[FileType] = None
    file_size: Optional[int] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[List[str]] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

class ResumeParserError(Exception):
    """
    Custom exception for resume parsing errors.
    
    Attributes:
        message: Error message
        details: Optional additional error details
        original_exception: Original exception that caused this error
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        self.message = message
        self.details = details or {}
        self.original_exception = original_exception
        
        # Add traceback if available
        if original_exception:
            self.details['traceback'] = traceback.format_exc()
        
        super().__init__(self.message)
    
    def __str__(self) -> str:
        error_str = self.message
        if self.details:
            error_str += f"\nDetails: {self.details}"
        if self.original_exception:
            error_str += f"\nOriginal error: {str(self.original_exception)}"
        return error_str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for serialization."""
        return {
            'message': self.message,
            'details': self.details,
            'type': self.__class__.__name__
        }

def detect_file_type(file_obj: BytesIO, file_extension: str) -> FileType:
    """Detect the file type based on content and extension."""
    try:
        # Save current position
        current_pos = file_obj.tell()
        
        # Try to read magic numbers
        magic = file_obj.read(8)
        file_obj.seek(current_pos)  # Reset position
        
        # PDF
        if magic and magic.startswith(b'%PDF-'):
            return FileType.PDF
            
        # Check for ZIP-based formats (DOCX, ODT)
        if magic and magic.startswith(b'PK\x03\x04'):
            content = file_obj.read(1024)
            file_obj.seek(current_pos)  # Reset position
            
            if b'word/document.xml' in content:
                return FileType.DOCX
            elif b'mimetype' in content:
                return FileType.ODT
        
        # RTF
        if magic and magic.startswith(b'{\\rtf'):
            return FileType.RTF
            
    except Exception as e:
        logger.warning(f"Error detecting file type from content: {str(e)}")
        file_obj.seek(0)  # Ensure we reset position on error
    
    # Fall back to extension if content detection fails or file is not seekable
    if file_extension:
        file_extension = file_extension.lower().lstrip('.')
        if file_extension == 'pdf':
            return FileType.PDF
        elif file_extension in ('docx', 'docm'):
            return FileType.DOCX
        elif file_extension == 'odt':
            return FileType.ODT
        elif file_extension == 'rtf':
            return FileType.RTF
        elif file_extension in ('txt', 'md'):
            return FileType.TXT
        elif file_extension in ('png', 'jpg', 'jpeg', 'tiff', 'bmp'):
            return FileType.IMAGE
    
    return FileType.UNKNOWN

def extract_metadata(file_obj: BytesIO, file_type: FileType) -> ResumeMetadata:
    """
    Extract metadata from the file based on its type.
    
    Args:
        file_obj: File-like object containing the resume
        file_type: Type of the file
        
    Returns:
        ResumeMetadata object with extracted metadata
        
    Raises:
        ResumeParserError: If there's an error extracting metadata
    """
    logger.debug(f"Extracting metadata for file type: {file_type}")
    metadata = ResumeMetadata()
    metadata.file_type = file_type
    
    try:
        # Save current position to restore later
        original_position = file_obj.tell()
        
        # Extract metadata based on file type
        if file_type == FileType.PDF:
            try:
                import fitz  # PyMuPDF
                
                # Get file content
                file_content = file_obj.getvalue()
                if not file_content:
                    logger.warning("Empty file content when extracting PDF metadata")
                    return metadata
                    
                # Open PDF document
                try:
                    doc = fitz.open(stream=file_content, filetype='pdf')
                except Exception as e:
                    logger.warning(f"Failed to open PDF with PyMuPDF: {str(e)}")
                    return metadata
                
                # Extract metadata
                with doc:  # Ensures the document is properly closed
                    metadata.page_count = len(doc)
                    if doc.metadata:
                        meta = doc.metadata
                        if meta.get('title'):
                            metadata.title = meta['title']
                        if meta.get('author'):
                            metadata.author = meta['author']
                        if meta.get('subject'):
                            metadata.subject = meta['subject']
                        if meta.get('keywords'):
                            keywords = meta['keywords']
                            if isinstance(keywords, str):
                                metadata.keywords = [k.strip() for k in keywords.split(',') if k.strip()]
                            elif isinstance(keywords, (list, tuple)):
                                metadata.keywords = [str(k).strip() for k in keywords if k and str(k).strip()]
                
                logger.debug(f"Extracted PDF metadata: {metadata}")
                
            except ImportError:
                logger.warning("PyMuPDF not available for PDF metadata extraction")
                
        # Add size in bytes
        file_obj.seek(0, 2)  # Seek to end
        metadata.file_size = file_obj.tell()
        file_obj.seek(original_position)  # Reset position
        
        logger.info(f"Successfully extracted metadata: {metadata}")
        
    except Exception as e:
        error_msg = f"Failed to extract metadata: {str(e)}"
        logger.error(error_msg, exc_info=True)
        # Don't raise here, just log and return what we have
        
    return metadata

def parse_resume(
    file_path: Union[str, BinaryIO, BytesIO], 
    file_extension: Optional[str] = None,
    extract_metadata_flag: bool = True,
    clean_text: bool = True
) -> Tuple[str, Optional[ResumeMetadata]]:
    """
    Parse a resume file and extract its text content and metadata.
    
    Args:
        file_path: Path to the resume file or file-like object (str, Path, or file-like)
        file_extension: Optional file extension if not inferrable from file_path
        extract_metadata: Whether to extract and return metadata
        clean_text: Whether to clean and normalize the extracted text
        
    Returns:
        Tuple of (extracted_text, metadata)
        
    Raises:
        ResumeParserError: If the file cannot be parsed or format is unsupported
    """
    file_obj = None
    metadata = None
    
    try:
        # Handle file-like objects (including BytesIO and Streamlit UploadedFile)
        if hasattr(file_path, 'read'):
            # Save the original file position if seekable
            original_pos = file_path.tell() if hasattr(file_path, 'seekable') and file_path.seekable() else 0
            
            # Get file extension from the name if available
            if hasattr(file_path, 'name') and file_path.name:
                file_extension = os.path.splitext(file_path.name)[1].lstrip('.').lower()
            
            # If no extension from name, use the provided one or raise error
            if not file_extension and not file_extension:
                raise ResumeParserError(
                    "Could not determine file type. "
                    "Please provide a file with a valid extension or specify the file_extension parameter."
                )
            
            # Read the content
            try:
                content = file_path.getvalue() if hasattr(file_path, 'getvalue') else file_path.read()
                if not content:
                    raise ResumeParserError("The uploaded file is empty")
                file_obj = BytesIO(content)
            except Exception as e:
                raise ResumeParserError(f"Error reading file content: {str(e)}")
            finally:
                # Reset the original file position if possible
                if hasattr(file_path, 'seek') and callable(file_path.seek):
                    try:
                        file_path.seek(original_pos)
                    except Exception:
                        pass
        
        # Handle file paths (string or Path object)
        elif isinstance(file_path, (str, Path)):
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            # Get file extension from path if not provided
            file_extension = file_extension or path.suffix.lstrip('.')
            if not file_extension:
                raise ResumeParserError(
                    "Could not determine file type from path. "
                    "Please provide a file with a valid extension or specify the file_extension parameter."
                )
            
            # Read file content
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                if not content:
                    raise ResumeParserError(f"File is empty: {path}")
                file_obj = BytesIO(content)
            except Exception as e:
                raise ResumeParserError(f"Error reading file {path}: {str(e)}")
        
        else:
            raise ResumeParserError(
                "Invalid file input. "
                "Expected file path (str or Path) or file-like object with read() method."
            )
        
        # At this point, we should have a valid file_obj
        if not file_obj:
            raise ResumeParserError("Failed to initialize file object")
            
        # Reset file position to start
        file_obj.seek(0)
        
        # Detect file type
        try:
            file_type = detect_file_type(file_obj, file_extension)
            if file_type == FileType.UNKNOWN:
                raise ResumeParserError(
                    f"Unsupported or unrecognized file format: {file_extension}. "
                    f"Supported formats: PDF, DOCX, ODT, RTF, TXT, and common image formats"
                )
        except Exception as e:
            raise ResumeParserError(f"Error detecting file type: {str(e)}")
        
        # Reset file position before parsing
        file_obj.seek(0)
        
        # Extract metadata if requested
        if extract_metadata_flag:
            try:
                metadata = extract_metadata(file_obj, file_type)
                file_obj.seek(0)  # Reset position after metadata extraction
            except Exception as e:
                logger.warning(f"Error extracting metadata: {str(e)}")
                metadata = ResumeMetadata()
        
        # Parse based on file type
        text = ""
        try:
            if file_type == FileType.PDF:
                text = _parse_pdf(file_obj) or ""
            elif file_type == FileType.DOCX:
                text = _parse_docx(file_obj) or ""
            elif file_type == FileType.ODT:
                text = _parse_odt(file_obj) or ""
            elif file_type == FileType.RTF:
                text = _parse_rtf(file_obj) or ""
            elif file_type == FileType.TXT:
                text = content.decode('utf-8', errors='replace')
            elif file_type == FileType.IMAGE:
                text = _parse_image(file_obj, file_extension) or ""
            
            if not text.strip():
                raise ResumeParserError("No text could be extracted from the file")
                
        except ResumeParserError:
            raise  # Re-raise our custom errors
        except Exception as e:
            raise ResumeParserError(f"Error parsing {file_type.name} file: {str(e)}")
        
        # Clean the text if requested
        if clean_text and text:
            try:
                text = clean_resume_text(text)
            except Exception as e:
                logger.warning(f"Error cleaning text: {str(e)}")
                # Continue with uncleaned text rather than failing
        
        return text, metadata
        
    except ResumeParserError:
        raise  # Re-raise our custom errors
    except Exception as e:
        raise ResumeParserError(f"Failed to process resume: {str(e)}")
    finally:
        # Ensure file objects are properly closed
        if file_obj and hasattr(file_obj, 'close'):
            try:
                file_obj.close()
            except Exception as e:
                logger.warning(f"Error closing file object: {str(e)}")

def _parse_pdf(file_obj: Union[BytesIO, BinaryIO]) -> str:
    """
    Parse PDF file and extract text with multiple fallback mechanisms.
    
    This function tries multiple methods to extract text from PDFs in order of reliability:
    1. PyMuPDF (fitz) - Most reliable for most PDFs
    2. PyPDF2 - Fallback for simple PDFs
    3. OCR with pdf2image and Tesseract - For scanned PDFs
    
    Args:
        file_obj: File-like object containing the PDF data
        
    Returns:
        Extracted text from the PDF
        
    Raises:
        ResumeParserError: If text extraction fails with all available methods
    """
    text = ""
    errors = []
    
    # Reset file pointer to start
    if hasattr(file_obj, 'seek'):
        file_obj.seek(0)
    
    # Get file data as bytes for methods that need it
    file_data = file_obj.read() if hasattr(file_obj, 'read') else b''
    if hasattr(file_obj, 'seek'):
        file_obj.seek(0)
    
    # Method 1: Try PyMuPDF first (most reliable for most PDFs)
    if FITZ_AVAILABLE:
        try:
            doc = fitz.open(stream=file_obj.getvalue(), filetype="pdf")
            text = ""
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text.strip():
                        text += page_text + "\n"
                except Exception as page_error:
                    logger.warning(f"Error on page {page_num + 1}: {str(page_error)}")
                    continue
            
            # If we got some text, return it
            if text.strip():
                logger.info("Successfully extracted text using PyMuPDF")
                return text.strip()
            else:
                logger.warning("PyMuPDF extracted empty text, trying next method...")
                
        except Exception as e:
            logger.warning(f"PyMuPDF text extraction failed: {str(e)}")
            # Continue to next method
    else:
        logger.warning("PyMuPDF not available, trying next method...")
    
    # Method 2: Fallback to PyPDF2
    if PyPDF2:
        try:
            # Create a new BytesIO for PyPDF2
            pdf_io = BytesIO(file_data) if file_data else file_obj
            if hasattr(pdf_io, 'seek'):
                pdf_io.seek(0)
                
            pdf_reader = PyPDF2.PdfReader(pdf_io)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:  # Only add non-empty text
                    text += page_text + "\n"
                    
            if text.strip():
                return text.strip()
                
        except Exception as e:
            error_msg = f"PyPDF2 failed: {str(e)}"
            errors.append(error_msg)
            logging.warning(error_msg)
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
    
    # Method 3: Try using pdfminer.six for text extraction
    try:
        from io import StringIO
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        
        # Reset file pointer
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
            
        # Extract text using pdfminer.six
        output_string = StringIO()
        laparams = LAParams()
        extract_text_to_fp(file_obj, output_string, laparams=laparams)
        text = output_string.getvalue()
        
        if text.strip():
            return text.strip()
            
    except ImportError as e:
        error_msg = "pdfminer.six is not available for PDF processing"
        errors.append(error_msg)
        logging.warning(error_msg)
    except Exception as e:
        error_msg = f"PDF processing with pdfminer.six failed: {str(e)}"
        errors.append(error_msg)
        logging.warning(error_msg)
        
        # Fallback to PyPDF2 if pdfminer.six fails
        try:
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)  # Reset file pointer
            reader = PyPDF2.PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text.strip()
        except Exception as e2:
            error_msg = f"Fallback PDF processing also failed: {str(e2)}"
            errors.append(error_msg)
            logging.warning(error_msg)
    
    # Method 4: OCR fallback for scanned PDFs
    if not text.strip():
        error_messages = []
        
        # Check if we have the required OCR dependencies
        ocr_available = True
        missing_deps = []
        
        if not TESSERACT_AVAILABLE:
            missing_deps.append("pytesseract")
        if not FITZ_AVAILABLE:
            missing_deps.append("PyMuPDF")
        if not PDF2IMAGE_AVAILABLE:
            missing_deps.append("pdf2image")
        
        if missing_deps:
            logger.warning(f"Skipping OCR - Missing dependencies: {', '.join(missing_deps)}")
            ocr_available = False
        
        # Only attempt OCR if we have the required dependencies
        if ocr_available:
            # Try OCR with PyMuPDF rendering first
            if FITZ_AVAILABLE and TESSERACT_AVAILABLE:
                try:
                    doc = fitz.open(stream=file_data, filetype="pdf")
                    text = ""
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        # Try to extract text first
                        page_text = page.get_text()
                        if not page_text.strip():
                            # If no text, try OCR
                            try:
                                pix = page.get_pixmap()
                                img_data = pix.tobytes("png")
                                page_text = _extract_text_with_ocr(img_data, "png") or ""
                            except Exception as ocr_error:
                                logger.warning(f"OCR on page {page_num + 1} failed: {str(ocr_error)}")
                                continue
                        text += page_text + "\n\n"
                    
                    if text.strip():
                        logger.info("Successfully extracted text using OCR with PyMuPDF rendering")
                        return text.strip()
                        
                except Exception as e:
                    error_msg = f"OCR via PyMuPDF rendering failed: {str(e)}"
                    if "tesseract" in str(e).lower():
                        error_msg += ". tesseract is not installed or it's not in your PATH. See README file for more information."
                    error_messages.append(error_msg)
                    logger.warning(error_msg)
            
            # Fallback to pdf2image if available
            if PDF2IMAGE_AVAILABLE and TESSERACT_AVAILABLE and not text.strip():
                try:
                    # Allow configuring poppler path via env var on Windows
                    poppler_path = os.environ.get("POPPLER_PATH")
                    if poppler_path:
                        images = convert_from_bytes(file_data, poppler_path=poppler_path)
                    else:
                        images = convert_from_bytes(file_data)
                    text = ""
                    for img in images:
                        try:
                            img_byte_arr = BytesIO()
                            img.save(img_byte_arr, format='PNG')
                            img_byte_arr = img_byte_arr.getvalue()
                            ocr_text = _extract_text_with_ocr(img_byte_arr, "png")
                            if ocr_text:
                                text += ocr_text + "\n\n"
                        except Exception as img_error:
                            logger.warning(f"OCR on image failed: {str(img_error)}")
                            continue
                    
                    if text.strip():
                        logger.info("Successfully extracted text using OCR with pdf2image")
                        return text.strip()
                        
                except Exception as e:
                    error_msg = f"OCR via pdf2image failed: {str(e)}"
                    if "poppler" in str(e).lower():
                        error_msg += ". Is poppler installed and in PATH? You can set POPPLER_PATH env var to the bin folder."
                    error_messages.append(error_msg)
                    logger.warning(error_msg)
        
        # If we tried OCR methods but they failed, provide helpful error message
        if error_messages:
            logger.warning(" | ".join(error_messages))
            
        # If we get here, all OCR attempts failed or were skipped
        if not text.strip():
            logger.warning("No text could be extracted from the PDF with available methods")
            return ""
    
    # Final failure with aggregated error details
    raise ResumeParserError(
        "Failed to extract text from PDF with all available methods",
        details={"methods_errors": errors}
    )

def _parse_docx(file_obj: Union[BytesIO, BinaryIO]) -> str:
    """Parse DOCX file and extract text."""
    if not DOCX2TXT_AVAILABLE:
        raise ResumeParserError("docx2txt is not installed. Install with: pip install docx2txt")
    
    try:
        # Handle both BytesIO and file-like objects
        if hasattr(file_obj, 'getvalue'):
            content = file_obj.getvalue()
        else:
            current_pos = file_obj.tell()
            content = file_obj.read()
            file_obj.seek(current_pos)  # Reset position
        
        # Save to temp file for docx2txt
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            text = docx2txt.process(tmp_file_path)
            return text
        finally:
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass
    except Exception as e:
        raise ResumeParserError(f"Failed to parse DOCX: {str(e)}")

def _parse_odt(file_obj: Union[BytesIO, BinaryIO]) -> str:
    """Parse ODT file and extract text."""
    if not ODFPY_AVAILABLE:
        raise ImportError("odfpy is required for parsing ODT files")
    
    try:
        # Handle both BytesIO and file-like objects
        if hasattr(file_obj, 'getvalue'):
            content = file_obj.getvalue()
        else:
            current_pos = file_obj.tell()
            content = file_obj.read()
            file_obj.seek(current_pos)  # Reset position
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.odt') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            doc = odf.opendocument.load(temp_file_path)
            text_parts = []
            
            # Extract text from all paragraphs
            for item in doc.getElementsByType(odf.text.P):
                text_parts.append(str(item))
            
            return '\n'.join(text_parts)
        finally:
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
    except Exception as e:
        raise ResumeParserError(f"Failed to parse ODT: {str(e)}")

def _parse_rtf(file_obj: Union[BytesIO, BinaryIO]) -> str:
    """Parse RTF file and extract text."""
    try:
        # Handle both BytesIO and file-like objects
        if hasattr(file_obj, 'getvalue'):
            content = file_obj.getvalue()
        else:
            current_pos = file_obj.tell()
            content = file_obj.read()
            file_obj.seek(current_pos)  # Reset position
        
        # Simple RTF to text conversion (basic implementation)
        if isinstance(content, bytes):
            rtf_text = content.decode('utf-8', errors='ignore')
        else:
            rtf_text = content
            
        # Remove RTF control sequences (very basic)
        text = re.sub(r'\\.*?[\\{}]|[{}\\]', '', rtf_text)
        # Remove excessive whitespace
        text = ' '.join(text.split())
        return text
    except Exception as e:
        raise ResumeParserError(f"Failed to parse RTF: {str(e)}")

def _parse_image(file_obj: Union[BytesIO, BinaryIO], file_extension: str) -> str:
    """Extract text from an image using OCR."""
    if not TESSERACT_AVAILABLE:
        raise ResumeParserError("Tesseract OCR is not available. Install with: pip install pytesseract")
    
    try:
        # Handle both BytesIO and file-like objects
        if hasattr(file_obj, 'getvalue'):
            content = file_obj.getvalue()
        else:
            current_pos = file_obj.tell()
            content = file_obj.read()
            file_obj.seek(current_pos)  # Reset position
            
        return _extract_text_with_ocr(content, file_extension)
    except Exception as e:
        raise ResumeParserError(f"Failed to extract text from image: {str(e)}")

def _extract_text_with_ocr(image_data: bytes, file_extension: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    import tempfile
    import os
    
    # Ensure file_extension starts with a dot
    if not file_extension.startswith('.'):
        file_extension = f'.{file_extension}'
    
    # Create a temporary file with the correct extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(image_data)
    
    try:
        # Use pytesseract to extract text
        from PIL import Image
        img = Image.open(temp_file_path)
        # Configure tesseract path
        tesseract_cmd = os.environ.get("TESSERACT_PATH")
        if not tesseract_cmd and os.name == "nt":
            # Fallback to common Windows install location
            default_tess = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
            if os.path.exists(default_tess):
                tesseract_cmd = default_tess
        if tesseract_cmd:
            try:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
                logger.info(f"Using Tesseract at: {tesseract_cmd}")
            except Exception as cfg_err:
                logger.warning(f"Failed to set Tesseract path: {cfg_err}")
        # Use Tesseract with a general model and layout mode that works well for resumes
        text = pytesseract.image_to_string(img, lang="eng", config="--oem 3 --psm 6")
        return text
    except Exception as e:
        raise ResumeParserError(f"Failed to extract text with OCR: {str(e)}")
    finally:
        # Clean up the temporary file
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")

def clean_resume_text(text: str) -> str:
    """
    Clean and normalize the extracted resume text.
    
    This function performs several cleaning operations:
    1. Removes HTML/CSS tags and scripts
    2. Removes excessive whitespace and normalizes it
    3. Filters out non-printable characters
    4. Normalizes unicode characters
    5. Removes common resume section headers
    6. Removes email addresses and URLs
    7. Cleans up special characters
    
    Args:
        text: Raw extracted text from resume
        
    Returns:
        str: Cleaned and normalized text
        
    Raises:
        ValueError: If input is not a string
    """
    logger.debug("Starting text cleaning")
    
    # Input validation
    if not text:
        logger.warning("Empty text provided to clean_resume_text")
        return ""
        
    if not isinstance(text, str):
        error_msg = f"Expected string for text cleaning, got {type(text).__name__}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Log original text length for debugging
        original_length = len(text)
        
        # 1. Remove HTML/CSS content
        # Remove entire style and script tags with content
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove all HTML tags but keep their content
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove inline CSS styles
        text = re.sub(r'style="[^"]*"', '', text)
        # Remove HTML entities
        text = re.sub(r'&[a-z0-9]+;', ' ', text)
        
        # 2. Normalize whitespace and clean up text
        # Replace multiple spaces, newlines, tabs with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # 3. Remove non-printable characters except for common ones
        text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
        
        # 4. Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # 5. Remove common resume section headers (case insensitive)
        section_headers = [
            r'\b(?:personal\s+details?|contact\s+info(?:rmation)?|summary|experience|education|skills|projects|certifications|awards|publications|languages|interests|references)\b',
            r'\b(?:work\s+history|employment\s+history|professional\s+experience|academic\s+background)\b',
            r'\b(?:technical\s+skills|soft\s+skills|programming\s+languages|frameworks|tools)\b',
            r'\b(?:name|address|phone|email|linkedin|github|portfolio)\s*:.*?(?=\n\s*\n|$)',
            r'\b(?:page\s*\d+|confidential|resume|cv|curriculum vitae)\b',
        ]
        
        for pattern in section_headers:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 6. Remove email addresses and URLs
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)  # emails
        text = re.sub(r'https?://\S+|www\.\S+', '', text)  # URLs
        
        # 7. Clean up special characters but keep common ones used in text
        # Keep common punctuation and symbols used in resumes
        keep_chars = "'@#%&*+=-/\\"
        text = re.sub(f'[^\w\s{re.escape(keep_chars)}]', ' ', text)
        
        # Normalize whitespace again after cleaning
        text = ' '.join(text.split())
        
        # Log cleaning results
        cleaned_length = len(text)
        logger.debug(
            f"Text cleaning complete. Original length: {original_length}, "
            f"Cleaned length: {cleaned_length}, "
            f"Removed: {original_length - cleaned_length} characters"
        )
        
        return text.strip()
        
    except Exception as e:
        error_msg = f"Error cleaning resume text: {str(e)}"
        logger.error(error_msg, exc_info=True)
        # Return original text if cleaning fails, but still clean basic HTML
        if text:
            text = re.sub(r'<[^>]+>', ' ', text)  # Basic HTML tag removal as fallback
            return text.strip()
        return ""
