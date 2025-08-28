# Cavro - AI Resume Agent

Cavro is an AI-powered Resume Agent that helps candidates:
- Parse resumes (PDF/DOCX/TXT)
- Score resumes for ATS (Applicant Tracking Systems)
- Match resumes against job descriptions
- Rewrite bullet points with AI (Gemini, OpenAI, HuggingFace)
- Suggest improvements, career paths, and interview prep
- Provide mock blockchain verification for resumes

## 🚀 Tech Stack
- **Frontend:** Streamlit (Porcelain + Lapins theme)
- **AI APIs:** Gemini / OpenAI / HuggingFace
- **Python Libraries:** PyPDF2, python-docx, reportlab, transformers

## 📂 Project Structure
```
cavro/
    app.py
    modules/
    config/
    assets/
    data/
    logs/
    ...
```

## ▶️ Run Locally

1. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

2. **Set up environment variables**
    - Copy `.env` and add your API keys for Gemini, OpenAI, and HuggingFace.

3. **Start the app**
    ```sh
    streamlit run app.py
    ```

## 🛠 Features

- **Resume Parsing:** Extracts text and metadata from PDF, DOCX, and TXT resumes.
- **ATS Scoring:** Evaluates resume formatting and keyword optimization.
- **Job Match:** Compares resume against job descriptions for keyword overlap.
- **AI Rewriting:** Improves resume bullet points using Gemini, OpenAI, or HuggingFace.
- **Career Suggestions:** Recommends career paths based on skills and experience.
- **Interview Prep:** Generates tailored interview questions.
- **Blockchain Verification:** Mock verification for resume authenticity.

## 📄 License

This project is for educational and personal use. Do not share API keys or sensitive data.

---

*Made with ❤️ by Cavro AI • Empowering your
