import pyzed.sl as sl
import numpy as np
import threading
import socket
from MP import MP
import Settings as s
import time


class Camera(threading.Thread):

    def calc_angle_3d(self, joint1, joint2, joint3):
        #if joint1.is_joint_all_zeros() or joint2.is_joint_all_zeros() or joint3.is_joint_all_zeros():
         #   return None

        a = joint1 # First
        b = joint2  # Mid
        c = joint3  # End

        ba = a - b
        bc = c - b
        try:
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(cosine_angle)
            return round(np.degrees(angle), 2)

        except:
            print("could not calculate the angle")
            return None




    #camera initialization
    def __init__(self):
        threading.Thread.__init__(self)
        # Initialize the ZED camera
        self.zed = sl.Camera()
        self.initialize_camera()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 7000)
        self.sock.bind(self.server_address)



    def initialize_camera(self):
        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD720  # Use HD720 video mode
        init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
        init_params.coordinate_units = sl.UNIT.METER
        init_params.sdk_verbose = True

        # Open the camera
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)


        # Define the Objects detection module parameters
        body_params = sl.BodyTrackingParameters()
        # Set runtime parameters for body tracking
        body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_ACCURATE
        body_params.enable_tracking = True
        body_params.image_sync = True
        #body_params.enable_segmentation = False
        body_params.enable_body_fitting = True
        body_params.body_format = sl.BODY_FORMAT.BODY_34

        # grab runtime parameters
        runtime_params = sl.RuntimeParameters()
        runtime_params.measure3D_reference_frame = sl.REFERENCE_FRAME.WORLD

        # if detection_parameters.enable_tracking:
        # Set positional tracking parameters
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        # Enable positional tracking
        self.zed.enable_positional_tracking(positional_tracking_parameters)

        self.body_runtime_param = sl.BodyTrackingRuntimeParameters()
        self.body_runtime_param.detection_confidence_threshold = 40

        # Enable body tracking
        zed_error = self.zed.enable_body_tracking(body_params)
        if zed_error != sl.ERROR_CODE.SUCCESS:
            print("enable_body_tracking", zed_error, "\nExit program.")
            self.zed.close()
            exit(-1)



        print("CAMERA INITIALIZATION")





    def get_skeleton_data(self):
        self.sock.settimeout(1)

        try:
                if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
                    self.zed.retrieve_bodies(self.bodies, self.body_runtime_param)

                    body_array = self.bodies.body_list
                    i = len(body_array)
                    # if bodies.is_new:
                    print(str(i) + " Person(s) detected\n")

                    if i > 1:
                        print("more then one person detected, try again!")
                        return 2

                    if i==1:
                        return 1

                    else:
                        print("no person detected, try again!")
                        return 0


        except socket.timeout:  # fail after 1 second of no activity
            print("Didn't receive data! [Timeout]")
            return None




    def init_position(self):

        # Check user position - so all joints all visible, and all exercise will be able to be recognized.
        init_pos = False
        ##### say("calibration")
        print("CAMERA: init position - please stand in front of the camera with hands to the sides")
        self.bodies = sl.Bodies()  # Structure containing all the detected bodies

        while not init_pos:
            sk_data =self.get_skeleton_data()

            if sk_data is not None and sk_data==1:
                body_array = self.bodies.body_list
                jd=body_array[0]


                all_body = False
                while all_body == False:
                    was_null = False
                    for kp_3d in body_array[0].keypoint:
                        if kp_3d is None:
                            was_null = True

                    if was_null == False:
                        all_body = True


                angle_right = self.calc_angle_3d(jd.keypoint['R_shoulder'], jd.keypoint['R_hip'], jd.keypoint['R_wrist'])
                angle_left = self.calc_angle_3d(jd['L_Shoulder'], jd["L_Hip"], jd["L_Wrist"])
                if all_body and angle_right > 80 and angle_left > 80:
                    init_pos = True  # all joints are visible + arms are raised to the sides - position initialized.
            else:  # skeleton is not recognized in frame
                print("user is not recognized")
        #say("calibration_complete")
        s.calibration = True
        print("CAMERA: init position verified")












# Close the camera when done
##############self.zed.disable_body_tracking()
##############self.zed.close()




    def run(self):
        print("CAMERA START")
        medaip = MP()
        medaip.start()



if __name__ == '__main__':
        c = Camera()
        c.start()
        c.init_position()