import cv2
import time
import base64
import requests

# Client-specific configurations
CLIENT_ID = "laptop_1"  # Unique client identifier
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
    cap = None  # Initialize capture object

    while True:
        command = fetch_command()

        if command == "start":
            if cap is None:  # Open the camera only if not already opened
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print(f"Error: Unable to access the camera on {CLIENT_ID}.")
                    break
                print(f"{CLIENT_ID} started capturing.")

            ret, frame = cap.read()
            if ret:
                _, img_encoded = cv2.imencode(".jpg", frame)
                img_data = base64.b64encode(img_encoded).decode("utf-8")
                send_image_to_server(img_data)
            else:
                print("Error: Failed to capture image.")

            time.sleep(5)  # Adjust the capture interval

        elif command == "stop":
            print(f"{CLIENT_ID} stopped capturing.")
            if cap is not None:  # Release the camera when stopping
                cap.release()
                cap = None
                print(f"{CLIENT_ID}: Camera released.")
            time.sleep(5)  # Wait before checking the status again

    # Cleanup if exiting the loop
    if cap is not None:
        cap.release()
        print(f"{CLIENT_ID}: Camera released on exit.")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_images()
