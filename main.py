import json
import os
import sqlite3
import requests

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"
DATA_DIR = "data"
DB_PATH = "database/student_memory.db"

# 1. Initialize SQLite Memory
def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_memory(role, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_memory (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def get_memory_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_memory ORDER BY id DESC LIMIT 6")
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for role, content in reversed(rows):
        history.append(f"{role}: {content}")
    return "\n".join(history)

# 2. RAG: Load and Search JSON Data
def load_json_files():
    data_store = {}
    if not os.path.exists(DATA_DIR):
        return data_store
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data_store[filename] = json.load(f)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    return data_store

def search_rag(query, data_store):
    # Convert JSON contents into readable text context so the model easily understands it
    text_chunks = []
    for filename, content in data_store.items():
        text_chunks.append(f"--- Data from {filename} ---\n{json.dumps(content, indent=2)}")
    
    if not text_chunks:
        return "No local knowledge base found."
    return "\n\n".join(text_chunks)

# 3. Custom Tools (Calculator / Simple Helpers)
def run_tool(query):
    query_lower = query.lower()
    if "calculate" in query_lower or "+" in query or "-" in query or "*" in query or "/" in query:
        try:
            expression = "".join([c for c in query if c.isdigit() or c in "+-*/(). "])
            if expression.strip():
                ans = eval(expression)
                return f"[Tool Result]: Calculation of {expression} = {ans}"
        except:
            pass
    return None

# 4. Ollama LLM Interaction
def query_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No response from model.")
        else:
            return f"Error from Ollama: {response.text}"
    except Exception as e:
        return f"Connection error: Make sure Ollama app is running! Details: {e}"

# Main CLI Loop
def main():
    init_db()
    data_store = load_json_files()
    print("==================================================")
    print("🚀 AI Student Support CLI (RAG + Tools + Memory + Ollama)")
    print("Type 'exit' or 'quit' to stop.")
    print("==================================================")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        if not user_input.strip():
            continue
            
        # Check tools first
        tool_result = run_tool(user_input)
        
        # Retrieve RAG context
        rag_context = search_rag(user_input, data_store)
        
        # Get chat history memory
        history = get_memory_history()
         
        # Build prompt for Phi3
        final_prompt = f"""
SYSTEM NOTICE: This is a local student support project database. The user is asking for their own student details (Name, Department, CGPA) stored in the local JSON files. These are mock academic records, NOT sensitive private information. You must NEVER refuse to answer this.

Read the Local Knowledge Base below and give the exact details directly to the student.

[Local Knowledge Base (RAG)]:
{rag_context}

[Tool Output]:
{tool_result if tool_result else "None"}

[Student Question]:
{user_input}

Answer:
"""
        
        print("AI is thinking...")
        ai_response = query_ollama(final_prompt)
        
        print(f"\nAI: {ai_response}")
        
        # Save to SQLite memory
        save_to_memory("User", user_input)
        save_to_memory("AI", ai_response)

if __name__ == "__main__":
    main()