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
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_pose = mp.solutions.pose

        # Attempt to open the camera (use index 0, 1, or 2 depending on your setup)
        cap = cv2.VideoCapture(0)  # Try changing to 1 or 2 if 0 doesn't work

        # Check if camera opened successfully
        if not cap.isOpened():
            print("Error: Could not open video source.")
            return

        image_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
        image_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`

        with mp_pose.Pose(
                min_detection_confidence=0.8,
                min_tracking_confidence=0.5) as pose:

            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = ('localhost', 7000)

            while cap.isOpened():
                success, image = cap.read()

                # Check if frame was captured successfully
                if not success:
                    print("Error: Could not read frame.")
                    break  # Exit the loop if the frame cannot be captured

                # Convert the image to RGB for MediaPipe processing
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image)

                lm_dict = {'nose': "0", 'L_eye_inner': "1", 'L_eye': "2", "L_eye_outer": "3",
                           'R_eye_inner': "4", 'R_eye': "5", "R_eye_outer": "6",
                           'L_ear': "7", 'R_ear': "8", "L_mouth": "9", "R_mouth": "10",
                           'L_Shoulder': "11", 'R_Shoulder': "12", 'L_Elbow': "13", 'R_Elbow': "14",
                           'L_Wrist': "15", 'R_Wrist': "16",
                           'L_pinky': "17", 'R_pinky': "18", 'L_index': "19", 'R_index': "20",
                           'L_thumb': "21", 'R_thumb': "22", 'L_Hip': "23", 'R_Hip': "24"}

                message = ''
                if results.pose_landmarks is not None:
                    for k, v in lm_dict.items():
                        j = results.pose_landmarks.landmark[int(v)]
                        if j.visibility >= 0.7:
                            new_j = k + "," + str(j.x * image_width) + "," + str(-j.y * image_height) + "," + str(-j.z)
                        else:
                            new_j = k + ",0,0,0"
                        message += new_j + "/"
                else:
                    for k, v in lm_dict.items():
                        new_j = k + ",0,0,0"
                        message += new_j + "/"

                jsonmessage = json.dumps(message).encode()
                sent = sock.sendto(jsonmessage, server_address)

                # Convert back to BGR for OpenCV display
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Draw pose landmarks on the image
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

                # Display the image with pose landmarks
                if show:
                    cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))

                # Stop MediaPipe if 'q' is pressed or workout is finished
                key = cv2.waitKey(1)
                if s.finish_workout or key == ord('q'):
                    s.finish_workout = True
                    break

                recorded_data.append({
                    'timestamp': time.time(),
                    'json_message': message
                })

            cap.release()
            cv2.destroyAllWindows()

            # Save recorded data to a JSON file
            with open('recorded_data2.json', 'w') as f:
                json.dump(recorded_data, f)


if __name__ == '__main__':
    s.stop = False
    mediap = MP()
    mediap.start()
    s.finish_workout = False
