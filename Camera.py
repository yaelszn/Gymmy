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
from scipy.signal import savgol_filter


import numpy as np
from scipy.signal import savgol_filter


class CombinedFilter:
    def __init__(self, window_size=5, current_weight=0.2, savgol_window=15, polyorder=2, max_null_extrapolation=100,
                 max_jump=50.0):
        self.window_size = window_size  # Number of previous measurements to consider
        self.current_weight = current_weight  # Weight to place on the current measurement
        self.savgol_window = savgol_window  # Window size for Savitzky-Golay smoothing
        self.polyorder = polyorder  # Polynomial order for Savitzky-Golay filter
        self.max_null_extrapolation = max_null_extrapolation  # Max nulls before fallback
        self.max_jump = max_jump  # Maximum allowable jump between consecutive positions

        self.previous_positions = []  # Store previous positions
        self.consecutive_invalid_measurements = 0  # Track consecutive null measurements
        self.last_valid_position = None  # Last valid position used for smoothing
        self.last_velocity = None  # Track the last calculated velocity

    def update(self, measurement):
        # Handle NaN values or [0, 0, 0] measurements
        if measurement is None or np.any(np.isnan(measurement)) or np.all(np.array(measurement) == 0):
            self.consecutive_invalid_measurements += 1
            print(f"null measurement number: {self.consecutive_invalid_measurements}")

            # Predict next value if within the limit
            if self.last_velocity is not None and self.consecutive_invalid_measurements < self.max_null_extrapolation:
                # Extrapolate based on the last known velocity
                measurement = self.extrapolate_position()
                print(f"Predicting using velocity: {self.last_velocity}, extrapolated position: {measurement}")
            else:
                # Too many nulls: use last valid position or stop extrapolating
                measurement = self.last_valid_position if self.last_valid_position is not None else np.zeros(3)
                print(f"Too many nulls. Using the last valid measurement: {measurement}")

        else:
            # Valid measurement found, reset null count
            self.last_valid_position = measurement
            self.consecutive_invalid_measurements = 0
            self.last_velocity = self.calculate_velocity()

        # Add current measurement and ensure window size is limited
        self.previous_positions.append(measurement)
        if len(self.previous_positions) > self.window_size:
            self.previous_positions.pop(0)

        # Smooth data if enough measurements are available
        if len(self.previous_positions) >= self.savgol_window:
            smoothed_data = self.smooth_data()
            return smoothed_data[-1]  # Return the most recent smoothed value
        else:
            return self.previous_positions[-1]

    def limit_jump(self, measurement):
        """
        Limit the maximum jump between the last valid position and the current measurement.
        """
        if self.last_valid_position is None:
            return measurement  # No valid previous position, return as is

        # Calculate the difference between the current and last valid position
        distance = np.linalg.norm(measurement - self.last_valid_position)

        # If the distance exceeds the max_jump, clamp it
        if distance > self.max_jump:
            # Limit the jump by scaling the change down
            direction = (measurement - self.last_valid_position) / distance  # Unit vector in direction of change
            measurement = self.last_valid_position + direction * self.max_jump  # Clamp to max_jump distance

        return measurement

    def extrapolate_position(self):
        """
        Extrapolate position based on velocity, with velocity decay and a maximum distance cap.
        """
        # Dynamic decay factor based on the number of nulls, with a cap to prevent excessive decay
        base_decay = min(0.2 + (0.05 * self.consecutive_invalid_measurements), 0.7)  # Cap at 0.5

        # Calculate decay factor
        decay_factor = max(0.1, 1 - base_decay * self.consecutive_invalid_measurements)

        # Adjust velocity based on the decay factor
        adjusted_velocity = self.last_velocity * decay_factor

        # Calculate the extrapolated position
        extrapolated_position = self.last_valid_position + adjusted_velocity

        # Cap the maximum distance that can be extrapolated
        max_distance = 50.0  # Define a maximum allowed distance for extrapolation
        total_extrapolated_distance = np.linalg.norm(extrapolated_position - self.last_valid_position)

        if total_extrapolated_distance > max_distance:
            # Limit the extrapolated position to the maximum allowed distance
            extrapolated_position = self.last_valid_position + (
                    adjusted_velocity / total_extrapolated_distance) * max_distance

        return extrapolated_position

    def calculate_velocity(self):
        """
        Calculate the velocity based on the last few valid positions (sliding window).
        """
        if len(self.previous_positions) < 2:
            return np.zeros(3)  # Not enough data for velocity calculation

        # Use a sliding window approach for velocity (considering the last few positions)
        velocity_window = min(3, len(self.previous_positions))  # Use up to 3 positions
        velocity = (self.previous_positions[-1] - self.previous_positions[-velocity_window]) / velocity_window
        return velocity

    def adjust_for_trend(self, measurement):
        """
        Adjust the measurement based on trend detection.
        """
        avg_diff = self.calculate_avg_diff()

        diff_last = np.abs(self.previous_positions[-1] - self.previous_positions[-2])
        diff_second_last = np.abs(self.previous_positions[-2] - self.previous_positions[-3])

        if self.is_downward_trend():
            if np.any(diff_last > diff_second_last):
                return self.previous_positions[-1] - 1.1 * avg_diff  # Accelerating downward
            else:
                return self.previous_positions[-1] - 0.5 * avg_diff  # Decelerating downward
        else:
            if np.any(diff_last > diff_second_last):
                return self.previous_positions[-1] + 1.1 * avg_diff  # Accelerating upward
            else:
                return self.previous_positions[-1] + 0.5 * avg_diff  # Decelerating upward

    def smooth_data(self):
        """
        Apply the Savitzky-Golay filter to smooth the data.
        """
        data = np.array(self.previous_positions)
        smoothed_data = savgol_filter(data, self.savgol_window, self.polyorder, axis=0)
        return smoothed_data

    def calculate_avg_diff(self, window_size=4):
        """
        Calculate the average difference over the last 'window_size' measurements.
        """
        if len(self.previous_positions) < window_size:
            return 0  # Not enough data for average diff

        diffs = np.diff(self.previous_positions[-window_size:], axis=0)
        avg_diff = np.mean(diffs, axis=0)
        return avg_diff

    def is_downward_trend(self, window_size=5):
        """
        Check if the average of the last 'window_size' measurements is decreasing.
        """
        if len(self.previous_positions) < window_size:
            return False  # Not enough data to determine the trend

        avg_previous = np.mean(self.previous_positions[-window_size:-1], axis=0)
        return np.all(avg_previous > self.previous_positions[-1])


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
                        joint.filter = CombinedFilter()
                        joint.position = joint.filter.update(kp_3d)
                        self.joints[organ] = joint

                return self.joints

            else:
                time.sleep(0.01)
                return None

        else:
            return None

    def is_Nan(self, point):
        value1 = float(point[0])
        value2 = float(point[1])
        value3 = float(point[2])

        if math.isnan(value1) and math.isnan(value2) and math.isnan(value3):
            return True

        return False


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


    def exercise_one_angle_3d_by_sides(self, exercise_name, joint1, joint2, joint3, one_lb, one_ub, two_lb, two_ub, side):
        flag = True
        counter = 0
        list_joints = []
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
                        if (one_lb < right_angle < one_ub) & (joints[str("R_wrist")].x>joints[str("L_shoulder")].x+50) & (joints[str("nose")].y-50>joints[str("R_wrist")].y) & (not flag):
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
                        if (one_lb < left_angle < one_ub) & (joints[str("R_shoulder")].x-50>joints[str("L_wrist")].x)& (joints[str("nose")].y - 50 > joints[str("L_wrist")].y) & (not flag):
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

    # def raise_arms_forward_turn_ball(self):  # EX3
    #     self.exercise_two_angles_3d_with_axis_check("raise_arms_forward_turn_ball", "shoulder", "elbow","wrist", 100, 180, 140, 180,
    #                                 "wrist", "hip", "hip",95,140,35,70, True, True)
    #                                 #"wrist", "hip", "hip",95 ,135 , 35, 70, True, True)


    def ball_switch(self):  # EX3
        self.exercise_two_angles_3d_with_axis_check("ball_switch", "shoulder", "elbow","wrist", 0, 180, 120, 180,
                                    "wrist", "hip", "hip",65,120,30,70, True, True)
                                    #"wrist", "hip", "hip",95 ,135 , 35, 70, True, True)


    def ball_hands_up_and_bend_backwards(self):
        self.exercise_two_angles_3d("ball_hands_up_and_bend_backwards", "hip", "shoulder", "elbow", 90,170,90,170,
                                    "shoulder", "elbow", "wrist", 120,180,0,90)

######################################################### Second set of ball exercises

    def ball_open_arms_and_forward(self):  # EX4
        # self.exercise_three_angles_3d("open_arms_and_forward_ball", "hip", "shoulder", "elbow", 40, 110, 80, 120,
        #                               "shoulder", "elbow", "wrist",0,180,140,180,
        #                             "elbow", "shoulder", "shoulder", 60, 100, 130,180,True)

        self.exercise_two_angles_3d("ball_open_arms_and_forward", "hip", "shoulder", "elbow", 20, 110, 80, 120,
                                    "elbow", "shoulder", "shoulder", 60, 120, 140,180,True)
    def ball_open_arms_above_head(self):  # EX5
        self.exercise_two_angles_3d("ball_open_arms_above_head", "elbow", "shoulder", "hip", 145,180, 80, 110,
                                   "shoulder", "elbow", "wrist", 130, 180, 130, 180)


########################################################### Set with a rubber band

    def band_open_arms(self):  # EX6
        self.exercise_two_angles_3d("band_open_arms","hip", "shoulder", "wrist", 70, 110, 40, 110,
                                    "wrist", "shoulder", "wrist", 125,170,0,80,True)

        #"wrist", "shoulder", "shoulder", 100, 160,75, 95, True)

    def band_open_arms_and_up(self):  # EX7
        self.exercise_three_angles_3d("band_open_arms_and_up", "hip", "shoulder", "wrist", 125, 170, 20, 100,
                                    "shoulder", "elbow", "wrist", 130,180,0,180,
                                    "wrist", "shoulder", "shoulder", 110, 160, 70, 130, True)


    def band_up_and_lean(self):  # EX8
        self.exercise_two_angles_3d("band_up_and_lean", "shoulder", "elbow", "wrist", 125, 180, 125,180,
                                   "elbow", "hip", "hip", 115, 170, 50, 90, True, True)




######################################################  Set with a stick
    def stick_bend_elbows(self):  # EX9
        self.exercise_two_angles_3d("stick_bend_elbows", "shoulder", "elbow", "wrist",135, 180, 10, 40,
                                    "elbow", "shoulder", "hip", 0, 45, 0, 45)

    def stick_bend_elbows_and_up(self):  # EX10
        self.exercise_two_angles_3d("stick_bend_elbows_and_up", "hip", "shoulder", "elbow", 125, 170, 10, 50,
                                 "shoulder", "elbow", "wrist", 130, 180, 30, 75)

    def stick_raise_arms_above_head(self):  # EX11
        self.exercise_two_angles_3d("stick_raise_arms_above_head", "hip", "shoulder", "elbow", 120, 180, 10, 55,
                                    "wrist", "elbow", "shoulder", 130,180,130,180)

    def stick_switch(self):  # EX12
        # self.exercise_two_angles_3d("stick_switch", "shoulder", "elbow", "wrist", 0, 180, 140, 180,
        #                             "wrist", "hip", "hip", 95, 140, 35, 70, True, True)
        self.exercise_two_angles_3d_with_axis_check("stick_switch", "shoulder", "elbow","wrist", 0, 180, 120, 180,
                                    "wrist", "hip", "hip",80,140,10,70, True, True)


    def stick_bending_forward(self):
        self.exercise_two_angles_3d("stick_bending_forward", "wrist", "elbow", "shoulder", 120,180,120,180,
                                     "shoulder", "hip", "knee",40,90,105,150)
################################################# Set of exercises without equipment
    def notool_hands_behind_and_lean(self): # EX13
        self.exercise_two_angles_3d("notool_hands_behind_and_lean", "shoulder", "elbow", "wrist", 10,70,10,70,
                                    "elbow", "shoulder", "hip", 80, 110, 125, 170,False, True)
                                    # "elbow", "hip", "hip", 30, 100, 125, 170,True, True)

        #def hands_behind_and_turn_both_sides(self):  # EX14
     #   self.exercise_two_angles_3d("hands_behind_and_turn_both_sides", "elbow", "shoulder", "hip", 140,180,15,100,
      #                              "elbow", "hip", "knee", 130, 115, 80, 105, False, True)

    def notool_right_hand_up_and_bend(self):  # EX14
        self.exercise_one_angle_3d_by_sides("notool_right_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0, 180, "right")

    def notool_left_hand_up_and_bend(self): #EX15
        self.exercise_one_angle_3d_by_sides("notool_left_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0, 180, "left")

    def notool_raising_hands_diagonally(self): # EX16
        self.exercise_two_angles_3d_with_axis_check("notool_raising_hands_diagonally", "wrist", "shoulder", "hip", 0, 100, 105, 135,
                                    #"elbow", "shoulder", "shoulder", 0, 180, 40, 75, True, True)\
                                    "shoulder", "elbow", "wrist", 0,180, 120, 180, False, True,70, True)


    def weights_right_hand_up_and_bend(self):  # EX14
        self.exercise_one_angle_3d_by_sides("weights_right_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0, 180, "right")

    def weights_left_hand_up_and_bend(self):  # EX15
        self.exercise_one_angle_3d_by_sides("weights_left_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 0,
                                            180, "left")


    def weights_raising_hands_diagonally(self): # EX16
        self.exercise_two_angles_3d_with_axis_check("weights_raising_hands_diagonally", "wrist", "shoulder", "hip", 0, 100, 105, 135,
                                    #"elbow", "shoulder", "shoulder", 0, 180, 40, 75, True, True)\
                                    "shoulder", "elbow", "wrist", 0,180, 120, 180, False, True,70, True)

    def weights_bending_forward(self):
        self.exercise_two_angles_3d("weights_bending_forward", "wrist", "elbow", "shoulder", 120,180,120,180,
                                     "shoulder", "hip", "knee",40,90,105,150)


    def help_function(self):
        while True:
            joints = self.get_skeleton_data()
            print(f'R_hand_thumb: {joints["R_hand_thumb"]} ')
            print(f'R_hand_pinky: {joints["R_hand_pinky"]} ')

            # arr_organs = ['pelvis', 'spine_1', 'spine_2', 'spine_3', 'neck', 'nose', 'L_eye', 'R_eye', 'L_ear', 'R_ear',
            #               'L_clavicle', 'R_clavicle', 'L_shoulder', 'R_shoulder', 'L_elbow', 'R_elbow', 'L_wrist',
            #               'R_wrist', 'L_hip', 'R_hip', 'L_knee', 'R_knee', 'L_ankle', 'R_ankle', 'L_big_toe',
            #               'R_big_toe', 'L_small_toe', 'R_small_toe', 'L_heel', 'R_heel', 'L_hand_thumb', 'R_hand_thumb',
            #               'L_hand_index', 'R_hand_index', 'L_hand_middle', 'R_hand_middle', 'L_hand_pinky',
            #               'R_hand_pinky']


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
    s.req_exercise = "weights_bending_forward"
    time.sleep(2)
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
    time.sleep(45)
    s.req_exercise=""
    Excel.success_worksheet()
    # Excel.find_and_add_training_to_patient()
    Excel.close_workbook()


