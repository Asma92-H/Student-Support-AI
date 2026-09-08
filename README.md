# Student Support AI

## Project Overview
An intelligent, local-first AI assistant designed to help students get instant and accurate answers regarding their academic details,
FAQs, notices, regulations, and syllabus. It runs completely offline using local models to ensure data privacy and reliable performance.

## Key Features
- **Smart RAG System:** Retrieves precise information directly from structured JSON data files (`faqs.json`, `syllabus.json`, `notices.json`, `regulations.json`).
- **Custom Tools:** Integrated with dynamic calculators and utility functions to handle data computation seamlessly.
- **SQLite Memory:** Maintains conversational history and context locally using a lightweight SQLite database (`student_memory.db`).
- **Ollama Integration:** Powered by local LLMs (Phi3) to process natural language queries without triggering refusal guardrails on sensitive-looking student metrics.

## Future Enhancements
- Implementing multi-user authentication and role-based access for faculty and students.
- Expanding the RAG knowledge base to include real-time timetable updates and exam hall allocations.
- Adding a web-based graphical user interface (GUI) alongside the current terminal setup for enhanced user experience.

---

Developed as part of IBM Internship Program

By Asma H
