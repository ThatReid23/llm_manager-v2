# app.py (Upgraded for High-Availability Routing)

import yaml
import requests
from functools import wraps
from flask import Flask, request, jsonify, Response, render_template, redirect, url_for, session

# --- 1. Initialization and Configuration ---

app = Flask(__name__)
# This global variable will hold our configuration.
CONFIG = {}

def load_config():
    """Loads config from YAML and sets up the app."""
    global CONFIG
    with open("config.yaml", "r") as f:
        CONFIG = yaml.safe_load(f)

    # Set Flask secret key for session management from the config file.
    app.secret_key = CONFIG['manager']['secret_key']
    
    print("Configuration loaded successfully.")

# --- 2. Security Wrappers and Helper Functions ---

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header is missing or invalid"}), 401
        provided_key = auth_header.split(' ')[1]
        if provided_key not in CONFIG.get('client_api_keys', []):
            return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_node_health(node_address):
    """Pings a node's base URL to see if it's responsive."""
    try:
        requests.get(node_address, timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False

# --- 3. Core API Endpoint (High-Availability Version) ---

##
## <<< THIS IS THE LINE YOU ARE ASKING ABOUT. IT DEFINES THE ROUTER'S MAIN ENDPOINT. <<<
##
@app.route('/v1/chat/completions', methods=['POST'])
@api_key_required
def route_chat_completion():
    """
    Receives an OpenAI-compatible request and routes it to the first
    available inference node that supports the requested model.
    """
    request_data = request.get_json()
    model_name = request_data.get('model')

    if not model_name:
        return jsonify({"error": "The 'model' field is required."}), 400

    potential_nodes = [node for node in CONFIG.get('nodes', []) if model_name in node.get('models', [])]

    if not potential_nodes:
        return jsonify({"error": f"Model '{model_name}' is not supported by any configured node."}), 404

    for node_info in potential_nodes:
        if check_node_health(node_info['address']):
            print(f"Routing request for '{model_name}' to available node: {node_info['name']}")
            try:
                node_response = requests.post(
                    f"{node_info['address']}/v1/chat/completions",
                    headers={'Authorization': f"Bearer {node_info.get('api_key')}", 'Content-Type': 'application/json'},
                    json=request_data, stream=True, timeout=300
                )
                return Response(node_response.iter_content(chunk_size=1024), status=node_response.status_code, content_type=node_response.headers.get('Content-Type'))
            except requests.exceptions.RequestException as e:
                print(f"Node {node_info['name']} failed during request: {e}. Trying next available.")
                continue

    return jsonify({"error": f"Service unavailable. No nodes for model '{model_name}' are online."}), 503

# --- 4. Web Management UI Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        creds = CONFIG['management_ui']
        if request.form['username'] == creds['username'] and request.form['password'] == creds['password']:
            session['logged_in'] = True
            return redirect(url_for('manage_dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@app.route('/manage')
@login_required
def manage_dashboard():
    nodes_with_status = []
    for node in CONFIG.get('nodes', []):
        status_info = node.copy()
        status_info['online'] = check_node_health(node['address'])
        nodes_with_status.append(status_info)
    return render_template('manage.html', config=CONFIG, nodes_status=nodes_with_status)

# --- 5. Application Runner ---
# THIS BLOCK MUST BE AT THE VERY END OF THE FILE.
# DO NOT ADD ANY @app.route DEFINITIONS AFTER THIS.

if __name__ == '__main__':
    load_config()
    manager_config = CONFIG.get('manager', {})
    app.run(
        host=manager_config.get('host', '127.0.0.1'),
        port=manager_config.get('port', 8000),
        debug=True
    )