
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

        ################################################################
        # Create a ZED camera object

        # Set configuration parameters
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD720
        init.coordinate_system = sl.COORDINATE_SYSTEM.IMAGE
        init.depth_mode = sl.DEPTH_MODE.ULTRA
        init.coordinate_units = sl.UNIT.MILLIMETER
        init.camera_fps = 60
        # if len(sys.argv) >= 2:
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

        # image_size.width = image_size.width
        # image_size.height = image_size.height
        # image_size.height = image_size.height / 2

        # Declare your sl.Mat matrices

        ################################################################
        image = sl.Mat()

        while self.zed.is_opened() and not s.finish_program:

            if self.zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:

                self.zed.retrieve_image(image, sl.VIEW.LEFT)
                # self.zed.retrieve_image(image, sl.VIEW.RIGHT)
                frame = image.get_data()
                cv2.imshow("ZED Camera with Skeleton", frame)

                # Stop MediaPipe:
                key = cv2.waitKey(10)
                if s.finish_program or key == ord('q'):
                    s.finish_program = True
                    break

        self.zed.close()
        print("Camera closed")

    def get_zed(self):
        return self.zed


if __name__ == ('__main__'):
    s.stop = False
    s.finish_workout = False
    mediap = MP()
    mediap.start()