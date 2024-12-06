import cv2
import time
import base64
import requests

# URL of the Flask server
SERVER_URL = 'http://127.0.0.1:5000'
GET_COMMAND_URL = f'{SERVER_URL}/get_capture_status'
POST_IMAGE_URL = f'{SERVER_URL}/receive_alert'

def fetch_command():
    """Fetch the current capture command from the server."""
    try:
        response = requests.get(GET_COMMAND_URL)
        response.raise_for_status()
        return response.json().get('command', 'stop')
    except Exception as e:
        print(f"Error fetching command: {e}")
        return 'stop'

def send_image(frame):
    """Send captured image to the server."""
    _, img_encoded = cv2.imencode('.jpg', frame)
    img_data = base64.b64encode(img_encoded).decode('utf-8')
    data = {
        'message': 'Empty space detected!',  # Example message
        'image': img_data
    }
    try:
        response = requests.post(POST_IMAGE_URL, json=data)
        print(response.json())
    except Exception as e:
        print(f"Error sending image: {e}")

def capture_images():
    cap = cv2.VideoCapture(0)
    while True:
        command = fetch_command()
        if command == 'stop':
            print("Capture stopped.")
            time.sleep(1)
            continue

        print("Capturing images...")
        ret, frame = cap.read()
        if not ret:
            print("Error accessing camera.")
            break

        send_image(frame)
        time.sleep(5)  # Capture every 5 seconds

    cap.release()

if __name__ == '__main__':
    capture_images()
