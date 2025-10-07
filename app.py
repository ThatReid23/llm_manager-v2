# llm_manager/app.py (with Auto-Detecting Model Discovery)

import yaml
import requests
from functools import wraps
from flask import Flask, request, jsonify, Response, render_template, redirect, url_for, session

# --- 1. Initialization and Configuration ---
app = Flask(__name__)
CONFIG = {}
# --- NEW: In-memory cache to store which model lives on which node ---
MODEL_CACHE = {} 

def load_config():
    """Loads config from YAML."""
    global CONFIG
    with open("config.yaml", "r") as f:
        CONFIG = yaml.safe_load(f)
    app.secret_key = CONFIG['manager']['secret_key']
    print("LLM Manager configuration loaded.")

# --- NEW: Function to auto-discover and cache models ---
def update_model_cache():
    """
    Contacts all nodes, asks for their models, and builds the routing cache.
    """
    global MODEL_CACHE
    MODEL_CACHE = {}
    print("Attempting to auto-detect models from all configured nodes...")

    for node_info in CONFIG.get('nodes', []):
        node_name = node_info['name']
        node_address = node_info['address']
        node_api_key = node_info.get('api_key', '')

        try:
            # Ask the node for its list of models
            headers = {'Authorization': f'Bearer {node_api_key}'}
            response = requests.get(f"{node_address}/v1/models", headers=headers, timeout=5)
            response.raise_for_status()
            
            models_data = response.json().get('data', [])
            if not models_data:
                print(f"  - Node '{node_name}' is online but reported no models.")
                continue

            # Add each discovered model to the cache
            for model in models_data:
                model_id = model.get('id')
                if model_id:
                    MODEL_CACHE[model_id] = node_info # Store the entire node's info
                    print(f"  + Discovered model '{model_id}' on node '{node_name}'.")

        except requests.exceptions.RequestException as e:
            print(f"  - Node '{node_name}' is offline or could not be reached: {e}")
    
    print(f"Model auto-detection complete. Total models available: {len(MODEL_CACHE)}")


# --- 2. Security Wrappers and Helper Functions (Unchanged) ---
def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization');
        if not auth_header or not auth_header.startswith('Bearer '): return jsonify({"error": "Authorization header is missing"}), 401
        provided_key = auth_header.split(' ')[1];
        if provided_key not in CONFIG.get('client_api_keys', []): return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session: return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_node_health(node_address):
    try: requests.get(node_address, timeout=2); return True
    except requests.exceptions.RequestException: return False


# --- 3. Core API Endpoints (MODIFIED to use the cache) ---

@app.route('/v1/models', methods=['GET'])
@api_key_required
def list_models():
    """Returns the list of all auto-detected, cached models."""
    model_data = [{"id": name, "object": "model"} for name in sorted(list(MODEL_CACHE.keys()))]
    return jsonify({"object": "list", "data": model_data})

@app.route('/v1/chat/completions', methods=['POST'])
@api_key_required
def route_chat_completion():
    """Routes chat requests using the auto-populated model cache."""
    try: request_data = request.get_json();
    except Exception: return jsonify({"error": "Failed to parse JSON body."}), 400
    
    model_name = request_data.get('model')
    if not model_name: return jsonify({"error": "The 'model' field is required."}), 400

    # --- MODIFIED: The routing logic is now a simple, fast cache lookup ---
    node_info = MODEL_CACHE.get(model_name)

    if not node_info:
        return jsonify({"error": f"Model '{model_name}' not found in cache or its node is offline."}), 404

    # Check node health just in case it went offline since the last cache update
    if not check_node_health(node_info['address']):
        return jsonify({"error": f"Node '{node_info['name']}' for model '{model_name}' is currently offline."}), 503

    print(f"Routing request for '{model_name}' to cached node: {node_info['name']}")
    try:
        node_response = requests.post(
            f"{node_info['address']}/v1/chat/completions",
            headers={'Authorization': f"Bearer {node_info.get('api_key')}", 'Content-Type': 'application/json'},
            json=request_data, stream=True, timeout=300
        )
        return Response(node_response.iter_content(chunk_size=1024), status=node_response.status_code, content_type=node_response.headers.get('Content-Type'))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to backend node '{node_info['name']}': {e}"}), 502

# --- 4. Web Management UI Routes (Unchanged) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        creds = CONFIG['management_ui'];
        if request.form['username'] == creds['username'] and request.form['password'] == creds['password']:
            session['logged_in'] = True; return redirect(url_for('manage_dashboard'))
        else: return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout(): session.pop('logged_in', None); return redirect(url_for('login'))

@app.route('/')
@app.route('/manage')
@login_required
def manage_dashboard():
    nodes_with_status = [];
    for node in CONFIG.get('nodes', []):
        status_info = node.copy(); status_info['online'] = check_node_health(node['address']); nodes_with_status.append(status_info)
    return render_template('manage.html', config=CONFIG, nodes_status=nodes_with_status)


# --- 5. Application Runner (MODIFIED to build cache on startup) ---
if __name__ == '__main__':
    load_config()
    update_model_cache() # <-- NEW: Auto-detect and cache models when the server starts
    manager_config = CONFIG.get('manager', {})
    app.run(
        host=manager_config.get('host', '127.0.0.1'),
        port=manager_config.get('port', 8000),
        debug=True
    )