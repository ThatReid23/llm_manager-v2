ChatInterface
ChatInterface is a modern web-based front-end for the llm_manager system.
It provides a simple yet powerful interface for interacting with local or remote LLM backends managed through your unified API gateway.
🚀 Features
Chat history system — automatically saves conversations as JSON in the chat_history/ folder.
User authentication — lightweight login system for personalized sessions.
File uploads — attach files as context for chat interactions.
Model auto-detection — dynamically lists models discovered by the backend.
Simple, clean UI — responsive interface built with Flask templates and minimal JS.
🧩 Project Structure
code
Code
ChatInterface/
├── app.py                # Main Flask application
├── templates/
│   ├── index.html        # Main chat interface
│   └── login.html        # User login page
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # Client-side scripts
└── chat_history/
    └── user/             # Stored chat logs (JSON)
⚙️ Installation
Clone the repository
code
Bash
git clone https://github.com/ryyReid/ChatInterface.git
cd ChatInterface
Install dependencies
code
Bash
pip install -r requirements.txt
Configure environment
Set your backend URL and API key inside app.py:
code
Python
MANAGER_API_URL = "http://localhost:8000"
MANAGER_API_KEY = "your_api_key_here"
Run the app
code
Bash
python app.py
Access the interface at http://127.0.0.1:5000.
🧠 How It Works
ChatInterface communicates directly with your llm_manager backend, which routes requests to the correct LLM nodes.
This allows multiple models to be accessed through one clean endpoint, while user sessions, chat logs, and file contexts stay locally stored for privacy and speed.
📦 Requirements
Python 3.10+
Flask
Requests
(Optional) Access to a running llm_manager backend
🧑‍💻 Author
Reid
GitHub: @ryyReid • @ThatReid23
🪐 License
MIT License © 2025 Reid
