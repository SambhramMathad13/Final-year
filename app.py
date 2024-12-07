import base64
from flask import Flask, render_template, request, jsonify
import os
import time
from threading import Lock

app = Flask(__name__)

# Directory for storing images
STATIC_IMAGE_FOLDER = 'static/images'
if not os.path.exists(STATIC_IMAGE_FOLDER):
    os.makedirs(STATIC_IMAGE_FOLDER)

# State to manage commands for each client
client_states = {}
status_lock = Lock()

@app.route('/start_capture/<client_id>', methods=['POST'])
def start_capture(client_id):
    """Set the command to start capturing for a specific client."""
    global client_states
    with status_lock:
        client_states[client_id] = 'start'
    return jsonify({'status': f'Capture started for {client_id}'})

@app.route('/stop_capture/<client_id>', methods=['POST'])
def stop_capture(client_id):
    """Set the command to stop capturing for a specific client."""
    global client_states
    with status_lock:
        client_states[client_id] = 'stop'
    return jsonify({'status': f'Capture stopped for {client_id}'})

@app.route('/get_capture_status/<client_id>', methods=['GET'])
def get_capture_status(client_id):
    """Return the current capture command for a specific client."""
    global client_states
    with status_lock:
        # Default to "stop" if no state is set for the client
        return jsonify({'command': client_states.get(client_id, 'stop')})

@app.route('/receive_alert/<client_id>', methods=['POST'])
def receive_alert(client_id):
    """Receive image data from a specific client."""
    data = request.json
    image_data = data.get('image')
    message = data.get('message', '')

    # Create a subfolder for each client
    client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)
    if not os.path.exists(client_folder):
        os.makedirs(client_folder)

    # Save the image
    if image_data:
        filename = f'image_{int(time.time())}.jpg'
        filepath = os.path.join(client_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(image_data))
        print(f"Saved image for {client_id}: {filepath}")
        return jsonify({'status': 'Image received', 'message': message})

    return jsonify({'status': 'No image received'})

@app.route('/get_images/<client_id>', methods=['GET'])
def get_images(client_id):
    """Return the list of captured images for a specific client."""
    client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)
    if not os.path.exists(client_folder):
        return jsonify([])  # No images for this client
    images = os.listdir(client_folder)
    images = [f'/static/images/{client_id}/{img}' for img in sorted(images)]
    return jsonify(images)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
