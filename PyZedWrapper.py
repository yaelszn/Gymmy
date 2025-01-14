import time
import pyzed.sl as sl
import threading
import cv2
import Settings as s
import mediapipe as mp
import socket
import json
import numpy as np


class PyZedWrapper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("MP INITIALIZATION")
        self.zed = sl.Camera()
        self.frame_count = 0
        self.start_time = time.time()

    def run(self):
        print("MP START")

        # Set configuration parameters for camera initialization
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD720
        init.coordinate_system = sl.COORDINATE_SYSTEM.IMAGE
        init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
        init.coordinate_units = sl.UNIT.MILLIMETER
        init.camera_fps = 60

        # Open the camera
        err = self.zed.open(init)
        if err != sl.ERROR_CODE.SUCCESS:
            print(repr(err))
            self.zed.close()
            exit(1)

        # Define Body Tracking parameters for skeleton recognition
        body_params = sl.BodyTrackingParameters()
        body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
        body_params.enable_tracking = True
        body_params.enable_body_fitting = False
        body_params.body_format = sl.BODY_FORMAT.BODY_18

        # Set runtime parameters
        runtime = sl.RuntimeParameters()
        runtime.measure3D_reference_frame = sl.REFERENCE_FRAME.WORLD

        # Enable positional tracking
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        positional_tracking_parameters.set_as_static = True
        self.zed.enable_positional_tracking(positional_tracking_parameters)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, -1)  # Range: 0 to 100
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.GAIN, -1)  # Range: 0 to 100

        # Enable body tracking
        zed_error = self.zed.enable_body_tracking(body_params)
        if zed_error != sl.ERROR_CODE.SUCCESS:
            print("enable_body_tracking", zed_error, "\nExit program.")
            self.zed.close()
            exit(-1)



        # MediaPipe Initialization
        mp_pose = mp.solutions.pose

        # Joint Dictionary for MediaPipe
        lm_dict = {'nose': 0, 'L_shoulder': 11, 'R_shoulder': 12, 'L_elbow': 13, 'R_elbow': 14,
                   'L_wrist': 15, 'R_wrist': 16, 'L_hip': 23, 'R_hip': 24}  # Updated to integers

        with mp_pose.Pose(
                min_detection_confidence=0.3,
                min_tracking_confidence=0.3) as pose:

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_address = ('localhost', 7000)

            zed_frame = sl.Mat()

            while not s.finish_program and self.zed.is_opened():
                # Capture ZED Frame
                if self.zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                    self.zed.retrieve_image(zed_frame, sl.VIEW.LEFT)
                    zed_image = zed_frame.get_data()

                    # Convert ZED frame to RGB for MediaPipe
                    mp_frame = cv2.cvtColor(zed_image, cv2.COLOR_BGRA2BGR)

                    # MediaPipe Pose Processing
                    mp_frame_rgb = cv2.cvtColor(mp_frame, cv2.COLOR_BGR2RGB)
                    results = pose.process(mp_frame_rgb)
                    message = ""

                    # Prepare UDP Message
                    if results.pose_landmarks:
                        for joint, idx in lm_dict.items():
                            landmark = results.pose_landmarks.landmark[idx]
                            if landmark.visibility >= 0.7:
                                message += f"{joint},{landmark.x},{landmark.y},{landmark.z}/"
                            else:
                                message += f"{joint},0,0,0/"
                    else:
                        message = "/".join([f"{joint},0,0,0" for joint in lm_dict.keys()]) + "/"

                    jsonmessage = json.dumps(message).encode()

                    self.sock.sendto(jsonmessage, self.server_address)


                    # # Visualize ZED keypoints
                    # for body in body_list:
                    #     for joint in body.keypoint_2d:
                    #         cv2.circle(mp_frame, (int(joint[0]), int(joint[1])), 5, (0, 255, 0), -1)

                    # FPS Calculation
                    self.frame_count += 1
                    elapsed_time = time.time() - self.start_time
                    if elapsed_time >= 1:
                        fps = self.frame_count / elapsed_time
                        print(f"FPS: {fps:.2f}")
                        self.frame_count = 0
                        self.start_time = time.time()

                    # # Display both feeds
                    # cv2.imshow("MediaPipe Pose", mp_frame)
                    if cv2.waitKey(1) == ord('q'):
                        s.finish_program = True
                        break

        # Cleanup resources
        self.zed.close()
        cv2.destroyAllWindows()
        print("Program ended")

    def get_zed(self):
        return self.zed


if __name__ == '__main__':
    s.stop = False
    s.finish_program = False
    mediap = PyZedWrapper()
    mediap.start()
