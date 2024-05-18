import pyzed.sl as sl
import threading
import cv2
import mediapipe as mp
import Settings as s
import sys


class MP(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        print("MP INITIALIZATION")
        self.zed = sl.Camera()


    def run(self):
        print("MP START")
        show = True
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_pose = mp.solutions.pose

        ################################################################
        # Create a ZED camera object

        # Set configuration parameters
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD720
        init.coordinate_system= sl.COORDINATE_SYSTEM.IMAGE
        init.depth_mode = sl.DEPTH_MODE.ULTRA
        init.coordinate_units = sl.UNIT.MILLIMETER
        init.camera_fps=60
        #if len(sys.argv) >= 2:
        #    init.svo_input_filename = sys.argv[1]

        # Open the camera
        #################למחוק בסוף
        self.zed.close()
        err = self.zed.open(init)
        if err != sl.ERROR_CODE.SUCCESS:
            print(repr(err))
            self.zed.close()
            exit(1)
        # Display help in console
        # print_help()

        # Define the Objects detection module parameters
        body_params = sl.BodyTrackingParameters()
        # Set runtime parameters for body tracking
        body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
        body_params.enable_tracking = True
        body_params.image_sync = True
        # body_params.enable_segmentation = False
        body_params.enable_body_fitting = True
        body_params.body_format = sl.BODY_FORMAT.BODY_18

        # Set runtime parameters after opening the camera
        runtime = sl.RuntimeParameters()
        sl.RuntimeParameters.enable_fill_mode
        runtime.measure3D_reference_frame = sl.REFERENCE_FRAME.WORLD

        # if detection_parameters.enable_tracking:
        # Set positional tracking parameters
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        # Enable positional tracking
        positional_tracking_parameters.set_as_static = True
        self.zed.enable_positional_tracking(positional_tracking_parameters)

        # Enable body tracking
        zed_error = self.zed.enable_body_tracking(body_params)
        if zed_error != sl.ERROR_CODE.SUCCESS:
            print("enable_body_tracking", zed_error, "\nExit program.")
            self.zed.close()
            exit(-1)

        # Prepare new image size to retrieve half-resolution images
        image_size = self.zed.get_camera_information().camera_configuration.resolution;


        #image_size.width = image_size.width
        #image_size.height = image_size.height
        # image_size.height = image_size.height / 2

        # Declare your sl.Mat matrices

        ################################################################
        image = sl.Mat()

        with mp_pose.Pose(
                min_detection_confidence=0.85,
                min_tracking_confidence=0.7) as pose:

            # Create a UDP socket
            #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #server_address = ('localhost', 7000)

            while self.zed.is_opened() and not s.finish_workout:

                if self.zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:

                    self.zed.retrieve_image(image, sl.VIEW.LEFT)
                    self.zed.retrieve_image(image, sl.VIEW.RIGHT)
                    frame = image.get_data()
                    # Convert the frame to RGB format (MediaPipe requires RGB input)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = pose.process(frame_rgb)

                    lm_dict = {'nose': "0", 'neck': "1", 'R_shoulder': "2", 'R_elbow': "3", 'R_wrist': "4",
                               'L_shoulder': "5", 'L_elbow': "6", 'L_wrist': "7", 'R_hip': "8", 'R_knee': "9",
                               'R_ankle': "10", 'L_hip': "11", 'L_knee': "12", 'L_ankle': "13", 'R_eye': "14", 'L_eye': "15",
                               'R_ear': "16", 'L_ear': "17"}

                    message = ''
                    if results.pose_landmarks is not None:
                        for k, v in lm_dict.items():
                            j = results.pose_landmarks.landmark[int(v)]
                            if j.visibility >= 0.7:
                                new_j = k + "," + str(j.x * image_size.width) + "," + str(
                                    -j.y * image_size.height) + "," + str(-j.z)
                            else:
                                new_j = k + ",0,0,0"
                            message += new_j + "/"
                    else:
                        for k, v in lm_dict.items():
                            new_j = k + ",0,0,0"
                            message += new_j + "/"

                    frame_rgb = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

                    mp_drawing.draw_landmarks(
                        frame_rgb,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                    # Present camera's video: Flip the image horizontally for a selfie-view display.
                    zoom_out_factor = 0.5  # Adjust the factor to control the level of zoom-out
                    resized_frame = cv2.resize(frame_rgb, None, fx=zoom_out_factor, fy=zoom_out_factor)

                    if show:
                        cv2.imshow("ZED Camera with Skeleton", resized_frame)

                    # Stop MediaPipe:
                    key = cv2.waitKey(10)
                    if s.finish_workout or key == ord('q'):
                        s.finish_workout = True
                        break

            self.zed.close()


    def get_zed(self):
         return self.zed




if __name__ == ('__main__'):
    s.stop = False
    s.finish_workout = False
    mediap = MP()
    mediap.start()
