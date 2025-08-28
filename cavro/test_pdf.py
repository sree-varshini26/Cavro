import sys
from PyPDF2 import PdfReader

def test_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            print(f"Number of pages: {len(reader.pages)}")
            
            # Try to read first page
            if reader.pages:
                page = reader.pages[0]
                text = page.extract_text()
                print(f"First 200 chars of text: {text[:200]}")
                return True
            return False
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_pdf(sys.argv[1])
    else:
        print("Please provide a PDF file path")
