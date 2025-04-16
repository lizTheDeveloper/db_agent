import requests
import base64
import cv2
import openai
import time

import os

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to encode the image
def encode_image(image_path):
    print(image_path)
    with open(image_path, "rb") as image_file:
        print(f"Encoding image: {image_path}")
        print(f"Image size: {os.path.getsize(image_path)} bytes")
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_images_to_openai(image, prompt):


    # Getting the base64 string
    base64_image = encode_image(image[0])


    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {client.api_key}",
    }
    content = [{
        "type": "text",
        "text": prompt
    }]
    content.append({
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
        }
    })
    

    payload = {
        "model": "gpt-4o-mini",
        "messages":[
            {
                "role": "user",
                "content": content
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response.text)
    response_json = response.json()
    print(response_json)
    ## return only the text
    return response_json["choices"][0]["message"]["content"]


def capture_frames_from_stream():
        most_recent_timestamp = time.time()

        cap = cv2.VideoCapture(0)
        
        # Initialize video capture from the stream URL
        if not cap.isOpened():
            print("Error: Unable to open stream.")
            return
        try:
            ## move the current rover.jpg to the current timestamp.jpg in the /old_frames directory
            ## then save the current frame as rover.jpg
            ## this will allow us to keep a history of frames
            ## if the rover.jpg file does not exist, we will not move it
            if os.path.exists("rover.jpg"):
            
                old_frame_filename = f"old_frames/{most_recent_timestamp}.jpg"
                os.rename("rover.jpg", old_frame_filename)


            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to fetch frame.")
                return

            # Save the frame as an image file
            cv2.imwrite(f"rover.jpg", frame)
            print(f"Captured frame")


        except Exception as e:
            print(f"Error: {e}")
            # Release the video capture object
            print("video capture died")
        finally:
            cap.release()
            ## reconnect 
            cap = cv2.VideoCapture(0)
            cv2.destroyAllWindows()
            
def get_camera_frame():
    global most_recent_timestamp
    most_recent_timestamp = time.time()
    ## read rover.png
    output_filename = "rover.jpg"
    capture_frames_from_stream()
    

    return output_filename
            


class AutonomousAgent():
    def __init__(self, name, mode='default'):
        self.name = name
        self.mode = mode

    def set_mode(self, mode):
        self.mode = mode
        print(f"{self.name} is now in {self.mode} mode.")

    def perform_action(self):
        if self.mode == 'default':
            print(f"{self.name} is navigating or exploring.")
        elif self.mode == 'analyzing':
            print(f"{self.name} is analyzing sensor data.")
        elif self.mode == 'moving':
            print(f"{self.name} is currently moving.")
        else:
            print(f"{self.name} is in an unknown mode.")
            
    def observe(self):
        
        global most_recent_timestamp
        frame = get_camera_frame()  
        
        if self.mode == "default":
            observation_prompt = """
            Your visual point of view is third-person
            You are an autonomous rover exploring an environment.
            You have a camera that captures images of your surroundings.
            Decide what to do next based on the image.
            You can: move_forward, turn_left, turn_right, stop, or analyze_the_environment.
            Please respond with only one of those actions.
            """
        elif self.mode == "analyzing_the_environment":
            observation_prompt = """
            Your visual point of view is third-person
            You are an autonomous rover analyzing the environment.
            You have a camera that captures images of your surroundings.
            Analyze the image and describe what you see.
            Please respond with a description of the environment.
            """
        else:
            observation_prompt = """
            Your visual point of view is third-person
            You are an autonomous rover exploring an environment.
            You have a camera that captures images of your surroundings.
            """
        observation = upload_images_to_openai([frame], observation_prompt)
        
        print(f"Observation: {observation}")
        ## log observations based on this timestamp 
        with open("observations.jsonl", "a") as f:
            f.write((str(most_recent_timestamp) + "|" + observation + "\n"))

        
        return observation

    def orient(self, observation):
        if "analyze_the_environment" in observation:
            print(f"{self.name} is analyzing the environment based on observation.")
            self.set_mode('analyzing_the_environment')
        elif "move_forward" in observation:
            print(f"{self.name} is moving forward.")
            self.set_mode('moving')
        elif "turn_left" in observation:
            print(f"{self.name} is turning left.")
            self.set_mode('moving')
        elif "turn_right" in observation:
            print(f"{self.name} is turning right.")
            self.set_mode('moving')
        elif "stop" in observation:
            print(f"{self.name} is stopping.")
            self.set_mode('default')
        else:
            print(f"{self.name} received an unknown observation: {observation}.")
    
    def decide(self, observation):
        # This method can be expanded to include more complex decision-making logic
        print(f"{self.name} is deciding based on observation: {observation}")
        
                 
    def run(self):
        while True:
            ## observe the environment - get sensor data
            ## read from camera
            observation = self.observe()
            print(f"Observation: {observation}")
            
            
            ## orient yourself in your environment - make sense of sensor data
            self.orient(observation)
            ## decide what to do - autonomy happen here
            
            ## act - actually do it
            
rover = AutonomousAgent(name="Rover", mode='default')
rover.run()