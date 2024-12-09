import base64
import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from threading import Lock

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a strong random secret key

# Directory for storing images
STATIC_IMAGE_FOLDER = 'static/images'
if not os.path.exists(STATIC_IMAGE_FOLDER):
    os.makedirs(STATIC_IMAGE_FOLDER)

# Hardcoded credentials for authentication
USERNAME = "admin"
PASSWORD = "admin"

# State to manage commands for each client
client_states = {}
status_lock = Lock()


# ------------------------------
# Authentication Routes
# ------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('authenticated'):  # Prevent logged-in users from accessing login page
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))


# ------------------------------
# Main Index Route
# ------------------------------

@app.route('/')
def index():
    if not session.get('authenticated'):  # Restrict access if not logged in
        return redirect(url_for('login'))
    return render_template('index.html')  # Main dashboard


# ------------------------------
# Client Command and Alerts Management
# ------------------------------

@app.route('/start_capture/<client_id>', methods=['POST'])
def start_capture(client_id):
    global client_states
    with status_lock:
        client_states[client_id] = 'start'
    return jsonify({'status': f'Capture started for {client_id}'})


@app.route('/stop_capture/<client_id>', methods=['POST'])
def stop_capture(client_id):
    global client_states
    with status_lock:
        client_states[client_id] = 'stop'
    return jsonify({'status': f'Capture stopped for {client_id}'})


@app.route('/get_capture_status/<client_id>', methods=['GET'])
def get_capture_status(client_id):
    global client_states
    with status_lock:
        return jsonify({'command': client_states.get(client_id, 'stop')})


@app.route('/receive_alert/<client_id>', methods=['POST'])
def receive_alert(client_id):
    data = request.json
    img_data = base64.b64decode(data['image'])

    client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)
    os.makedirs(client_folder, exist_ok=True)

    # Save the image
    timestamp = int(time.time())
    image_filename = f"{timestamp}.jpg"
    image_path = os.path.join(client_folder, image_filename)
    with open(image_path, "wb") as img_file:
        img_file.write(img_data)

    return jsonify({"status": "Image received!"})


@app.route('/get_images/<client_id>', methods=['GET'])
def get_images(client_id):
    client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)

    if not os.path.exists(client_folder):
        return jsonify([])

    images = []
    for img_file in sorted(os.listdir(client_folder)):
        if img_file.endswith(".jpg"):
            image_path = f'/static/images/{client_id}/{img_file}'
            # Extract timestamp from the filename
            timestamp = img_file.split('.')[0]
            readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))
            message = f"Empty space detected! by {client_id.replace('_', ' ')}"
            images.append({"image": image_path, "message": message, "time": readable_time})

    return jsonify(images)


@app.route('/delete_images/<client_id>', methods=['POST'])
def delete_images(client_id):
    data = request.json
    deleted_files = []

    for filename in data['filenames']:
        image_path = os.path.join(STATIC_IMAGE_FOLDER, client_id, filename)
        if os.path.exists(image_path):
            os.remove(image_path)
            deleted_files.append(filename)

    return jsonify({"status": "Images deleted successfully", "deleted": deleted_files})


# ------------------------------
# Run Application
# ------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
