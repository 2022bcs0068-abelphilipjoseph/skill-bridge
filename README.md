# 🎓 Skill-Bridge: Career Navigator MVP


## Overview
Skill-Bridge is an AI-powered Career Navigator designed to bridge the gap between a candidate's current skills and their target role. Built for MVP constraint, it features real-time resume parsing, AI-driven gap analysis, personalized learning roadmaps, and a gamified mock-interview module.

## Core Features
- **In-Memory Resume Parsing:** Extracts text from PDF/TXT files dynamically without writing to disk, ensuring zero PII leakage.
- **Gemini 3.0 Flash Integration:** Utilizes Google's latest `google-genai` SDK with strict Pydantic schemas (Structured Outputs) for deterministic, JSON-only responses.
- **Interactive Progress Tracker:** Uses Streamlit `session_state` to allow users to manually track their upskilling journey (Yet to Start -> Highly Skilled) within a single session.
- **Mock Interview Pivot:** Dynamically generates challenging, scenario-based interview questions based *only* on the candidate's verified skills.
- **Robust Fallback Mechanism:** Gracefully degrades to a Rule-Based Fallback algorithm if the AI API rate-limits, fails, or is unavailable, ensuring the UI never crashes.

## Quick Start Guide
1. **Clone & Setup:**
   ```bash
   git clone https://github.com/2022bcs0068-abelphilipjoseph/skill-bridge
   cd skill-bridge
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Rename .env.example to .env and add your Google AI Studio API Key:
   ```bash 
   GEMINI_API_KEY=your_api_key_here 
   ```


3. Generate Synthetic Data:
   ```bash
   python generate_data.py
   ```


4. Run the App:
   ```bash
   streamlit run app.py
   ```

5. Run Tests:
   ```bash
   pytest test_app.py
   ```

## Architecture & Design Tradeoffs 
### Key Higlights of MVP:
- **Stateless vs. Stateful:** The MVP uses Streamlit's session_state to manage the UI dashboard without requiring a database. This prioritizes speed of delivery and core logic testing over complex authentication routing.
- **Data Safety (No Scraping):** Adhering to prompt constraints, live job boards were not scraped. A synthetic data generator (generate_data.py) creates realistic job profiles.
- **Memory Management:-** Resume PDFs are processed entirely in memory via pypdf. In a production environment, strict pre-processing (5MB limit, <5 pages) and virus scanning would be implemented to protect server RAM and optimize LLM token usage.

## Phase 2: Future Enhancements 

- **Firebase Authentication:** Implementing a secure login wall so users have a persistent "Skills Profile".
- **Firestore NoSQL Database:** Migrating away from stateless sessions. The app would push/pull the user's generated learning roadmap and skill statuses (Basic -> Highly Skilled) to a database, tracking their journey over months.
- **Interactive Gamified Quizzer:** Upgrading the single Mock Interview question into a dynamic, endless batch quiz generator with score tracking to rigorously test verified skills.



