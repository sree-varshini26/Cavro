import os
from io import BytesIO
from modules.resume_parser import parse_resume

# Path to the sample resume
test_file_path = "data/sample_resume.pdf"

try:
    # Read the file
    with open(test_file_path, "rb") as f:
        file_content = f.read()
        file_obj = BytesIO(file_content)
        file_extension = os.path.splitext(test_file_path)[1].lstrip('.')
        
        # Parse the resume
        print(f"Parsing {test_file_path}...")
        resume_text, metadata = parse_resume(file_obj, file_extension=file_extension)
        
        # Print the first 500 characters of the extracted text
        print("\n" + "="*50)
        print("EXTRACTED TEXT (first 500 chars):")
        print("-" * 50)
        print(resume_text[:500] + "...")
        
        # Print metadata
        print("\n" + "="*50)
        print("METADATA:")
        print("-" * 50)
        for field, value in vars(metadata).items():
            if value:  # Only print non-None values
                print(f"{field}: {value}")
                
except FileNotFoundError:
    print(f"Error: Could not find file at {test_file_path}")
    print("Please make sure the file exists at the specified path.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
