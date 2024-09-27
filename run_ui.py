# run_ui.py

import sys
import os
import threading
import logging
from flask import Flask, send_from_directory, jsonify, request
from agent_config import AgentContext, AgentConfig
from initialize import initialize
from python.helpers.files import get_abs_path
from dotenv import load_dotenv
from agent import Agent
import uuid

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the internal Flask server
app = Flask("app", static_folder=get_abs_path("./webui"), static_url_path="/")
lock = threading.Lock()


# Get context to run agent zero in
def get_context(ctxid: str):
    with lock:
        if not ctxid:
            return AgentContext.first() or AgentContext(config=initialize())
        return AgentContext.get(ctxid) or AgentContext(
            config=initialize(), context_id=ctxid
        )


# Add route for the root URL
@app.route('/')
def index():
    return send_from_directory(app.static_folder or '', 'index.html')


# Add route for the /poll endpoint
@app.route('/poll', methods=['POST'])
def poll():
    # TODO: Implement actual polling logic
    return jsonify({
        "status": "success",
        "message": "Polling endpoint reached"
    })


# Add route for the /msg endpoint
@app.route('/msg', methods=['POST'])
def handle_message():
    logging.debug("Received POST request to /msg endpoint")
    data = request.json
    if not data:
        logging.error("No JSON data provided in the request")
        return jsonify({"status": "error", "message": "No JSON data provided"}), 400

    message = data.get('message')
    ctxid = data.get('ctxid')
    logging.debug(f"Received message: {message}, ctxid: {ctxid}")

    if not message:
        logging.error("No message provided in the request")
        return jsonify({"status": "error", "message": "No message provided"}), 400

    try:
        context = get_context(ctxid)
        logging.debug(f"Got context: {context}")
        config = context.config if isinstance(context.config, AgentConfig) else AgentConfig()
        logging.debug(f"Got config: {config}")

        agent = Agent(
            agent_id=str(uuid.uuid4()),
            name="Agent Zero",
            config=config,
            context=context
        )
        logging.debug(f"Created agent: {agent}")

        response = agent.process_input(message)
        logging.debug(f"Agent response: {response}")
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        logging.exception(f"An error occurred while processing the message: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get("WEB_UI_PORT", 50001)))
