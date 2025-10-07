# llm_manager-v2

**Description**  
`llm_manager-v2` is a Python Flask app for managing and interacting with large language models (LLMs). It provides a web interface and API for querying multiple LLM instances, auto-detects available models, stores chat histories, and supports YAML-based configuration for easy setup and distributed inference workflows.

---

## Features

- Web interface to manage LLMs  
- API endpoints for programmatic interaction  
- Auto-detects available LLM models on different nodes  
- Stores chat history and session data  
- YAML-based configuration for easy customization  
- Lightweight and easy to deploy  

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YourUsername/llm_manager-v2.git
cd llm_manager-v2
Create a virtual environment (recommended):

Windows:

powershell
Copy code
python -m venv venv
.\venv\Scripts\activate
Linux/Mac:

bash
Copy code
python -m venv venv
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Usage
Start the Flask server:

bash
Copy code
python app.py
Open your browser:

cpp
Copy code
http://127.0.0.1:5000
Use the web interface to manage and query LLMs.

Configuration
config.yaml – main configuration for models, nodes, and API keys

chat_history/ – folder to store persistent chat sessions

Dependencies (requirements.txt)
shell
Copy code
Flask>=2.3.0
requests>=2.31.0
PyYAML>=6.0
License
java
Copy code
MIT License
Copyright (c) 2025 Reid
pgsql
Copy code

This is a **fully structured `README.md`** you can place in the root of your GitHub repository.  

If you want, I can also make a **version with GitHub badges** and a nicer “first impression” style for the repo page. Do you want me to do that?
