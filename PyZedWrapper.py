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

        ################################################################
        # Set configuration parameters for camera initialization
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD720  # Lower resolution to increase FPS
        init.coordinate_system = sl.COORDINATE_SYSTEM.IMAGE  # Set coordinate system to IMAGE (standard for 2D image)
        init.depth_mode = sl.DEPTH_MODE.PERFORMANCE  # Less computationally intensive depth mode
        init.coordinate_units = sl.UNIT.MILLIMETER  # Units in millimeters for depth
        init.camera_fps = 60  # Lower FPS to balance performance

        # Open the camera
        err = self.zed.open(init)
        if err != sl.ERROR_CODE.SUCCESS:
            print(repr(err))
            self.zed.close()
            exit(1)

        # Define Body Tracking parameters for skeleton recognition
        body_params = sl.BodyTrackingParameters()
        body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST  # Use the fastest tracking model
        body_params.enable_tracking = True
        #body_params.image_sync = True
        body_params.enable_body_fitting = False  # Disable body fitting for performance
        body_params.body_format = sl.BODY_FORMAT.BODY_38  # Use BODY_18 format for 18 joints

        # Set runtime parameters
        runtime = sl.RuntimeParameters()
        runtime.measure3D_reference_frame = sl.REFERENCE_FRAME.WORLD  # 3D reference frame

        # Enable positional tracking for body tracking in world coordinates
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        positional_tracking_parameters.set_as_static = True  # Static scene assumption for better stability
        self.zed.enable_positional_tracking(positional_tracking_parameters)

        # Enable body tracking
        zed_error = self.zed.enable_body_tracking(body_params)
        if zed_error != sl.ERROR_CODE.SUCCESS:
            print("enable_body_tracking", zed_error, "\nExit program.")
            self.zed.close()
            exit(-1)

        # Declare an sl.Mat object to hold image data
        image = sl.Mat()

        while self.zed.is_opened() and not s.finish_program:
            if self.zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                # Retrieve the left view image for display
                self.zed.retrieve_image(image, sl.VIEW.LEFT)
                frame = image.get_data()

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
                if self.frame_count % 10 == 0:  # Show every 10th frame
                    cv2.imshow("ZED Camera with Skeleton", frame)

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
