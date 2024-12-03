import copy
import math
import random
from datetime import datetime, timedelta

import pygame
import pyzed.sl as sl
import threading
import socket
from Audio import say, get_wav_duration
from Joint_zed import Joint
from PyZedWrapper import PyZedWrapper
import Settings as s
import time
import Excel
from ScreenNew import Screen, FullScreenApp, OnePage, TwoPage, ThreePage, FourPage, FivePage, SixPage, SevenPage, \
    EightPage, NinePage, TenPage, FailPage, Very_good, Excellent, Well_done, AlmostExcellent
import numpy as np
from openpyxl import Workbook
from scipy.signal import savgol_filter


import numpy as np


class MovingAverageFilter:
    def __init__(self, window_size=3, max_null_extrapolation=50, max_jump=70.0):
        self.window_size = window_size  # Number of previous measurements to consider for moving average
        self.max_null_extrapolation = max_null_extrapolation  # Max nulls before fallback
        self.max_jump = max_jump  # Maximum allowable jump between consecutive positions

        self.previous_positions = []  # Store previous positions for moving average
        self.consecutive_invalid_measurements = 0  # Track consecutive null measurements
        self.last_valid_position = None  # Last valid position used for jump limiting
        self.last_velocity = None  # Track the last calculated velocity

    def update(self, measurement):
        # Handle NaN values or [0, 0, 0] measurements
        if measurement is None or np.any(np.isnan(measurement)) or np.all(np.array(measurement) == 0):
            self.consecutive_invalid_measurements += 1
            print(f"null measurement number: {self.consecutive_invalid_measurements}")

            # Predict next value if within the limit
            if self.last_velocity is not None and self.consecutive_invalid_measurements < self.max_null_extrapolation:
                measurement = self.extrapolate_position()
                print(f"Predicting using velocity: {self.last_velocity}, extrapolated position: {measurement}")
            else:
                # Too many nulls: use last valid position or default to zero if none available
                measurement = self.last_valid_position if self.last_valid_position is not None else np.zeros(3)
                print(f"Too many nulls. Using the last valid measurement: {measurement}")
        else:
            # Reset null count if valid measurement is found
            self.consecutive_invalid_measurements = 0
            self.last_valid_position = measurement
            self.last_velocity = self.calculate_velocity(measurement)

        # Add current measurement and ensure window size is limited
        self.previous_positions.append(measurement)
        if len(self.previous_positions) > self.window_size:
            self.previous_positions.pop(0)

        # Calculate and return the moving average of the stored positions
        return self.calculate_moving_average()

    def limit_jump(self, measurement):
        """Limit the maximum jump between the last valid position and the current measurement."""
        if self.last_valid_position is None:
            return measurement  # No valid previous position, return as is

        # Calculate the distance between the current and last valid position
        distance = np.linalg.norm(measurement - self.last_valid_position)

        # If the distance exceeds the max_jump, clamp it
        if distance > self.max_jump:
            direction = (measurement - self.last_valid_position) / distance  # Unit vector in direction of change
            measurement = self.last_valid_position + direction * self.max_jump  # Clamp to max_jump distance

        return measurement

    def extrapolate_position(self):
        """Extrapolate position based on the last known velocity."""
        if self.last_velocity is None or self.last_valid_position is None:
            return np.zeros(3)  # Fallback to zero if no velocity or position is available

        extrapolated_position = self.last_valid_position + self.last_velocity
        return self.limit_jump(extrapolated_position)  # Ensure no sudden jump

    def calculate_velocity(self, measurement):
        """Calculate the velocity based on the difference from the last valid position."""
        if self.last_valid_position is None:
            return np.zeros(3)  # No velocity if there's no previous position

        # Velocity is the difference between the current and last valid position
        return measurement - self.last_valid_position

    def calculate_moving_average(self):
        """Calculate the moving average of positions in the window."""
        if len(self.previous_positions) == 0:
            return np.zeros(3)  # Return zero if no data is available
        return np.mean(self.previous_positions, axis=0)

    def reset(self):
        """Reset the filter (clear stored positions and last valid measurement)."""
        self.previous_positions.clear()
        self.last_valid_position = None
        self.last_velocity = None
        self.consecutive_invalid_measurements = 0
        print("Filter reset.")


class Camera(threading.Thread):
    def calc_angle_3d(self, joint1, joint2, joint3, joint_name="default"):
        a = np.array([joint1.x, joint1.y, joint1.z], dtype=np.float32)  # First joint
        b = np.array([joint2.x, joint2.y, joint2.z], dtype=np.float32)  # Mid joint
        c = np.array([joint3.x, joint3.y, joint3.z], dtype=np.float32)  # End joint

        ba = a - b
        bc = c - b

        try:
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.degrees(np.arccos(cosine_angle))  # Calculate the angle in degrees

            # If this joint combination has a previous angle, apply the jump limit
            if joint_name in self.previous_angles:
                angle = self.limit_angle_jump(angle, joint_name)

            # Store the current angle as the last valid angle for this joint combination
            self.previous_angles[joint_name] = angle

            return round(angle, 2)

        except Exception as e:
            print(f"Could not calculate the angle for {joint_name}: {e}")
            return None

    def limit_angle_jump(self, angle, joint_name):
        """
        Limit the jump in the angle based on the previous valid angle for this joint combination.
        """
        previous_angle = self.previous_angles[joint_name]

        # If the jump exceeds the max allowed, limit the jump
        if abs(angle - previous_angle) > self.max_angle_jump:
            # Limit the angle jump by clamping it to the max_angle_jump
            direction = 1 if angle > previous_angle else -1
            angle = previous_angle + direction * self.max_angle_jump

        return angle


    def __init__(self):
        threading.Thread.__init__(self)
        # Initialize the ZED camera
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 7000)
        self.sock.bind(self.server_address)
        print("CAMERA INITIALIZATION")
        self.frame_count = 0
        self.start_time = None
        self.joints = {}  # Store joints data
        self.max_angle_jump = 12  # Maximum allowed jump between consecutive angle calculations
        self.previous_angle = {}
        s.general_sayings=["","",""]


    def run(self):
        print("CAMERA START")
        medaip = PyZedWrapper()
        medaip.start()
        self.zed = PyZedWrapper.get_zed(medaip)

        while not s.finish_program:
            time.sleep(0.0001)  # Prevents the MP from being stuck


            if (s.asked_for_measurement):
                time.sleep(9)
                self.dist_list = []  # Store joints data
                for i in range (0,20):
                    self.get_skeleton_data_for_distance_shoulders()

                for i in range(0, 20):  # from 0 to 19
                    self.get_skeleton_data()

                s.average_dist = sum(self.dist_list) / len(self.dist_list)
                print("distance: " + str(s.average_dist))

                s.asked_for_measurement = False


            if (s.req_exercise != "" and s.gymmy_finished_demo) or (s.req_exercise == "hello_waving"):
                ex = s.req_exercise
                print("CAMERA: Exercise ", ex, " start")
                if s.req_exercise != "hello_waving":
                    # audio = s.req_exercise
                    # time.sleep(get_wav_duration(audio) + get_wav_duration("start_ex"))
                    s.max_repetitions_in_training += s.rep  # Number of repetitions expected in this exercise
                self.joints = {}  # Clear joints data for each new exercise
                self.previous_angles={}
                getattr(self, ex)()
                print("CAMERA: Exercise ", ex, " done")
                s.req_exercise = ""
                s.camera_done = True
            else:
                time.sleep(1)  # Prevents the MP from being stuck
        print("Camera Done")


    def get_skeleton_data_for_distance_shoulders(self):
        bodies = sl.Bodies()  # Structure containing all the detected bodies
        body_runtime_param = sl.BodyTrackingRuntimeParameters()
        body_runtime_param.detection_confidence_threshold = 40

        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_bodies(bodies, body_runtime_param)
            body_array = bodies.body_list
            num_of_bodies = len(body_array)
            time.sleep(0.001)

            if num_of_bodies != 0:
                body = bodies.body_list[0]

                for i, kp_3d in enumerate(body.keypoint):
                    if i == 12:
                        l_shoulder_x = kp_3d[0]

                    if i == 13:
                        r_shoulder_x = kp_3d[0]

                self.dist_list.append(copy.deepcopy(abs(l_shoulder_x - r_shoulder_x)))

            else:
                return None

        else:
            return None

    def get_skeleton_data(self):
        bodies = sl.Bodies()  # Structure containing all the detected bodies
        body_runtime_param = sl.BodyTrackingRuntimeParameters()
        body_runtime_param.detection_confidence_threshold = 40

        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_bodies(bodies, body_runtime_param)
            body_array = bodies.body_list
            num_of_bodies = len(body_array)
            time.sleep(0.001)

            if num_of_bodies != 0:
                body = bodies.body_list[0]
                arr_organs = ['pelvis', 'spine_1', 'spine_2', 'spine_3', 'neck', 'nose', 'L_eye', 'R_eye', 'L_ear', 'R_ear',
                              'L_clavicle', 'R_clavicle', 'L_shoulder', 'R_shoulder', 'L_elbow', 'R_elbow', 'L_wrist',
                              'R_wrist', 'L_hip', 'R_hip', 'L_knee', 'R_knee', 'L_ankle', 'R_ankle', 'L_big_toe',
                              'R_big_toe', 'L_small_toe', 'R_small_toe', 'L_heel', 'R_heel', 'L_hand_thumb', 'R_hand_thumb',
                              'L_hand_index', 'R_hand_index', 'L_hand_middle', 'R_hand_middle', 'L_hand_pinky', 'R_hand_pinky']

                for i, kp_3d in enumerate(body.keypoint):
                    organ = arr_organs[i]

                    # If joint already exists, update with the MovingAverageFilter
                    if organ in self.joints:
                        kp_3d_new = self.joints[organ].filter.update(kp_3d)
                        self.joints[organ].x=kp_3d_new[0]
                        self.joints[organ].y=kp_3d_new[1]
                        self.joints[organ].z=kp_3d_new[2]

                    else:
                        # Initialize joint and filter for a new organ
                        joint = Joint(organ, kp_3d)
                        joint.filter = MovingAverageFilter()
                        joint.position = joint.filter.update(kp_3d)
                        self.joints[organ] = joint

                return self.joints

            else:
                time.sleep(0.01)
                return None

        else:
            return None




    # def change_count_screen(self, count):
    #     if count == 1:
    #         s.screen.switch_frame(OnePage)
    #
    #     if count == 2:
    #         s.screen.switch_frame(TwoPage)
    #
    #     if count == 3:
    #         s.screen.switch_frame(ThreePage)
    #
    #     if count == 4:
    #         s.screen.switch_frame(FourPage)
    #
    #     if count == 5:
    #         s.screen.switch_frame(FivePage)
    #
    #     if count == 6:
    #         s.screen.switch_frame(SixPage)
    #
    #     if count == 7:
    #         s.screen.switch_frame(SevenPage)
    #
    #     if count == 8:
    #         s.screen.switch_frame(EightPage)
    #
    #     if count == 9:
    #         s.screen.switch_frame(NinePage)
    #
    #     if count == 10:
    #         s.screen.switch_frame(TenPage)

    # def random_encouragement(self):
    #     enco = ["Well_done", "Very_good", "Excellent"]
    #     random_class_name = random.choice(enco)
    #     random_class = globals()[random_class_name]
    #     random_instance = random_class
    #     s.screen.switch_frame(random_instance)
    #
    #
    # def end_exercise(self, counter):
    #     print(" ")
    #     if s.rep - 2 > counter:
    #         time.sleep(1)
    #         s.screen.switch_frame(FailPage)
    #
    #
    #     if (s.rep - 2) <= counter <= (s.rep - 1):
    #         time.sleep(1)
    #         s.screen.switch_frame(AlmostExcellent)
    #
    #
    #     if counter == s.rep:
    #         time.sleep(1)
    #         self.random_encouragement()

    def sayings_generator(self):
        if s.robot_counter < s.rep-1:
            random_number_for_general_saying = random.randint(1, s.rep*30) #the number of frames probably in an exercise, devided by 6 to have the chance for several sayings

        if random_number_for_general_saying==1 or random_number_for_general_saying==2 and  (datetime.now() - timedelta(seconds=10) < s.last_saying_time):
            random_saying_name = random.choice(self.general_sayings)
            say(random_saying_name)
            s.last_saying_time= datetime.now()


    def exercise_two_angles_3d(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                                   joint4, joint5, joint6, up_lb2, up_ub2, down_lb2, down_ub2, use_alternate_angles=False, left_right_differ=False):

            list_first_angle=[]
            list_second_angle=[]
            flag = True
            counter = 0
            list_joints = []


            while s.req_exercise == exercise_name:
                while s.did_training_paused and not s.stop_requested:
                    time.sleep(0.01)


                #for i in range (1,200):
                joints = self.get_skeleton_data()
                if joints is not None:
                    right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                     joints[str("R_" + joint3)], "R_1")
                    left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                    joints[str("L_" + joint3)], "L_1")
                    if use_alternate_angles:
                        right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                         joints[str("L_" + joint6)], "R_2")
                        left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                         joints[str("R_" + joint6)], "L_2")

                        new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                     joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                     joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("L_" + joint6)],
                                     joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("R_" + joint6)],
                                     right_angle, left_angle, right_angle2, left_angle2]

                        # right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("L_" + joint5)],
                        #                                   joints[str("R_" + joint6)])
                        # left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("R_" + joint5)],
                        #                                  joints[str("L_" + joint6)])
                        #
                        # new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                        #              joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                        #              joints[str("R_" + joint4)], joints[str("L_" + joint5)], joints[str("R_" + joint6)],
                        #              joints[str("L_" + joint4)], joints[str("R_" + joint5)], joints[str("L_" + joint6)],
                        #              right_angle, left_angle, right_angle2, left_angle2]


                    else:
                        right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                       joints[str("R_" + joint6)], "R_2")
                        left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                      joints[str("L_" + joint6)], "L_2")

                        new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                     joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                     joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                     joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                     right_angle, left_angle, right_angle2, left_angle2]

                    ##############################################################################
                    print(str(joints[str("R_" + joint1)]))
                    print(str(joints[str("R_" + joint2)]))
                    print(str(joints[str("R_" + joint3)]))
                    print(str(joints[str("R_" + joint4)]))
                    print(str(joints[str("R_" + joint5)]))
                    print(str(joints[str("R_" + joint6)]))
                    print(str(joints[str("L_" + joint1)]))
                    print(str(joints[str("L_" + joint2)]))
                    print(str(joints[str("L_" + joint3)]))
                    print(str(joints[str("L_" + joint4)]))
                    print(str(joints[str("L_" + joint5)]))
                    print(str(joints[str("L_" + joint6)]))





                    print(left_angle, " ", right_angle)
                    print(left_angle2, " ", right_angle2)

                    list_first_angle.append(left_angle)
                    list_second_angle.append(left_angle2)

                    ##############################################################################

                    list_joints.append(copy.deepcopy(new_entry))

                    #print(str(i))
                    if right_angle is not None and left_angle is not None and \
                            right_angle2 is not None and left_angle2 is not None:
                        print("first angle mean: ", np.nanmean(list_first_angle))
                        print("first angle stdev: ", np.nanstd(list_first_angle))
                        print("second angle mean: ", np.nanmean(list_second_angle))
                        print("second angle stdev: ", np.nanstd(list_second_angle))


                        if left_right_differ:
                            if (up_lb < right_angle < up_ub) & (down_lb < left_angle < down_ub) & \
                                    (up_lb2 < right_angle2 < up_ub2) & (down_lb2 < left_angle2 < down_ub2) & (not flag):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise+=1
                                #self.change_count_screen(counter)
                                print("counter:"+ str(counter))
                              #  if not s.robot_count:
                                say(str(counter))


                            elif (down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (up_lb2 < left_angle2 < up_ub2) & (flag):
                                flag = False


                        else:
                            if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & \
                                    (up_lb2 < right_angle2 < up_ub2) & (up_lb2 < left_angle2 < up_ub2) & (not flag):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise+=1
                                #self.change_count_screen(counter)
                                print("counter:" + str(counter))
                                #  if not s.robot_count:
                                say(str(counter))
                            elif (down_lb < right_angle < down_ub) & (down_lb < left_angle < down_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (down_lb2 < left_angle2 < down_ub2) & (flag):
                                flag = False

                if counter == s.rep:
                    s.req_exercise = ""
                    s.success_exercise = True
                    break
            #self.ezer(list_first_angle)
            #self.end_exercise(counter)
            s.ex_list.update({exercise_name: counter})
            Excel.wf_joints(exercise_name, list_joints)



    def exercise_two_angles_3d_one_side(self, exercise_name, joint1, joint2, joint3, up_lb_right, up_ub_right, down_lb_right, down_ub_right, up_lb_left, up_ub_left, down_lb_left, down_ub_left,
                                   joint4, joint5, joint6, up_lb_right2, up_ub_right2, down_lb_right2, down_ub_right2 , up_lb_left2, up_ub_left2, down_lb_left2, down_ub_left2, use_alternate_angles=False):

            list_first_angle=[]
            list_second_angle=[]
            flag = True
            counter = 0
            list_joints = []


            while s.req_exercise == exercise_name:
                while s.did_training_paused and not s.stop_requested:
                    time.sleep(0.01)


                #for i in range (1,200):
                joints = self.get_skeleton_data()
                if joints is not None:
                    right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                     joints[str("R_" + joint3)], "R_1")
                    left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                    joints[str("L_" + joint3)], "L_1")
                    if use_alternate_angles:
                        right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                         joints[str("L_" + joint6)], "R_2")
                        left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                         joints[str("R_" + joint6)], "L_2")

                        new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                     joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                     joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("L_" + joint6)],
                                     joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("R_" + joint6)],
                                     right_angle, left_angle, right_angle2, left_angle2]




                    else:
                        right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                       joints[str("R_" + joint6)], "R_2")
                        left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                      joints[str("L_" + joint6)], "L_2")

                        new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                     joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                     joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                     joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                     right_angle, left_angle, right_angle2, left_angle2]

                    ##############################################################################
                    print(str(joints[str("R_" + joint1)]))
                    print(str(joints[str("R_" + joint2)]))
                    print(str(joints[str("R_" + joint3)]))
                    print(str(joints[str("R_" + joint4)]))
                    print(str(joints[str("R_" + joint5)]))
                    print(str(joints[str("R_" + joint6)]))
                    print(str(joints[str("L_" + joint1)]))
                    print(str(joints[str("L_" + joint2)]))
                    print(str(joints[str("L_" + joint3)]))
                    print(str(joints[str("L_" + joint4)]))
                    print(str(joints[str("L_" + joint5)]))
                    print(str(joints[str("L_" + joint6)]))





                    print(left_angle, " ", right_angle)
                    print(left_angle2, " ", right_angle2)

                    list_first_angle.append(left_angle)
                    list_second_angle.append(left_angle2)

                    ##############################################################################

                    list_joints.append(copy.deepcopy(new_entry))

                    #print(str(i))
                    if right_angle is not None and left_angle is not None and \
                            right_angle2 is not None and left_angle2 is not None:
                        print("first angle mean: ", np.nanmean(list_first_angle))
                        print("first angle stdev: ", np.nanstd(list_first_angle))
                        print("second angle mean: ", np.nanmean(list_second_angle))
                        print("second angle stdev: ", np.nanstd(list_second_angle))





                    if (up_lb_right < right_angle < up_ub_right) & (up_lb_left < left_angle < up_ub_left) & \
                            (up_lb_right2 < right_angle2 < up_ub_right2) & (up_lb_left2 < left_angle2 < up_ub_left2) & (not flag):
                        flag = True
                        counter += 1
                        s.number_of_repetitions_in_training += 1
                        s.patient_repetitions_counting_in_exercise+=1
                        #self.change_count_screen(counter)
                        print("counter:" + str(counter))
                        #  if not s.robot_count:
                        say(str(counter))
                    elif (down_lb_right < right_angle < down_ub_right) & (down_lb_left < left_angle < down_ub_left) & \
                            (down_lb_right2 < right_angle2 < down_ub_right2) & (down_lb_left2 < left_angle2 < down_ub_left2) & (flag):
                        flag = False

                if counter == s.rep:
                    s.req_exercise = ""
                    s.success_exercise = True
                    break
            #self.ezer(list_first_angle)
            #self.end_exercise(counter)
            s.ex_list.update({exercise_name: counter})
            Excel.wf_joints(exercise_name, list_joints)



    def exercise_two_angles_3d_with_axis_check(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                               joint4, joint5, joint6, up_lb2, up_ub2, down_lb2, down_ub2, use_alternate_angles=False,
                               left_right_differ=False, differ = 50, check_nose = False):

        list_first_angle = []
        list_second_angle = []
        flag = True
        counter = 0
        list_joints = []
        sum_distance_between_shoulders=0
        number_in_distance = 0
        distance_between_shoulders=0

        while s.req_exercise == exercise_name:
            while s.did_training_paused and not s.stop_requested:
                time.sleep(0.01)
        #for i in range (1,100):
            joints = self.get_skeleton_data()
            if joints is not None:
                if number_in_distance<10:
                    sum_distance_between_shoulders+= abs(joints["L_shoulder"].x - joints["R_shoulder"].x)
                    number_in_distance+=1

                if number_in_distance==10:
                    distance_between_shoulders = sum_distance_between_shoulders/10

                print("distance_between_shoulders: "+ str(distance_between_shoulders))

                right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                 joints[str("R_" + joint3)], "R_1")
                left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                joints[str("L_" + joint3)], "L_1")
                if use_alternate_angles:
                    right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                      joints[str("L_" + joint6)], "R_2")
                    left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                     joints[str("R_" + joint6)], "L_2")

                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("L_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("R_" + joint6)],
                                 right_angle, left_angle, right_angle2, left_angle2]


                else:
                    right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                      joints[str("R_" + joint6)], "R_2")
                    left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                     joints[str("L_" + joint6)], "L_2")

                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                 right_angle, left_angle, right_angle2, left_angle2]

                ##############################################################################
                print(left_angle, " ", right_angle)
                print(left_angle2, " ", right_angle2)

                list_first_angle += [left_angle]
                list_second_angle += [left_angle2]

                print("left shoulder", joints["L_shoulder"].__str__())
                print("right shoulder", joints["R_shoulder"].__str__())
                print(str(abs(joints["L_shoulder"].x - joints["R_shoulder"].x)))


                ##############################################################################


                #print(i)
                list_joints.append(copy.deepcopy(new_entry))

                if right_angle is not None and left_angle is not None and \
                        right_angle2 is not None and left_angle2 is not None:
                    print("first angle mean: ", np.nanmean(list_first_angle))
                    print("first angle stdev: ", np.nanstd(list_first_angle))
                    print("second angle mean: ", np.nanmean(list_second_angle))
                    print("second angle stdev: ", np.nanstd(list_second_angle))
                    print("distance between shoulders: "+str(abs(joints["L_shoulder"].x - joints["R_shoulder"].x)))
                    if left_right_differ:
                        if check_nose:
                            if ((up_lb < right_angle < up_ub) & (down_lb < left_angle < down_ub) & \
                                    (up_lb2 < right_angle2 < up_ub2) & (down_lb2 < left_angle2 < down_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < distance_between_shoulders - differ) & \
                                    (joints[str("nose")].y-50>joints[str("R_wrist")].y or joints[str("nose")].y-50>joints[str("L_wrist")].y) & (not flag)):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise += 1
                                #self.change_count_screen(counter)
                                print("counter:" + str(counter))
                                #  if not s.robot_count:
                                say(str(counter))
                            elif (down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (up_lb2 < left_angle2 < up_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < distance_between_shoulders - differ) & \
                                    (joints[str("nose")].y-50>joints[str("R_wrist")].y or joints[str("nose")].y-50>joints[str("L_wrist")].y) & (flag):

                                flag = False


                        else:
                            if (up_lb < right_angle < up_ub) & (down_lb < left_angle < down_ub) & \
                                    (up_lb2 < right_angle2 < up_ub2) & (down_lb2 < left_angle2 < down_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < distance_between_shoulders - differ) & (not flag):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise += 1
                                #self.change_count_screen(counter)
                                print("counter:" + str(counter))
                                #  if not s.robot_count:
                                say(str(counter))
                            elif (down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (up_lb2 < left_angle2 < up_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < distance_between_shoulders - differ) & (flag):
                                flag = False


                    else:
                        if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & \
                                (up_lb2 < right_angle2 < up_ub2) & (up_lb2 < left_angle2 < up_ub2) & (not flag):
                            flag = True
                            counter += 1
                            s.number_of_repetitions_in_training += 1
                            s.patient_repetitions_counting_in_exercise += 1
                            #self.change_count_screen(counter)
                            print("counter:" + str(counter))
                            #  if not s.robot_count:
                            say(str(counter))
                        elif (down_lb < right_angle < down_ub) & (down_lb < left_angle < down_ub) & \
                                (down_lb2 < right_angle2 < down_ub2) & (down_lb2 < left_angle2 < down_ub2) & (flag):
                            flag = False

            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break

        #self.end_exercise(counter)
        s.ex_list.update({exercise_name: counter})
        Excel.wf_joints(exercise_name, list_joints)

    def exercise_three_angles_3d(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                               joint4, joint5, joint6, up_lb2, up_ub2, down_lb2, down_ub2,
                                joint7, joint8, joint9, up_lb3, up_ub3, down_lb3, down_ub3, use_alternate_angles=False,
                               left_right_differ=False):


        flag = True
        counter = 0
        list_joints = []
        while s.req_exercise == exercise_name:
            while s.did_training_paused and not s.stop_requested:
                time.sleep(0.01)
        #for i in range (1,100):
            joints = self.get_skeleton_data()
            if joints is not None:
                right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                 joints[str("R_" + joint3)], "R_1")
                left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                joints[str("L_" + joint3)], "L_1")

                right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                 joints[str("R_" + joint6)], "R_2")
                left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                joints[str("L_" + joint6)], "L_2")

                if use_alternate_angles:
                    right_angle3 = self.calc_angle_3d(joints[str("R_" + joint7)], joints[str("R_" + joint8)],
                                                      joints[str("L_" + joint9)], "R_3")
                    left_angle3 = self.calc_angle_3d(joints[str("L_" + joint7)], joints[str("L_" + joint8)],
                                                     joints[str("R_" + joint9)], "L_3")

                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                 joints[str("R_" + joint7)], joints[str("R_" + joint8)], joints[str("L_" + joint9)],
                                 joints[str("L_" + joint7)], joints[str("L_" + joint8)], joints[str("R_" + joint9)],
                                 right_angle, left_angle, right_angle2, left_angle2, right_angle3, left_angle3]

                else:
                    right_angle3 = self.calc_angle_3d(joints[str("R_" + joint7)], joints[str("R_" + joint8)],
                                                      joints[str("R_" + joint9)], "R_3")
                    left_angle3 = self.calc_angle_3d(joints[str("L_" + joint7)], joints[str("L_" + joint8)],
                                                     joints[str("L_" + joint9)], "L_3")

                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                 joints[str("R_" + joint7)], joints[str("R_" + joint8)], joints[str("R_" + joint9)],
                                 joints[str("L_" + joint7)], joints[str("L_" + joint8)], joints[str("L_" + joint9)],
                                 right_angle, left_angle, right_angle2, left_angle2, right_angle3, left_angle3]

                ##############################################################################
                print(left_angle, " ", right_angle)
                print(left_angle2, " ", right_angle2)
                print(left_angle3, " ", right_angle3)
                print("#######################################")
                ##############################################################################


                list_joints.append(copy.deepcopy(new_entry))

                if right_angle is not None and left_angle is not None and \
                        right_angle2 is not None and left_angle2 is not None and \
                        right_angle3 is not None and left_angle3 is not None:

                    if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & \
                            (up_lb2 < right_angle2 < up_ub2) & (up_lb2 < left_angle2 < up_ub2) & \
                            (up_lb3 < right_angle3 < up_ub3) & (up_lb3 < left_angle3 < up_ub3) & (not flag):
                        flag = True
                        counter += 1
                        s.number_of_repetitions_in_training += 1
                        s.patient_repetitions_counting_in_exercise += 1
                        print("counter:" + str(counter))
                        #self.change_count_screen(counter)
                       # if not s.robot_count:
                        say(str(counter))
                    elif (down_lb < right_angle < down_ub) & (down_lb < left_angle < down_ub) & \
                            (down_lb2 < right_angle2 < down_ub2) & (down_lb2 < left_angle2 < down_ub2) & \
                            (down_lb3 < right_angle3 < down_ub3) & (down_lb3 < left_angle3 < down_ub3) & (flag):
                        flag = False

            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break

        #self.end_exercise(counter)
        s.ex_list.update({exercise_name: counter})
        Excel.wf_joints(exercise_name, list_joints)


    def hand_up_and_band_angles(self, exercise_name, joint1, joint2, joint3, one_lb, one_ub, two_lb, two_ub, side, differ=120):
        flag = True
        counter = 0
        list_joints = []
        distance_between_shoulders = 285
        while s.req_exercise == exercise_name:
            while s.did_training_paused and not s.stop_requested:
                time.sleep(0.01)

            joints = self.get_skeleton_data()
            if joints is not None:
                right_angle= self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                          joints[str("R_" + joint3)], "R_1")

                left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                         joints[str("L_" + joint3)], "L_1")

                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             right_angle, left_angle]

                list_joints.append(copy.deepcopy(new_entry))

                ##############################################################################
                print(left_angle, " ", right_angle)
                print("left wrist x: ", joints[str("R_wrist")].x)
                print("right wrist x: ", joints[str("L_shoulder")].x)
                print("nose: ", joints[str("nose")].y)


                ##############################################################################

                if side == 'right':
                    if right_angle is not None and left_angle is not None:
                        if (one_lb < right_angle < one_ub)  & (joints[str("nose")].y-50>joints[str("R_wrist")].y) & \
                                (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < distance_between_shoulders - differ) & (not flag):
                            flag = True
                            counter += 1
                            s.patient_repetitions_counting_in_exercise += 1
                            s.number_of_repetitions_in_training += 1
                            print("counter:" + str(counter))
                            #self.change_count_screen(counter)
                            # if not s.robot_count:
                            say(str(counter))
                        elif (two_lb < right_angle < two_ub) & (joints[str("R_wrist")].x<joints[str("L_shoulder")].x-400) & (flag):
                            flag = False

                else:
                    if right_angle is not None and left_angle is not None:
                        if (one_lb < left_angle < one_ub) & (joints[str("R_shoulder")].x-50>joints[str("L_wrist")].x)& (joints[str("nose")].y - 50 > joints[str("L_wrist")].y) & \
                                (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < distance_between_shoulders - differ) & (not flag):
                            flag = True
                            counter += 1
                            s.number_of_repetitions_in_training += 1
                            s.patient_repetitions_counting_in_exercise += 1
                            print("counter:" + str(counter))
                            #self.change_count_screen(counter)
                            #if not s.robot_count:
                            say(str(counter))
                        elif (two_lb < left_angle < two_ub) & (joints[str("L_wrist")].x>joints[str("R_shoulder")].x+400) & (flag):
                            flag = False

            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break

        #self.end_exercise(counter)
        s.ex_list.update({exercise_name: counter})
        Excel.wf_joints(exercise_name, list_joints)

    def hello_waving(self):  # check if the participant waved
        while s.req_exercise == "hello_waving":
            joints = self.get_skeleton_data()
            if joints is not None:
                right_shoulder = joints[str("R_shoulder")]
                right_wrist = joints[str("R_wrist")]
                if right_shoulder.y > right_wrist.y != 0:
                    s.waved_has_tool = True
                    s.req_exercise = ""


######################################################### First set of ball exercises

    def ball_bend_elbows(self):  # EX1
        self.exercise_two_angles_3d("ball_bend_elbows", "shoulder", "elbow", "wrist",130, 180, 10, 50,
                                    "elbow", "shoulder", "hip", 0, 70, 0, 70)

    def ball_raise_arms_above_head(self):  # EX2
        self.exercise_two_angles_3d("ball_raise_arms_above_head", "hip", "shoulder", "elbow", 140, 180, 0, 50,
                                    "shoulder", "elbow", "wrist", 120, 180, 135, 180)


    def ball_switch(self):  # EX3
        self.exercise_two_angles_3d_with_axis_check("ball_switch", "shoulder", "elbow","wrist", 0, 180, 120, 180,
                                    "wrist", "hip", "hip",65,120,30,70, True, True)
                                    #"wrist", "hip", "hip",95 ,135 , 35, 70, True, True)




######################################################### Second set of ball exercises

    def ball_open_arms_and_forward(self):  # EX4
        self.exercise_two_angles_3d("ball_open_arms_and_forward", "hip", "shoulder", "elbow", 20, 110, 80, 120,
                                    "elbow", "shoulder", "shoulder", 60, 120, 140,180,True)

    def ball_open_arms_above_head(self):  # EX5
        self.exercise_two_angles_3d("ball_open_arms_above_head", "elbow", "shoulder", "hip", 130,180, 80, 110,
                                   "shoulder", "elbow", "wrist", 130, 180, 130, 180)


########################################################### Set with a rubber band

    def band_open_arms(self):  # EX6
        self.exercise_two_angles_3d("band_open_arms","hip", "shoulder", "wrist", 70, 110, 40, 110,
                                    "wrist", "shoulder", "shoulder", 130,170,0,120,True)

        #"wrist", "shoulder", "shoulder", 100, 160,75, 95, True)

    def band_open_arms_and_up(self):  # EX7
        self.exercise_three_angles_3d("band_open_arms_and_up", "hip", "shoulder", "elbow", 130, 170, 20, 100,
                                    "shoulder", "elbow", "wrist", 130,180,0,180,
                                    "elbow", "shoulder", "shoulder", 110, 160, 70, 120, True)


    def band_up_and_lean(self):  # EX8
        self.exercise_two_angles_3d_with_axis_check("band_up_and_lean", "shoulder", "elbow", "wrist", 125, 180, 125,180,
                                   "elbow", "hip", "hip", 110, 170, 50, 100, True, True,40)

    def band_straighten_left_arm_elbows_bend_to_sides(self):  # EX9
        self.exercise_two_angles_3d_one_side("band_straighten_left_arm_elbows_bend_to_sides", "shoulder", "elbow", "wrist", 0, 65, 0,65, 140,180, 0, 80,
                                   "elbow", "shoulder", "hip", 70, 120, 70, 120, 70, 120,70,120)


    def band_straighten_right_arm_elbows_bend_to_sides(self):  # EX10
        self.exercise_two_angles_3d_one_side("band_straighten_right_arm_elbows_bend_to_sides", "shoulder", "elbow", "wrist", 140, 180, 0,80, 0,65, 0, 65,
                                   "elbow", "shoulder", "hip", 60, 120, 60, 120, 60, 120,60,120)

######################################################  Set with a stick
    def stick_bend_elbows(self):  # EX11
        self.exercise_two_angles_3d("stick_bend_elbows", "shoulder", "elbow", "wrist",135, 180, 10, 45,
                                    "elbow", "shoulder", "hip", 0, 45, 0, 45)

    def stick_bend_elbows_and_up(self):  # EX12
        self.exercise_two_angles_3d("stick_bend_elbows_and_up", "hip", "shoulder", "elbow", 125, 170, 10, 50,
                                 "shoulder", "elbow", "wrist", 130, 180, 30, 75)

    def stick_raise_arms_above_head(self):  # EX13
        self.exercise_two_angles_3d("stick_raise_arms_above_head", "hip", "shoulder", "elbow", 120, 180, 10, 55,
                                    "wrist", "elbow", "shoulder", 135,180,135,180)

    def stick_switch(self):  # EX14
        # self.exercise_two_angles_3d("stick_switch", "shoulder", "elbow", "wrist", 0, 180, 140, 180,
        #                             "wrist", "hip", "hip", 95, 140, 35, 70, True, True)
        self.exercise_two_angles_3d_with_axis_check("stick_switch", "shoulder", "elbow","wrist", 0, 180, 120, 180,
                                    "wrist", "hip", "hip",80,140,10,70, True, True)


    # def stick_bending_forward(self):
    #     self.exercise_two_angles_3d("stick_bending_forward", "wrist", "elbow", "shoulder", 120,180,120,180,
    #                                  "shoulder", "hip", "knee",40,90,105,150)

    def stick_up_and_lean(self):  # EX15
        self.exercise_two_angles_3d_with_axis_check("stick_up_and_lean", "shoulder", "elbow", "wrist", 125, 180, 125, 180,
                                                    "elbow", "hip", "hip", 110, 170, 50, 100, True, True, 40)



    ######################################################  Set with a weights

    def weights_right_hand_up_and_bend(self):  # EX16
        self.hand_up_and_band_angles("weights_right_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0, 180, "right")


    def weights_left_hand_up_and_bend(self):  # EX17
        self.hand_up_and_band_angles("weights_left_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0,
                                            180, "left")

    def weights_open_arms_and_forward(self):  # EX18
        self.exercise_two_angles_3d("weights_open_arms_and_forward", "hip", "shoulder", "elbow", 20, 110, 80, 120,
                                    "elbow", "shoulder", "shoulder", 60, 110, 140, 180, True)

    def weights_abduction(self):  # EX19
        self.exercise_two_angles_3d("weights_abduction" , "shoulder", "elbow", "wrist", 140,180,140,180,
                                        "hip", "shoulder", "elbow", 80,120,0,40)

    ################################################# Set of exercises without equipment
    def notool_hands_behind_and_lean(self): # EX20
        self.exercise_two_angles_3d_with_axis_check("notool_hands_behind_and_lean", "shoulder", "elbow", "wrist", 10,70,10,70,
                                    "elbow", "shoulder", "hip", 80, 110, 125, 170,False, True, 40)
                                    # "elbow", "hip", "hip", 30, 100, 125, 170,True, True)

    def notool_right_hand_up_and_bend(self):  # EX21
        self.hand_up_and_band_angles("notool_right_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0, 180, "right")

    def notool_left_hand_up_and_bend(self): #EX22
        self.hand_up_and_band_angles("notool_left_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0, 180, "left")

    def notool_raising_hands_diagonally(self): # EX23
        self.exercise_two_angles_3d_with_axis_check("notool_raising_hands_diagonally", "wrist", "shoulder", "hip", 0, 100, 105, 135,
                                    #"elbow", "shoulder", "shoulder", 0, 180, 40, 75, True, True)\
                                    "shoulder", "elbow", "wrist", 0,180, 120, 180, False, True,70, True)


    def notool_right_bend_left_up_from_side(self):# EX24
        self.exercise_two_angles_3d_one_side("notool_right_bend_left_up_from_side", "wrist", "elbow", "shoulder", 110, 170, 0,40, 140, 180, 140, 180,
                                             "hip", "shoulder", "elbow", 0, 40, 0, 40, 80, 110, 0, 40)

    def notool_left_bend_right_up_from_side(self):# EX25
        self.exercise_two_angles_3d_one_side("notool_left_bend_right_up_from_side", "wrist", "elbow","shoulder", 140, 180, 140, 180,110, 170, 0, 40,
                                             "hip", "shoulder", "elbow", 80, 110, 0, 40, 0, 40, 0, 40)



if __name__ == '__main__':
    s.camera_num = 1  # 0 - webcam, 2 - second USB in maya's computer

    # Audio variables initialization
    language = 'Hebrew'
    gender = 'Male'
    s.audio_path = 'audio files/' + language + '/' + gender + '/'
    s.picture_path = 'audio files/' + language + '/' + gender + '/'
    # s.str_to_say = ""
    # current_time = datetime.datetime.now()
    # s.participant_code = str(current_time.day) + "." + str(current_time.month) + " " + str(current_time.hour) + "." + \
    # str(current_time.minute) + "." + str(current_time.second)

    s.gymmy_finished_demo = True
    # Training variables initialization
    s.rep = 5
    s.waved = False
    s.success_exercise = False
    s.calibration = False
    s.finish_workout = False
    s.gymmy_done = False
    s.camera_done = False
    s.robot_count = False
    s.demo_finish = False
    s.list_effort_each_exercise = {}
    s.ex_in_training = []
    s.finish_program= False
    # s.exercises_start=False
    s.waved_has_tool = True  # True just in order to go through the loop in Gymmy
    s.max_repetitions_in_training=0
    s.did_training_paused= False
    # Excel variable
    ############################# להוריד את הסולמיות
    s.ex_list = {}
    s.chosen_patient_ID="314808981"
    s.req_exercise = "ball_bend_elbows"
    time.sleep(2)
    s.asked_for_measurement = False
    # Create all components
    s.camera = Camera()
    s.number_of_repetitions_in_training=0
    s.patient_repetitions_counting_in_exercise=0
    s.starts_and_ends_of_stops=[]
    s.starts_and_ends_of_stops.append(datetime.now())

    pygame.mixer.init()
    # Start all threads
    s.camera.start()
    Excel.create_workbook_for_training()  # create workbook in excel for this session
    time.sleep(60)
    s.req_exercise=""
    Excel.success_worksheet()
    # Excel.find_and_add_training_to_patient()
    Excel.close_workbook()


