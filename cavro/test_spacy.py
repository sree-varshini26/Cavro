import spacy

try:
    print("Loading spaCy model...")
    nlp = spacy.load('en_core_web_sm')
    print("Successfully loaded spaCy model!")
    print(f"spaCy version: {spacy.__version__}")
    print(f"Model version: {nlp.meta['version']}")
except Exception as e:
    print(f"Error loading spaCy model: {str(e)}")
    print("\nTrying to download the model...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("Model downloaded successfully!")
    except Exception as e2:
        print(f"Failed to download model: {str(e2)}")
