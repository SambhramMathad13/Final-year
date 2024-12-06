import cv2
import time
import base64
import requests
import json

# Client-specific configurations
CLIENT_ID = "laptop_2"  # Unique client identifier
SERVER_URL = "http://127.0.0.1:5000"  # Hub server URL

def fetch_command():
    """Fetch the command from the server."""
    try:
        response = requests.get(f"{SERVER_URL}/get_capture_status/{CLIENT_ID}")
        return response.json().get("command", "stop")
    except Exception as e:
        print(f"Error fetching command: {e}")
        return "stop"

def send_image_to_server(image_data, message="Empty space detected!"):
    """Send image data to the server."""
    try:
        response = requests.post(
            f"{SERVER_URL}/receive_alert/{CLIENT_ID}",
            json={"image": image_data, "message": message},
        )
        print(response.json())
    except Exception as e:
        print(f"Error sending image: {e}")

def capture_images():
    """Capture images based on the command."""
    cap = cv2.VideoCapture(0)
    while True:
        command = fetch_command()
        if command == "start":
            ret, frame = cap.read()
            if ret:
                _, img_encoded = cv2.imencode(".jpg", frame)
                img_data = base64.b64encode(img_encoded).decode("utf-8")
                send_image_to_server(img_data)
            time.sleep(5)  # Adjust the capture interval
        elif command == "stop":
            print(f"{CLIENT_ID} stopped capturing.")
            time.sleep(5)  # Wait before checking the status again

if __name__ == "__main__":
    capture_images()
