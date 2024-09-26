import threading
import socket
import json
import cv2
import mediapipe as mp
import Settings as s
import time


class MP(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        print("MP INITIALIZATION")

    def run(self):
        print("MP START")
        recorded_data = []
        show = True
        frame_count = 0  # Initialize a counter to keep track of frames
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_pose = mp.solutions.pose
        mp_hands = mp.solutions.hands  # Initialize hand model

        # Attempt to open the camera (use index 0, 1, or 2 depending on your setup)
        cap = cv2.VideoCapture(2)  # Try changing to 1 or 2 if 0 doesn't work

        # Check if camera opened successfully
        if not cap.isOpened():
            print("Error: Could not open video source.")
            return

        image_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float width
        image_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float height

        # Initialize both Pose and Hands models
        with mp_pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.5) as pose, \
             mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:

            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = ('localhost', 7000)

            # For FPS calculation
            prev_time = time.time()  # Store the start time

            while cap.isOpened():
                success, image = cap.read()

                # Check if frame was captured successfully
                if not success:
                    print("Error: Could not read frame.")
                    break  # Exit the loop if the frame cannot be captured

                # Increment the frame count
                frame_count += 1

                # Convert the image to RGB for MediaPipe processing
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Process both Pose and Hands
                results_pose = pose.process(image)
                results_hands = hands.process(image)

                # Convert back to BGR for OpenCV display
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Draw pose landmarks on the image
                if results_pose.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        results_pose.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),  # landmark spec
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)   # connection spec
                    )

                # Draw hand landmarks on the image
                if results_hands.multi_hand_landmarks:
                    for hand_landmarks in results_hands.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            image,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
                            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                        )

                # Merge pose and hand landmarks into one message
                message = self.merge_pose_and_hands(results_pose, results_hands, image_width, image_height)

                # Send the message via UDP
                jsonmessage = json.dumps(message).encode()
                sock.sendto(jsonmessage, server_address)

                # Calculate FPS
                current_time = time.time()
                fps = 1 / (current_time - prev_time)  # Calculate FPS as inverse of frame duration
                prev_time = current_time

                # Display FPS on the image
                cv2.putText(image, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Display the image with pose and hand landmarks
                if show:
                    cv2.imshow('MediaPipe Pose + Hands', cv2.flip(image, 1))

                # Stop MediaPipe if 'q' is pressed or workout is finished
                key = cv2.waitKey(1)
                if s.finish_workout or key == ord('q'):
                    s.finish_workout = True
                    break

            cap.release()
            cv2.destroyAllWindows()

    def merge_pose_and_hands(self, results_pose, results_hands, image_width, image_height):
        # Only include pose landmarks that are unrelated to the hand except the wrists
        lm_dict_pose = {
            'nose': "0", 'L_eye_inner': "1", 'L_eye': "2", "L_eye_outer": "3",
            'R_eye_inner': "4", 'R_eye': "5", "R_eye_outer": "6",
            'L_ear': "7", 'R_ear': "8", "L_mouth": "9", "R_mouth": "10",
            'L_shoulder': "11", 'R_shoulder': "12", 'L_elbow': "13", 'R_elbow': "14",
            'L_wrist': "15", 'R_wrist': "16", 'L_hip': "23", 'R_hip': "24"  # Keep wrists and hips from the pose model
        }

        # Dictionary for hand landmarks
        hand_landmarks_mapping = {
            0: 'wrist', 1: 'thumb_cmc', 2: 'thumb_mcp', 3: 'thumb_ip', 4: 'thumb_tip',
            5: 'index_mcp', 6: 'index_pip', 7: 'index_dip', 8: 'index_tip',
            9: 'middle_mcp', 10: 'middle_pip', 11: 'middle_dip', 12: 'middle_tip',
            13: 'ring_mcp', 14: 'ring_pip', 15: 'ring_dip', 16: 'ring_tip',
            17: 'pinky_mcp', 18: 'pinky_pip', 19: 'pinky_dip', 20: 'pinky_tip'
        }

        message = {}

        # Get pose landmarks, but exclude fingers
        if results_pose.pose_landmarks:
            for k, v in lm_dict_pose.items():
                j = results_pose.pose_landmarks.landmark[int(v)]
                message[k] = {
                    'x': j.x * image_width,
                    'y': j.y * image_height,
                    'z': j.z
                }

        # Get hand landmarks for both left and right hands
        if results_hands.multi_hand_landmarks and results_hands.multi_handedness:
            for idx, hand_landmarks in enumerate(results_hands.multi_hand_landmarks):
                handedness = results_hands.multi_handedness[idx].classification[0].label
                hand_prefix = 'L_hand_' if handedness == 'Left' else 'R_hand_'

                for i, landmark in enumerate(hand_landmarks.landmark):
                    message[hand_prefix + hand_landmarks_mapping[i]] = {
                        'x': landmark.x * image_width,
                        'y': landmark.y * image_height,
                        'z': landmark.z
                    }

        return message

if __name__ == '__main__':
    s.stop = False
    mediap = MP()
    mediap.start()
    s.finish_workout = False
