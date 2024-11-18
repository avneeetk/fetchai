# FetchAI: Information Retrieval Agent

## Overview
AI-powered information extraction tool leveraging Google Sheets, SerpAPI, and Groq LLM.

## Features
- Multi-source data loading (CSV/Google Sheets)
- Web search extraction
- AI-powered information processing
- Exportable results

## Setup

### Prerequisites
- Python 3.8+
- Google Cloud Project
- SerpAPI Key
- Groq API Key

### Installation
```bash
# Clone Repository
git clone <https://github.com/avneeetk/fetchai>

# Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration
1. Google Cloud Credentials
   - Create service account
   - Download JSON key
   - Place in project root

2. API Keys
   - SerpAPI: serpapi.com
   - Groq: groq.com

## Usage
```bash
streamlit run app.py
```

## Security Notes
- Never commit sensitive files
- Rotate API keys regularly
- Use environment variables
