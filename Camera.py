import copy
import json
import math
import random
from datetime import datetime, timedelta

import pygame
import pyzed.sl as sl
import threading
import socket
from Audio import say, get_wav_duration
from Joint_zed import Joint
from MP import MP
from PyZedWrapper import PyZedWrapper
import Settings as s
import time
import Excel
from ScreenNew import Screen, FullScreenApp
import numpy as np
from openpyxl import Workbook
from scipy.signal import savgol_filter, butter

import numpy as np

# class KalmanFilter:
#     def __init__(self, initial_state=None):
#         self.x = np.zeros(3) if initial_state is None else np.array(initial_state)  # Initial state
#         self.P = np.eye(3) * 10  # Initial covariance
#         self.F = np.eye(3)  # State transition matrix
#         self.H = np.eye(3)  # Observation matrix
#         self.R = np.eye(3) * 0.5  # Measurement noise covariance
#         self.Q = np.eye(3) * 0.5 # Process noise covariance
#
#     def predict(self):
#         self.x = self.F @ self.x  # Predict state
#         self.P = self.F @ self.P @ self.F.T + self.Q  # Predict covariance
#
#     def update(self, z):
#         if z is None or np.any(np.isnan(z)) or len(z) != 3:  # Check for null or invalid measurements
#             print("Invalid or missing measurement, using prediction only.")
#             self.predict()  # Use prediction step only
#             return self.x  # Return the predicted state
#
#         z = np.array(z)
#         y = z - (self.H @ self.x)  # Measurement residual
#         S = self.H @ self.P @ self.H.T + self.R  # Residual covariance
#         K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain
#         self.x = self.x + (K @ y)  # Update state
#         self.P = (np.eye(len(self.P)) - K @ self.H) @ self.P  # Update covariance
#         return self.x



from scipy.signal import butter, filtfilt


class ButterworthFilter:
    def __init__(self, order=2, cutoff=5, fs=25, min_samples=5):
        self.b, self.a = butter(order, cutoff / (0.5 * fs), btype='low', analog=False)
        self.history = []  # Stores previous positions for filtering
        self.min_samples = min_samples  # Avoid filtfilt errors

    def update(self, measurement):
        """Apply Butterworth filter with interpolation for missing values."""
        measurement = np.array(measurement, dtype=np.float32)

        # If measurement is invalid, try interpolation
        if measurement is None or np.any(np.isnan(measurement)) or np.all(measurement == 0):
            if len(self.history) > 1:
                # Interpolate missing value
                measurement = self.interpolate_missing_value()
            else:
                return np.zeros(3)

        # Store last `min_samples` values
        self.history.append(measurement)
        if len(self.history) > self.min_samples:
            self.history.pop(0)

        # If not enough data, return raw measurement
        if len(self.history) < self.min_samples:
            return measurement

        # Apply Butterworth filter
        data = np.array(self.history)
        try:
            filtered_x = filtfilt(self.b, self.a, data[:, 0], padlen=3)
            filtered_y = filtfilt(self.b, self.a, data[:, 1], padlen=3)
            filtered_z = filtfilt(self.b, self.a, data[:, 2], padlen=3)
            return np.array([filtered_x[-1], filtered_y[-1], filtered_z[-1]])
        except ValueError:
            return measurement  # Return unfiltered value if error occurs

    def interpolate_missing_value(self):
        """Interpolates missing values using linear interpolation."""
        if len(self.history) < 2:
            return np.zeros(3)

        last_valid = np.array(self.history[-1])
        second_last_valid = np.array(self.history[-2])

        # Linear interpolation
        interpolated = last_valid + (last_valid - second_last_valid) * 0.5
        return interpolated



class MovingAverageFilter:
    def __init__(self, window_size=3, max_null_extrapolation=500, max_jump=100.0):
        self.window_size = window_size
        self.max_null_extrapolation = max_null_extrapolation
        self.max_jump = max_jump
        self.previous_positions = []
        self.consecutive_invalid_measurements = 0
        self.last_valid_position = None
        self.last_velocity = None

    def update(self, measurement):
        # Convert measurement to NumPy array
        measurement = np.array(measurement, dtype=np.float32)

        # Check for invalid measurements
        if measurement is None or np.any(np.isnan(measurement)) or np.all(measurement == 0):
            self.consecutive_invalid_measurements += 1
            if self.last_velocity is not None and self.consecutive_invalid_measurements < self.max_null_extrapolation:
                measurement = self.extrapolate_position()
            else:
                measurement = self.last_valid_position if self.last_valid_position is not None else np.zeros(3)
        else:
            # Handle sudden jumps
            if self.last_valid_position is not None:
                # Ensure both are NumPy arrays for subtraction
                last_position = np.array(self.last_valid_position, dtype=np.float32)
                if np.linalg.norm(measurement - last_position) > self.max_jump:
                    measurement = last_position
                else:
                    self.consecutive_invalid_measurements = 0
                    self.last_velocity = self.calculate_velocity(measurement)
                    self.last_valid_position = measurement

        # Add to window and trim
        self.previous_positions.append(measurement)
        if len(self.previous_positions) > self.window_size:
            self.previous_positions.pop(0)

        return self.calculate_moving_average()

    def calculate_velocity(self, measurement):
        if self.last_valid_position is None:
            return np.zeros(3)
        # Ensure both are NumPy arrays for subtraction
        last_position = np.array(self.last_valid_position, dtype=np.float32)
        return measurement - last_position

    def extrapolate_position(self):
        if self.last_velocity is None or self.last_valid_position is None:
            return np.zeros(3)
        return self.last_valid_position + self.last_velocity

    def calculate_moving_average(self):
        if len(self.previous_positions) == 0:
            return np.zeros(3)
        return np.mean(np.array(self.previous_positions), axis=0)


class Camera(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 7000)
        self.sock.bind(self.server_address)
        print("CAMERA INITIALIZATION")
        self.frame_count = 0
        self.start_time = None
        self.joints = {}
        self.max_angle_jump = 10
        self.previous_angles = {}
        s.general_sayings = ["", "", ""]
        self.first_coordination_ex = True



    def calc_angle_3d(self, joint1, joint2, joint3, joint_name="default"):
        a = np.array([joint1.x, joint1.y, joint1.z], dtype=np.float32)
        b = np.array([joint2.x, joint2.y, joint2.z], dtype=np.float32)
        c = np.array([joint3.x, joint3.y, joint3.z], dtype=np.float32)

        ba = a - b
        bc = c - b

        try:
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.degrees(np.arccos(cosine_angle))

            if joint_name in self.previous_angles:
                angle = self.limit_angle_jump(angle, joint_name)

            self.previous_angles[joint_name] = angle

            return round(angle, 2)

        except Exception as e:
            print(f"Could not calculate the angle for {joint_name}: {e}")
            return None

    def limit_angle_jump(self, angle, joint_name):
        previous_angle = self.previous_angles[joint_name]
        if abs(angle - previous_angle) > self.max_angle_jump:
            direction = 1 if angle > previous_angle else -1
            angle = previous_angle + direction * self.max_angle_jump
        return angle



    def run(self):
        print("CAMERA START")
        s.zed_camera = PyZedWrapper()
        s.zed_camera.start()

        self.zed = PyZedWrapper.get_zed(s.zed_camera)

        while not s.finish_program:
            time.sleep(0.0001)

            if s.asked_for_measurement:
                time.sleep(9)
                self.dist_list = []

                for i in range(20):
                    self.get_skeleton_data_for_distance_shoulders()

                # Count the number of None values in the list
                none_count = sum(1 for value in self.dist_list if value is None)

                # If more than 10 None values, set average_dist to None
                if none_count > 10:
                    s.average_dist = -1
                else:
                    # Compute the average while ignoring None values
                    valid_values = [value for value in self.dist_list if value is not None]
                    s.average_dist = sum(valid_values) / len(valid_values) if valid_values else None

                print("distance: " + str(s.average_dist))
                s.asked_for_measurement = False



            elif (s.req_exercise != "") or (s.req_exercise == "hello_waving"):
                ex = s.req_exercise


                if s.req_exercise != "hello_waving":
                    s.max_repetitions_in_training += s.rep

                    if self.first_coordination_ex:
                        while not s.explanation_over or not s.gymmy_finished_demo:
                            time.sleep(0.001)

                        time.sleep(get_wav_duration(f'{s.rep}_times')+0.5)

                if s.req_exercise == "notool_right_bend_left_up_from_side" or s.req_exercise == "notool_left_bend_right_up_from_side":  # if this is the fist of the 2, turn into false, and then in the next iteration it will skip the demonstration
                    if self.first_coordination_ex == False:
                        self.first_coordination_ex = True
                    if self.first_coordination_ex == True:
                        self.first_coordination_ex = False


                print("CAMERA: Exercise ", ex, " start")
                self.joints = {}
                self.previous_angles = {}
                getattr(self, ex)()
                print("CAMERA: Exercise ", ex, " done")
                s.req_exercise = ""
                s.camera_done = True


            else:
                time.sleep(1)
        print("Camera Done")

    def get_skeleton_data_for_distance_shoulders(self):
        bodies = sl.Bodies()
        body_runtime_param = sl.BodyTrackingRuntimeParameters()
        body_runtime_param.detection_confidence_threshold = 40

        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_bodies(bodies, body_runtime_param)
            body_array = bodies.body_list

            if body_array:
                body = body_array[0]  # Get the first detected body

                try:
                    # Extract shoulder positions safely
                    l_shoulder_x = body.keypoint[5][0] if body.keypoint[5] is not None else None
                    r_shoulder_x = body.keypoint[2][0] if body.keypoint[2] is not None else None

                    # If either shoulder value is missing, append None
                    if l_shoulder_x is None or r_shoulder_x is None:
                        self.dist_list.append(None)
                    else:
                        self.dist_list.append(abs(l_shoulder_x - r_shoulder_x))

                except (IndexError, TypeError):
                    # Catch any errors due to missing or malformed data
                    self.dist_list.append(None)

            else:
                # No bodies detected, append None
                self.dist_list.append(None)

    def get_skeleton_data(self):
        """
        Capture 3D joint positions from ZED camera and apply both Butterworth and Moving Average filters.
        If one filter fails, use the other. If both work, take the average.
        """
        bodies = sl.Bodies()
        body_runtime_param = sl.BodyTrackingRuntimeParameters()
        body_runtime_param.detection_confidence_threshold = 20
        time.sleep(0.001)

        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_bodies(bodies, body_runtime_param)
            body_array = bodies.body_list
            if body_array:
                body = bodies.body_list[0]

                arr_organs = ["nose", "neck", "R_shoulder", "R_elbow", "R_wrist", "L_shoulder", "L_elbow", "L_wrist",
                              "R_hip", "R_knee", "R_ankle", "L_hip", "L_knee", "L_ankle", "R_eye", "L_eye", "R_ear",
                              "L_ear"]

                for i, kp_3d in enumerate(body.keypoint):
                    organ = arr_organs[i]

                    if organ in self.joints:
                        butter_filtered = self.joints[organ].butter_filter.update(kp_3d)
                        # moving_avg_filtered = self.joints[organ].moving_avg_filter.update(kp_3d)
                        #
                        # # Handling NaNs: If one filter returns NaN, use the other
                        # valid_butter = not np.any(np.isnan(butter_filtered))
                        # valid_moving_avg = not np.any(np.isnan(moving_avg_filtered))
                        #
                        # if valid_butter and valid_moving_avg:
                        #     kp_3d_new = (butter_filtered + moving_avg_filtered) / 2  # Average if both valid
                        # elif valid_butter:
                        #     kp_3d_new = butter_filtered  # Use Butterworth if Moving Average failed
                        # elif valid_moving_avg:
                        #     kp_3d_new = moving_avg_filtered  # Use Moving Average if Butterworth failed
                        # else:
                        #     kp_3d_new = kp_3d  # If both fail, return raw data

                        self.joints[organ].x, self.joints[organ].y, self.joints[organ].z = butter_filtered
                    else:
                        joint = Joint(organ, kp_3d)
                        joint.butter_filter = ButterworthFilter()  # Initialize Butterworth filter
                        joint.moving_avg_filter = MovingAverageFilter()  # Initialize Moving Average filter
                        joint.position = kp_3d  # Store raw position initially
                        self.joints[organ] = joint

                s.latest_keypoints = self.joints
                return self.joints
            else:
                time.sleep(0.01)
                return None
        else:
            return None


    def sayings_generator(self, counter):
        if s.robot_counter < s.rep - 1 and s.robot_counter >= 2:
            random_number_for_general_saying = random.randint(1, s.rep*30)  # Random frame condition

            if (random_number_for_general_saying in range (1,5)) and \
                    datetime.now() - s.last_saying_time >= timedelta(seconds=10):
                if s.general_sayings:  # Ensure the list is not empty
                    # Filter sayings based on the counter condition
                    num = random.randint(2, 5)
                    filtered_sayings = s.general_sayings
                    if s.robot_counter <=2 :
                        filtered_sayings = []

                    else: # אם הרובוט גדול מ-2
                        if s.rep - s.robot_counter > 3 :  # לא לקראת הסוף
                            filtered_sayings = [saying for saying in filtered_sayings if not saying.endswith(("_end", "_end_good"))]
                        else:
                            if s.rep - counter > 4:#אם לקראת הסוף ולא הצלחתי הרבה
                                filtered_sayings = [saying for saying in filtered_sayings if not saying.endswith(("_end_good"))]

                        if counter <= 3: #אם לא עשיתי הרבה חזרות
                            filtered_sayings = [saying for saying in filtered_sayings if not saying.endswith("_middle")]

                        if s.robot_counter - num < counter: #אם הספירה של הרובוט קרובה לספירה של האדם
                            filtered_sayings = [saying for saying in filtered_sayings if not saying.startswith("faster")]



                    if filtered_sayings:  # Ensure the filtered list is not empty
                        random_saying_name = random.choice(filtered_sayings)
                        s.general_sayings.remove(random_saying_name)  # Remove the selected saying
                        say(random_saying_name)  # Call the function to say it
                        s.last_saying_time = datetime.now()

    def fill_null_joint_list(self):
        arr_organs = ["nose", "neck", "R_shoulder", "R_elbow", "R_wrist", "L_shoulder", "L_elbow", "L_wrist",
                      "R_hip", "R_knee", "R_ankle", "L_hip", "L_knee", "L_ankle", "R_eye", "L_eye", "R_ear", "L_ear"]

        for organ in arr_organs:
            joint = Joint(organ, [math.nan, math.nan, math.nan])
            self.joints[organ] = joint

        return self.joints

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

                self.sayings_generator(counter)
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

                        if flag == False:
                            s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), up_lb, up_ub],
                                             [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), up_lb, up_ub],
                                             [str("R_" + joint4), str("R_" + joint5), str("L_" + joint6), up_lb2, up_ub2],
                                             [str("L_" + joint4), str("L_" + joint5), str("R_" + joint6), up_lb2, up_ub2]]
                        else:
                            s.information = [
                                [str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb, down_ub],
                                [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb, down_ub],
                                [str("R_" + joint4), str("R_" + joint5), str("L_" + joint6), down_lb2, down_ub2],
                                [str("L_" + joint4), str("L_" + joint5), str("R_" + joint6), down_lb2, down_ub2]]

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

                        #
                        # # if flag == False:
                        # s.information = [
                        #     [str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb, down_ub],
                        #     [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb, down_ub],
                        #     [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), down_lb2, down_ub2],
                        #     [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), down_lb2, down_ub2]]

                        if flag == False:
                            s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), up_lb, up_ub],
                                             [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), up_lb, up_ub],
                                             [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), up_lb2,up_ub2],
                                             [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), up_lb2, up_ub2]]
                        else:
                            s.information = [
                                    [str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb, down_ub],
                                    [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb, down_ub],
                                    [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), down_lb2, down_ub2],
                                    [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), down_lb2, down_ub2]]

                        # else:



                    s.last_entry_angles = [right_angle, left_angle, right_angle2, left_angle2]

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
                                    (up_lb2 < right_angle2 < up_ub2) & (down_lb2 < left_angle2 < down_ub2) & s.reached_max_limit &(not flag):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise+=1
                                #self.change_count_screen(counter)
                                print("counter:"+ str(counter))
                                s.all_rules_ok = True
                                s.was_in_opposite_limit = False


                            #  if not s.robot_count:
                              #   say(str(counter))


                            elif (down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (up_lb2 < left_angle2 < up_ub2) & (flag):
                                flag = False
                                s.was_in_opposite_limit = True
                                s.all_rules_ok = False

                        else:
                            if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & \
                                    (up_lb2 < right_angle2 < up_ub2) & (up_lb2 < left_angle2 < up_ub2) & s.reached_max_limit & (not flag):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise+=1
                                #self.change_count_screen(counter)
                                print("counter:" + str(counter))
                                #  if not s.robot_count:
                                # say(str(counter))

                                s.all_rules_ok = True
                                s.was_in_opposite_limit = False



                            elif (down_lb < right_angle < down_ub) & (down_lb < left_angle < down_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (down_lb2 < left_angle2 < down_ub2) & (flag):
                                flag = False
                                s.was_in_opposite_limit = True
                                s.all_rules_ok = False

                if counter == s.rep:
                    s.req_exercise = ""
                    s.success_exercise = True
                    break
            #self.ezer(list_first_angle)
            #self.end_exercise(counter)

            if len(list_joints) == 0:
                joints = self.fill_null_joint_list()
                if use_alternate_angles:
                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("L_" + joint6)],
                             joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("R_" + joint6)],
                             None, None, None, None]
                else:
                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                 None, None, None, None]
                list_joints.append(copy.deepcopy(new_entry))

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

                self.sayings_generator(counter)

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

                        if flag == False:
                            s.information = [
                                [str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), up_lb_right, up_ub_right],
                                [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), up_lb_left, up_ub_left],
                                [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), up_lb_right2, up_ub_right2],
                                [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), up_lb_left2, up_ub_left2]]
                        else:
                            s.information = [
                                [str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb_right, down_ub_right],
                                [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb_left, down_ub_left],
                                [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), down_lb_right2, down_ub_right2],
                                [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), down_lb_left2, down_ub_left2]]



                    s.last_entry_angles = [right_angle, left_angle, right_angle2, left_angle2]

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
                            (up_lb_right2 < right_angle2 < up_ub_right2) & (up_lb_left2 < left_angle2 < up_ub_left2) & s.reached_max_limit & (not flag):
                        flag = True
                        counter += 1
                        s.number_of_repetitions_in_training += 1
                        s.patient_repetitions_counting_in_exercise+=1
                        #self.change_count_screen(counter)
                        print("counter:" + str(counter))
                        s.all_rules_ok = True
                        s.was_in_opposite_limit = False

                        #  if not s.robot_count:
                        # say(str(counter))
                    elif (down_lb_right < right_angle < down_ub_right) & (down_lb_left < left_angle < down_ub_left) & \
                            (down_lb_right2 < right_angle2 < down_ub_right2) & (down_lb_left2 < left_angle2 < down_ub_left2) & (flag):
                        flag = False
                        s.was_in_opposite_limit = True
                        s.all_rules_ok = False



                if counter == s.rep:
                    s.req_exercise = ""
                    s.success_exercise = True
                    break
            #self.ezer(list_first_angle)
            #self.end_exercise(counter)
            if len(list_joints) == 0:
                joints = self.fill_null_joint_list()
                if use_alternate_angles:
                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("L_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("R_" + joint6)],
                                 None, None, None, None]
                else:
                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                 None, None, None, None]
                list_joints.append(copy.deepcopy(new_entry))

            s.ex_list.update({exercise_name: counter})
            Excel.wf_joints(exercise_name, list_joints)




    def exercise_two_angles_3d_with_axis_check(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                               joint4, joint5, joint6, up_lb2, up_ub2, down_lb2, down_ub2, use_alternate_angles=False,
                               left_right_differ=False, differ = 50, wrist_check = False):

        list_first_angle = []
        list_second_angle = []
        flag = True
        counter = 0
        list_joints = []


        while s.req_exercise == exercise_name:
            while s.did_training_paused and not s.stop_requested:
                time.sleep(0.01)

            self.sayings_generator(counter)

            #for i in range (1,100):
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

                    if left_right_differ:
                        if flag == False:
                            s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), up_lb, up_ub],
                                             [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb, down_ub],
                                             [str("R_" + joint4), str("R_" + joint5), str("L_" + joint6), up_lb2, up_ub2],
                                             [str("L_" + joint4), str("L_" + joint5), str("R_" + joint6), down_lb2, down_ub2]]

                            s.side = "right"

                        else:

                            s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb, down_ub],
                                             [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), up_lb, up_ub],
                                             [str("R_" + joint4), str("R_" + joint5), str("L_" + joint6), down_lb2,
                                              down_ub2],
                                             [str("L_" + joint4), str("L_" + joint5), str("R_" + joint6), up_lb2,
                                              up_ub2]]

                            s.side = "left"

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

                    # if flag == False:
                    #     s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), up_lb, up_ub],
                    #                      [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), up_lb, up_ub],
                    #                      [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), up_lb2, up_ub2],
                    #                      [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), up_lb2, up_ub2]]
                    # else:
                    #     s.information = [
                    #         [str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb, down_ub],
                    #         [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb, down_ub],
                    #         [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), down_lb2, down_ub2],
                    #         [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), down_lb2, down_ub2]]


                s.last_entry_angles = [right_angle, left_angle, right_angle2, left_angle2]

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

                        if wrist_check:
                            if ((down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (up_lb2 < left_angle2 < up_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < s.dist_between_shoulders - differ) & \
                                    (joints["R_wrist"].x - joints["L_shoulder"].x > 50) & s.reached_max_limit &\
                                    (not flag)):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise += 1
                                #self.change_count_screen(counter)
                                print("counter:" + str(counter))
                                #  if not s.robot_count:
                                # say(str(counter))
                                s.all_rules_ok = True
                                s.was_in_opposite_limit = False

                            elif (up_lb < right_angle < up_ub) & (down_lb < left_angle < down_ub) & \
                                    (up_lb2 < right_angle2 < up_ub2) & (down_lb2 < left_angle2 < down_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < s.dist_between_shoulders - differ) & \
                                    ( joints["R_shoulder"].x-joints["L_wrist"].x > 50)&  s.reached_max_limit & (flag):

                                flag = False
                                s.all_rules_ok = True
                                s.was_in_opposite_limit = True



                        else:
                            if (up_lb < right_angle < up_ub) & (down_lb < left_angle < down_ub) & \
                                    (up_lb2 < right_angle2 < up_ub2) & (down_lb2 < left_angle2 < down_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < s.dist_between_shoulders - differ) & s.reached_max_limit &\
                                    (not flag):
                                flag = True
                                counter += 1
                                s.number_of_repetitions_in_training += 1
                                s.patient_repetitions_counting_in_exercise += 1
                                #self.change_count_screen(counter)
                                print("counter:" + str(counter))
                                #  if not s.robot_count:
                                # say(str(counter))
                                s.all_rules_ok = True
                                s.was_in_opposite_limit = False


                            elif (down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & \
                                    (down_lb2 < right_angle2 < down_ub2) & (up_lb2 < left_angle2 < up_ub2) & \
                                    (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < s.dist_between_shoulders - differ) &  s.reached_max_limit & (flag):
                                flag = False
                                s.all_rules_ok = True
                                s.was_in_opposite_limit = False




                    else:
                        if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & \
                                (up_lb2 < right_angle2 < up_ub2) & (up_lb2 < left_angle2 < up_ub2) &  s.reached_max_limit & (not flag):
                            flag = True
                            counter += 1
                            s.number_of_repetitions_in_training += 1
                            s.patient_repetitions_counting_in_exercise += 1
                            #self.change_count_screen(counter)
                            print("counter:" + str(counter))
                            #  if not s.robot_count:
                            # say(str(counter))
                            s.all_rules_ok = True
                            s.was_in_opposite_limit = True



                        elif (down_lb < right_angle < down_ub) & (down_lb < left_angle < down_ub) & \
                                (down_lb2 < right_angle2 < down_ub2) & (down_lb2 < left_angle2 < down_ub2) &  s.reached_max_limit & (flag):
                            flag = False
                            s.all_rules_ok = True
                            s.was_in_opposite_limit = True

            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break

        if len(list_joints) == 0:
            joints = self.fill_null_joint_list()
            if use_alternate_angles:
                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("L_" + joint6)],
                             joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("R_" + joint6)],
                             None, None, None, None]
            else:
                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                             joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                             None, None, None, None]
            list_joints.append(copy.deepcopy(new_entry))

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

            self.sayings_generator(counter)

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


                    if flag == False:
                        s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), up_lb, up_ub],
                                         [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), up_lb, up_ub],
                                         [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), up_lb2, up_ub2],
                                         [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), up_lb2, up_ub2],
                                         [str("R_" + joint7), str("R_" + joint8), str("L_" + joint9), up_lb3, up_ub3],
                                         [str("L_" + joint7), str("L_" + joint8), str("R_" + joint9), up_lb3, up_ub3]]


                    else:
                        s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb, down_ub],
                                         [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb, down_ub],
                                         [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), down_lb2, down_ub2],
                                         [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), down_lb2, down_ub2],
                                         [str("R_" + joint7), str("R_" + joint8), str("L_" + joint9), down_lb3, down_ub3],
                                         [str("L_" + joint7), str("L_" + joint8), str("R_" + joint9), down_lb3, down_ub3]]




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

                    if flag == False:
                        s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), up_lb, up_ub],
                                         [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), up_lb, up_ub],
                                         [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), up_lb2, up_ub2],
                                         [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), up_lb2, up_ub2],
                                         [str("R_" + joint7), str("R_" + joint8), str("R_" + joint9), up_lb3, up_ub3],
                                         [str("L_" + joint7), str("L_" + joint8), str("L_" + joint9), up_lb3, up_ub3]]


                    else:
                        s.information = [[str("R_" + joint1), str("R_" + joint2), str("R_" + joint3), down_lb, down_ub],
                                         [str("L_" + joint1), str("L_" + joint2), str("L_" + joint3), down_lb, down_ub],
                                         [str("R_" + joint4), str("R_" + joint5), str("R_" + joint6), down_lb2, down_ub2],
                                         [str("L_" + joint4), str("L_" + joint5), str("L_" + joint6), down_lb2, down_ub2],
                                         [str("R_" + joint7), str("R_" + joint8), str("R_" + joint9), down_lb3, down_ub3],
                                         [str("L_" + joint7), str("L_" + joint8), str("L_" + joint9), down_lb3, down_ub3]]


                s.last_entry_angles = [right_angle, left_angle, right_angle2, left_angle2, right_angle3, left_angle3]


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
                            (up_lb3 < right_angle3 < up_ub3) & (up_lb3 < left_angle3 < up_ub3) & s.reached_max_limit &(not flag):
                        flag = True
                        counter += 1
                        s.number_of_repetitions_in_training += 1
                        s.patient_repetitions_counting_in_exercise += 1
                        print("counter:" + str(counter))
                        s.all_rules_ok = True
                        s.was_in_opposite_limit = False
                        #self.change_count_screen(counter)
                       # if not s.robot_count:
                       #  say(str(counter))
                    elif (down_lb < right_angle < down_ub) & (down_lb < left_angle < down_ub) & \
                            (down_lb2 < right_angle2 < down_ub2) & (down_lb2 < left_angle2 < down_ub2) & \
                            (down_lb3 < right_angle3 < down_ub3) & (down_lb3 < left_angle3 < down_ub3) & (flag):
                        flag = False
                        s.all_rules_ok = False
                        s.was_in_opposite_limit = True


            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break


        if len(list_joints) == 0:
            joints = self.fill_null_joint_list()
            if use_alternate_angles:
                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                             joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                             joints[str("R_" + joint7)], joints[str("R_" + joint8)], joints[str("L_" + joint9)],
                             joints[str("L_" + joint7)], joints[str("L_" + joint8)], joints[str("R_" + joint9)],
                             None, None, None, None,  None, None]
            else:
                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                             joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                             joints[str("R_" + joint7)], joints[str("R_" + joint8)], joints[str("R_" + joint9)],
                             joints[str("L_" + joint7)], joints[str("L_" + joint8)], joints[str("L_" + joint9)],
                             None, None, None, None,  None, None]

            list_joints.append(copy.deepcopy(new_entry))

        s.ex_list.update({exercise_name: counter})
        Excel.wf_joints(exercise_name, list_joints)


    def hand_up_and_band_angles(self, exercise_name, joint1, joint2, joint3, one_lb, one_ub, two_lb, two_ub, side, differ=100):
        flag = True
        counter = 0
        list_joints = []
        while s.req_exercise == exercise_name:
            while s.did_training_paused and not s.stop_requested:
                time.sleep(0.01)

            self.sayings_generator(counter)
            joints = self.get_skeleton_data()
            if joints is not None:
                right_angle= self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                          joints[str("R_" + joint3)], "R_1")

                left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                         joints[str("L_" + joint3)], "L_1")

                right_angle_2 = self.calc_angle_3d(joints[str("R_wrist")], joints[str("R_elbow")],
                                          joints[str("R_shoulder")], "R_2")

                left_angle_2 = self.calc_angle_3d(joints[str("L_wrist")], joints[str("L_elbow")],
                                          joints[str("L_shoulder")], "L_2")

                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_wrist")], joints[str("R_elbow")], joints[str("R_shoulder")],
                             joints[str("L_wrist")], joints[str("L_elbow")], joints[str("L_shoulder")],
                             right_angle, left_angle, right_angle_2, left_angle_2]

                list_joints.append(copy.deepcopy(new_entry))

                ##############################################################################
                print(left_angle, " ", right_angle)
                print("second angle: ", left_angle_2, " ", right_angle_2)

                print("left wrist x: ", joints[str("R_wrist")].x)
                print("right wrist x: ", joints[str("L_shoulder")].x)
                print("nose: ", joints[str("nose")].y)


                ##############################################################################

                if side == 'right':
                    if right_angle is not None and left_angle is not None:
                        if (one_lb < right_angle < one_ub)  & (joints["nose"].y-150>joints["R_wrist"].y) & (joints[str("L_shoulder")].x+100<joints[str("R_wrist")].x) &\
                                (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < s.dist_between_shoulders - differ) &  (130 < right_angle_2< 180) & (not flag):
                            flag = True
                            counter += 1
                            s.patient_repetitions_counting_in_exercise += 1
                            s.number_of_repetitions_in_training += 1
                            print("counter:" + str(counter))
                            #self.change_count_screen(counter)
                            # if not s.robot_count:
                            # say(str(counter))
                        elif (two_lb < right_angle < two_ub) & (joints[str("L_shoulder")].x > joints[str("R_wrist")].x)  & (130 < right_angle_2< 180) & (flag):
                            flag = False

                else:
                    if right_angle is not None and left_angle is not None:
                        if (one_lb < left_angle < one_ub) & (joints[str("R_shoulder")].x-100>joints[str("L_wrist")].x)& (joints[str("nose")].y - 150 > joints[str("L_wrist")].y) & \
                                (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < s.dist_between_shoulders - differ) & (130 < left_angle_2< 180) & (not flag):
                            flag = True
                            counter += 1
                            s.number_of_repetitions_in_training += 1
                            s.patient_repetitions_counting_in_exercise += 1
                            print("counter:" + str(counter))
                            #self.change_count_screen(counter)
                            #if not s.robot_count:
                            # say(str(counter))
                        elif (two_lb < left_angle < two_ub) & (joints[str("R_shoulder")].x < joints[str("L_wrist")].x) & (130 < left_angle_2< 180) & (flag):
                            flag = False

            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break

        if len(list_joints) == 0:
            joints = self.fill_null_joint_list()
            new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                         joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                         None, None]
            list_joints.append(copy.deepcopy(new_entry))


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
        self.exercise_two_angles_3d("ball_bend_elbows", "shoulder", "elbow", "wrist", 10, 50, 120, 180,
                                    "elbow", "shoulder", "hip", 0, 70, 0, 70)

    def ball_raise_arms_above_head(self):  # EX2
        self.exercise_two_angles_3d("ball_raise_arms_above_head", "hip", "shoulder", "elbow", 120, 180, 0, 50,
                                    "shoulder", "elbow", "wrist", 120, 180, 135, 180)


    def ball_switch(self):  # EX3
        self.exercise_two_angles_3d_with_axis_check("ball_switch", "shoulder", "elbow","wrist", 0, 180, 135, 180,
                                    "wrist", "hip", "hip",100,160,40,70, True, True, 70)
                                    #"wrist", "hip", "hip",95 ,135 , 35, 70, True, True)


######################################################### Second set of ball exercises

    def ball_open_arms_and_forward(self):  # EX4
        self.exercise_three_angles_3d("ball_open_arms_and_forward", "hip", "shoulder", "elbow", 80, 120,20, 110,
                                    "shoulder", "elbow", "wrist", 155, 180 , 0, 180,
                                    "elbow", "shoulder", "shoulder", 160,180, 60, 120 ,True)

    def ball_open_arms_above_head(self):  # EX5
        self.exercise_two_angles_3d("ball_open_arms_above_head", "elbow", "shoulder", "hip", 135,180, 80, 110,
                                   "shoulder", "elbow", "wrist", 130, 180, 130, 180)


########################################################### Set with a rubber band

    def band_open_arms(self):  # EX6
        self.exercise_two_angles_3d("band_open_arms","hip", "shoulder", "wrist", 70, 120, 40, 120,
                                    "wrist", "shoulder", "shoulder", 140,170,0,125,True)

        #"wrist", "shoulder", "shoulder", 100, 160,75, 95, True)

    def band_open_arms_and_up(self):  # EX7
        self.exercise_three_angles_3d("band_open_arms_and_up", "hip", "shoulder", "elbow", 120, 170, 20, 105,
                                    "shoulder", "elbow", "wrist", 130,180,0,180,
                                    "elbow", "shoulder", "shoulder", 125, 170, 70, 140, True)


    def band_up_and_lean(self):  # EX8
        self.exercise_two_angles_3d_with_axis_check("band_up_and_lean", "shoulder", "elbow", "wrist", 90, 180, 120,180,
                                   "elbow", "hip", "hip", 120, 170, 50, 100, True, True,30)

    def band_straighten_left_arm_elbows_bend_to_sides(self):  # EX9
        self.exercise_two_angles_3d_one_side("band_straighten_left_arm_elbows_bend_to_sides", "shoulder", "elbow", "wrist", 0, 65, 0,65, 140,180, 0, 60,
                                   "elbow", "shoulder", "hip", 60, 120, 60, 120, 60, 120,60,120)


    def band_straighten_right_arm_elbows_bend_to_sides(self):  # EX10
        self.exercise_two_angles_3d_one_side("band_straighten_right_arm_elbows_bend_to_sides", "shoulder", "elbow", "wrist", 140, 180, 0,60, 0,65, 0, 65,
                                   "elbow", "shoulder", "hip", 60, 120, 60, 120, 60, 120,60,120)

######################################################  Set with a stick
    def stick_bend_elbows(self):  # EX11
        self.exercise_two_angles_3d("stick_bend_elbows", "shoulder", "elbow", "wrist",10, 70, 120, 180,
                                    "elbow", "shoulder", "hip", 0, 50, 0, 50)

    def stick_bend_elbows_and_up(self):  # EX12
        self.exercise_two_angles_3d("stick_bend_elbows_and_up", "hip", "shoulder", "elbow", 125, 170, 10, 50,
                                 "shoulder", "elbow", "wrist", 130, 180, 30, 75)

    def stick_raise_arms_above_head(self):  # EX13
        self.exercise_two_angles_3d("stick_raise_arms_above_head", "hip", "shoulder", "elbow", 120, 180, 10, 55,
                                    "wrist", "elbow", "shoulder", 125,180,125,180)

    def stick_switch(self):  # EX14
        # self.exercise_two_angles_3d("stick_switch", "shoulder", "elbow", "wrist", 0, 180, 140, 180,
        #                             "wrist", "hip", "hip", 95, 140, 35, 70, True, True)
        self.exercise_two_angles_3d_with_axis_check("stick_switch", "shoulder", "elbow","wrist", 0, 180, 120, 180,
                                    "wrist", "hip", "hip",85,160,10,70, True, True, 70)


    # def stick_bending_forward(self):
    #     self.exercise_two_angles_3d("stick_bending_forward", "wrist", "elbow", "shoulder", 120,180,120,180,
    #                                  "shoulder", "hip", "knee",40,90,105,150)....

    def stick_up_and_lean(self):  # EX15
        self.exercise_two_angles_3d_with_axis_check("stick_up_and_lean", "shoulder", "elbow", "wrist", 110, 180, 110, 180,
                                                    "elbow", "hip", "hip", 110, 170, 50, 105, True, True, 30)



    ######################################################  Set with a weights

    def weights_right_hand_up_and_bend(self):  # EX16
        self.hand_up_and_band_angles("weights_right_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 140, 180, "right")


    def weights_left_hand_up_and_bend(self):  # EX17
        self.hand_up_and_band_angles("weights_left_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 140,
                                            180, "left")

    def weights_open_arms_and_forward(self):  # EX18
        self.exercise_two_angles_3d("weights_open_arms_and_forward", "hip", "shoulder", "elbow", 20, 110, 80, 120,
                                    "elbow", "shoulder", "shoulder", 60, 125, 150, 180, True)

    def weights_abduction(self):  # EX19
        self.exercise_two_angles_3d("weights_abduction" , "shoulder", "elbow", "wrist", 140,180,140,180,
                                        "hip", "shoulder", "elbow", 80,120,0,40)

    ################################################# Set of exercises without equipment
    def notool_hands_behind_and_lean(self): # EX20
        self.exercise_two_angles_3d_with_axis_check("notool_hands_behind_and_lean", "shoulder", "elbow", "wrist", 10,70,10,70,
                                    "elbow", "hip", "hip", 120, 170, 80, 120,True, True, 30)
                                    # "elbow", "hip", "hip", 30, 100, 125, 170,True, True)

    def notool_right_hand_up_and_bend(self):  # EX21
        self.hand_up_and_band_angles("notool_right_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 140, 180, "right")

    def notool_left_hand_up_and_bend(self): #EX22
        self.hand_up_and_band_angles("notool_left_hand_up_and_bend", "hip", "shoulder", "wrist", 120, 160, 140, 180, "left")

    def notool_raising_hands_diagonally(self): # EX23
        self.exercise_two_angles_3d_with_axis_check("notool_raising_hands_diagonally", "wrist", "shoulder", "hip", 80, 135, 105, 150,
                                    #"elbow", "shoulder", "shoulder", 0, 180, 40, 75, True, True)\
                                    "shoulder", "elbow", "wrist", 0,180, 120, 180, False,  True,70, True)


    def notool_right_bend_left_up_from_side(self):# EX24
        self.exercise_two_angles_3d_one_side("notool_right_bend_left_up_from_side", "wrist", "elbow", "shoulder", 95, 170, 0,40, 140, 180, 140, 180,
                                             "hip", "shoulder", "elbow", 0, 60, 0, 60, 80, 120, 0, 50)

    def notool_left_bend_right_up_from_side(self):# EX25
        self.exercise_two_angles_3d_one_side("notool_left_bend_right_up_from_side", "wrist", "elbow","shoulder", 140, 180, 140, 180,95, 170, 0, 40,
                                             "hip", "shoulder", "elbow", 80, 120, 0, 50, 0, 60, 0, 60)



if __name__ == '__main__':
    s.camera_num = 1  # 0 - webcam, 2 - second USB in maya's computer
    s.robot_counter = 0
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
    s.chosen_patient_ID="3333"
    s.req_exercise = "band_up_and_lean"
    s.explanation_over = True
    time.sleep(2)
    s.asked_for_measurement = False
    # Create all components
    s.camera = Camera()
    s.number_of_repetitions_in_training=0
    s.patient_repetitions_counting_in_exercise=0
    s.starts_and_ends_of_stops=[]
    s.starts_and_ends_of_stops.append(datetime.now())
    s.dist_between_shoulders =280
    pygame.mixer.init()
    # Start all threads
    s.camera.start()
    Excel.create_workbook_for_training()  # create workbook in excel for this session
    time.sleep(30)
    s.req_exercise=""
    # Excel.find_and_add_training_to_patient()
    Excel.close_workbook()

