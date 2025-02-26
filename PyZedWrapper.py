import time
import pyzed.sl as sl
import threading
import cv2
import Settings as s

class PyZedWrapper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("MP INITIALIZATION")
        self.zed = sl.Camera()
        self.frame_count = 0  # To count the number of frames captured
        self.start_time = time.time()  # To track the start time for FPS calculation

    def run(self):
        print("MP START")

        # Set configuration parameters for camera initialization
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD720
        init.coordinate_system = sl.COORDINATE_SYSTEM.IMAGE
        init.depth_mode = sl.DEPTH_MODE.ULTRA
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
        body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_MEDIUM
        body_params.enable_tracking = True
        body_params.enable_body_fitting = True
        body_params.body_format = sl.BODY_FORMAT.BODY_18
        body_params.prediction_timeout_s = 0.2
        # body_params.allow_reduced_precision_inference = True

        # Set runtime parameters
        runtime = sl.RuntimeParameters()
        runtime.measure3D_reference_frame = sl.REFERENCE_FRAME.WORLD
        # runtime.enable_fill_mode = True
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

        # Declare an sl.Mat object to hold image data
        image = sl.Mat()
        bodies = sl.Bodies()  # Structure to hold body tracking data

        while self.zed.is_opened() and not s.finish_program:
            if self.zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                time.sleep(0.001)
                # Retrieve the left view image for display
                # self.zed.retrieve_image(image, sl.VIEW.LEFT)
                # frame = image.get_data()
                #
                # # Retrieve bodies (skeleton data)
                # self.zed.retrieve_bodies(bodies, sl.BodyTrackingRuntimeParameters())
                # body_list = bodies.body_list
                #
                # # Draw markers for each joint if a body is detected
                # for body in body_list:
                #     for joint in body.keypoint_2d:  # 2D keypoints
                #         # Draw a small circle at each joint position
                #         cv2.circle(frame, (int(joint[0]), int(joint[1])), 5, (0, 255, 0), -1)  # Green circle

                # Increment frame count for FPS calculation
                self.frame_count += 1
                current_time = time.time()
                elapsed_time = current_time - self.start_time

                # Calculate FPS every second
                if elapsed_time >= 1:
                    fps = self.frame_count / elapsed_time
                    print(f"FPS: {fps:.2f}")
                    self.frame_count = 0
                    self.start_time = current_time

                # Display the ZED camera's view with skeleton tracking every 10th frame
               #if self.frame_count % 10 == 0:
                # cv2.imshow("ZED Camera with Skeleton", frame)

                # Stop camera if 'q' is pressed or finish_program is triggered
                key = cv2.waitKey(10)
                if s.finish_program or key == ord('q'):
                    s.finish_program = True
                    break

        # Close the camera when done
        self.zed.close()
        print("Camera closed")

    def get_zed(self):
        return self.zed

if __name__ == '__main__':
    # Initialize settings variables
    s.stop = False
    s.finish_program = False
    s.finish_workout = False

    # Start the ZED camera thread
    mediap = PyZedWrapper()
    mediap.start()