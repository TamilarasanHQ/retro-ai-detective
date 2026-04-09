# Retro AI Detective Architecture

## Overview
Retro AI Detective is a browser-based interrogation game built with a Python Flask backend and a static HTML/CSS/JavaScript frontend. Players question three AI suspects in a green-screen retro terminal UI to discover the hidden killer.

## Tech Stack
- Backend: Python 3, Flask, Flask-CORS, Requests
- AI Logic: OpenRouter API via `OPENROUTER_API_KEY`
- Frontend: HTML, CSS, JavaScript
- Hosting: Backend on Render, Frontend on Vercel

## Data Flow
1. The player opens the frontend in the browser.
2. Frontend JavaScript sends a request to `/start` to create a new game session.
3. The backend initializes three suspects and randomly assigns one killer.
4. The player selects a suspect and asks a question.
5. The frontend sends `/interrogate` with `game_id`, `suspect_id`, and the question.
6. Backend uses OpenRouter to generate an AI response based on suspect role and question.
7. The backend analyzes the answer for contradiction and suspicion keywords.
8. The backend returns the suspect response, updated history, and suspicion scores.
9. The player can accuse one suspect via `/accuse` to determine if they found the killer.

## State Management
- Game state is stored in-memory in the backend.
- Each game session is assigned a unique `game_id`.
- Game state includes suspect profiles, chat history, and suspicion scores.

## Suspicion & Contradiction Logic
- Keyword-based tracking detects suspicious phrases such as "I didn't", "actually", "never", and crime-related terms.
- The suspicion meter updates after each interrogation.
- Correct accusations are validated against the hidden killer.

## Deployment Notes
- Backend dependencies are listed in `backend/requirements.txt`.
- Frontend is static and can be served directly from Vercel.
- Set `OPENROUTER_API_KEY` in Render environment variables for the backend.
