import random

import pyzed.sl as sl
import numpy as np
import threading
import socket

from Audio import say
from Joint import Joint
from MP import MP
import Settings as s
import time
import json
import math
import Excel
from ScreenNew import Screen, FullScreenApp, OnePage, TwoPage, ThreePage, FourPage, FivePage, SixPage, SevenPage, \
    EightPage, NinePage, TenPage, Fail, Very_good, Excellent, Well_done, AlmostExcellent
from statistics import mean,stdev
import numpy as np


class Camera(threading.Thread):

    def calc_angle_3d(self, joint1, joint2, joint3):
        # if joint1.is_joint_all_zeros() or joint2.is_joint_all_zeros() or joint3.is_joint_all_zeros():
        #   return None

        a = np.array([joint1.x, joint1.y, joint1.z], dtype=np.float32)  # First
        b = np.array([joint2.x, joint2.y, joint2.z], dtype=np.float32)  # Mid
        c = np.array([joint3.x, joint3.y, joint3.z], dtype=np.float32)  # End

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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 7000)
        self.sock.bind(self.server_address)
        print("CAMERA INITIALIZATION")


    def run(self):
        while True:
            print("CAMERA START")
            medaip = MP()
            medaip.start()
            self.zed = MP.get_zed(medaip)

            while not s.finish_workout:
                time.sleep(0.00000001)  # Prevents the MP to stuck
                if (s.req_exercise != "" and s.demo_finish) or (s.req_exercise=="hello_waving"):
                    ex = s.req_exercise
                    print("CAMERA: Exercise ", ex, " start")
                    time.sleep(1)
                    getattr(self, ex)()
                    print("CAMERA: Exercise ", ex, " done")
                    s.req_exercise = ""
                    s.camera_done = True
            print("Camera Done")


    def get_skeleton_data(self):
            #time.sleep(0.01)
            bodies = sl.Bodies()  # Structure containing all the detected bodies
            body_runtime_param = sl.BodyTrackingRuntimeParameters()
            body_runtime_param.detection_confidence_threshold = 30

            if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
                self.zed.retrieve_bodies(bodies, body_runtime_param)
                body_array = bodies.body_list
                num_of_bodies = len(body_array)

                if num_of_bodies!=0:
                    body = bodies.body_list[0]

                    arr_organs = ['nose', 'neck', 'R_shoulder', 'R_elbow', 'R_wrist', 'L_shoulder', 'L_elbow', 'L_wrist',
                              'R_hip', 'R_knee', 'R_ankle', 'L_hip', 'L_knee', 'L_ankle', 'R_eye', 'L_eye', 'R_ear', 'L_ear']

                   # arr_organs=['', '', '', '', '', '', '', '', '', '', '', '', 'L_shoulder', 'R_shoulder', 'L_elbow', 'R_elbow', 'L_wrist']

                    joints={}
                    i=0
                    for kp_3d in body.keypoint:
                        if 0<=i<=8 or i==11:
                            organ = arr_organs[i]
                            joint = Joint(organ,kp_3d)
                            joints[organ]=joint
                           # joint.__str__()

                        i+=1

                    return joints

                else:
                    return None

            else:
                return None


    def init_position(self):
        # Check user position - so all joints all visible, and all exercise will be able to be recognized.
        init_pos = False
        #say("calibration")
        print("CAMERA: init position - please stand in front of the camera with hands to the sides")

        while not init_pos:
            jd = self.get_skeleton_data()
            if jd is not None:
                count = 0
                for j in jd.values():
                    print(j)
                    if j.visible:
                        count += 1
                angle_right = self.calc_angle_3d(jd["R_hip"], jd["R_shoulder"], jd["R_wrist"])
                print(angle_right)
                angle_left = self.calc_angle_3d(jd["L_hip"], jd["L_shoulder"], jd["L_wrist"])
                print(angle_left)
                if count == len(jd) and angle_right > 80 and angle_left > 80:
                    init_pos = True  # all joints are visible + arms are raised to the sides - position initialized.
            else:  # skeleton is not recognized in frame
                print("user is not recognized")
        #say("calibration_complete")
        s.calibration = True
        print("CAMERA: init position verified")
        time.sleep(2)





    # Close the camera when done
##############self.zed.disable_body_tracking()
##############self.zed.close()

    def change_count_screen(self, count):
        if count == 1:
            s.screen.switch_frame(OnePage)

        if count == 2:
            s.screen.switch_frame(TwoPage)

        if count == 3:
            s.screen.switch_frame(ThreePage)

        if count == 4:
            s.screen.switch_frame(FourPage)

        if count == 5:
            s.screen.switch_frame(FivePage)

        if count == 6:
            s.screen.switch_frame(SixPage)

        if count == 7:
            s.screen.switch_frame(SevenPage)

        if count == 8:
            s.screen.switch_frame(EightPage)

        if count == 9:
            s.screen.switch_frame(NinePage)

        if count == 10:
            s.screen.switch_frame(TenPage)

    def random_encouragement(self):
        enco = ["Well_done", "Very_good", "Excellent"]
        random_class_name = random.choice(enco)
        random_class = globals()[random_class_name]
        random_instance = random_class
        s.screen.switch_frame(random_instance)
        #random_class_name = random.choice(enco)
        #random_class = globals()[random_class_name]
        #random_instance = random_class()
        #return random.choice(enco)

    def end_exercise(self, counter):
        if s.rep - 2 > counter:
            s.screen.switch_frame(Fail)

        if (s.rep - 2) <= counter <= (s.rep - 1):
            s.screen.switch_frame(AlmostExcellent)

        if counter == s.rep:
            self.random_encouragement()

    def exercise_one_angle_3d(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                              use_alternate_angles=False, left_right_differ=False):
        flag = True
        counter = 0
        list_joints = []
        while s.req_exercise == exercise_name:
            joints = self.get_skeleton_data()
            if joints is not None:
                if use_alternate_angles:
                    right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                     joints[str("L_" + joint3)])
                    left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                    joints[str("R_" + joint3)])
                else:
                    right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                     joints[str("R_" + joint3)])
                    left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                    joints[str("L_" + joint3)])

                print(left_angle, " ", right_angle)
                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             right_angle, left_angle]
                list_joints.append(new_entry)


                if right_angle is not None and left_angle is not None:
                    if left_right_differ is False:
                        if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & (not flag):
                            flag = True
                            counter += 1
                            self.change_count_screen(counter)
                            print("counter:" + str(counter))
                        #  if not s.robot_count:
                            say(str(counter))
                        elif (down_lb < right_angle < down_ub) & (down_lb < left_angle < down_ub) & (flag):
                            flag = False

                    else:
                        if (up_lb < right_angle < up_ub) & (down_lb < left_angle < down_ub) & (not flag):
                            flag = True
                            counter += 1
                        #    self.change_count_screen(counter)
                            print("counter:" + str(counter))
                            self.change_count_screen(counter)
                            #  if not s.robot_count:
                            say(str(counter))
                        elif (down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & (flag):
                            flag = False



            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break

        self.end_exercise(counter)



            #else:
             #   s.screen.switch_frame(Fail)

        # s.ex_list.update({exercise_name: counter})
        #Excel.wf_joints(exercise_name, list_joints)

    def exercise_two_angles_3d(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                                   joint4, joint5, joint6, up_lb2, up_ub2, down_lb2, down_ub2, use_alternate_angles=False, left_right_differ=False):
################################################

           # time.sleep(2)
##############################################

            list_first_angle=[]
            list_second_angle=[]
            flag = True
            counter = 0
            list_joints = []
            while s.req_exercise == exercise_name:
                joints = self.get_skeleton_data()
                if joints is not None:
                    right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                     joints[str("R_" + joint3)])
                    left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                    joints[str("L_" + joint3)])
                    if use_alternate_angles:
                        right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                         joints[str("L_" + joint6)])
                        left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                         joints[str("R_" + joint6)])

                       # right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("L_" + joint5)],
                        #                                  joints[str("R_" + joint6)])
                        #left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("R_" + joint5)],
                         #                                joints[str("L_" + joint6)])
                    else:
                        right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                       joints[str("R_" + joint6)])
                        left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                      joints[str("L_" + joint6)])

                    ##############################################################################
                    print(left_angle, " ", right_angle)
                    print(left_angle2, " ", right_angle2)

                    list_first_angle+=[left_angle]
                    list_second_angle+=[left_angle2]




                    ##############################################################################

                    new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                                 joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                                 joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                                 joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                                 right_angle, left_angle, right_angle2, left_angle2]
                    list_joints.append(new_entry)
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
                                s.patient_repititions_counting+=1
                                self.change_count_screen(counter)
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
                                s.patient_repititions_counting+=1
                                self.change_count_screen(counter)
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

            self.end_exercise(counter)
            s.ex_list.update({exercise_name: counter})
            Excel.wf_joints(exercise_name, list_joints)


    def exercise_two_angles_3d_with_axis_check(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                               joint4, joint5, joint6, up_lb2, up_ub2, down_lb2, down_ub2, use_alternate_angles=False,
                               left_right_differ=False):
        ################################################

        # time.sleep(2)
        ##############################################

        list_first_angle = []
        list_second_angle = []
        flag = True
        counter = 0
        list_joints = []
        while s.req_exercise == exercise_name:
            joints = self.get_skeleton_data()
            if joints is not None:
                right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                 joints[str("R_" + joint3)])
                left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                joints[str("L_" + joint3)])
                if use_alternate_angles:
                    right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                      joints[str("L_" + joint6)])
                    left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                     joints[str("R_" + joint6)])

                # right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("L_" + joint5)],
                #                                  joints[str("R_" + joint6)])
                # left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("R_" + joint5)],
                #                                joints[str("L_" + joint6)])
                else:
                    right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                      joints[str("R_" + joint6)])
                    left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                     joints[str("L_" + joint6)])

                ##############################################################################
                print(left_angle, " ", right_angle)
                print(left_angle2, " ", right_angle2)

                list_first_angle += [left_angle]
                list_second_angle += [left_angle2]

                print("left shoulder", joints["L_shoulder"].__str__())
                print("right shoulder", joints["R_shoulder"].__str__())
                print(str(abs(joints["L_shoulder"].x - joints["R_shoulder"].x)))


                ##############################################################################

                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                             joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                             right_angle, left_angle, right_angle2, left_angle2]
                list_joints.append(new_entry)
                if right_angle is not None and left_angle is not None and \
                        right_angle2 is not None and left_angle2 is not None:
                    print("first angle mean: ", np.nanmean(list_first_angle))
                    print("first angle stdev: ", np.nanstd(list_first_angle))
                    print("second angle mean: ", np.nanmean(list_second_angle))
                    print("second angle stdev: ", np.nanstd(list_second_angle))

                    if left_right_differ:
                        if (up_lb < right_angle < up_ub) & (down_lb < left_angle < down_ub) & \
                                (up_lb2 < right_angle2 < up_ub2) & (down_lb2 < left_angle2 < down_ub2) & \
                                (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < 150) & (not flag):
                            flag = True
                            counter += 1
                            s.patient_repititions_counting += 1
                            self.change_count_screen(counter)
                            print("counter:" + str(counter))
                            #  if not s.robot_count:
                            say(str(counter))
                        elif (down_lb < right_angle < down_ub) & (up_lb < left_angle < up_ub) & \
                                (down_lb2 < right_angle2 < down_ub2) & (up_lb2 < left_angle2 < up_ub2) & \
                                (abs(joints["L_shoulder"].x - joints["R_shoulder"].x) < 150) & (flag):
                            flag = False


                    else:
                        if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & \
                                (up_lb2 < right_angle2 < up_ub2) & (up_lb2 < left_angle2 < up_ub2) & (not flag):
                            flag = True
                            counter += 1
                            s.patient_repititions_counting += 1
                            self.change_count_screen(counter)
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

        self.end_exercise(counter)

    # s.ex_list.update({exercise_name: counter})
    # Excel.wf_joints(exercise_name, list_joints)


    def exercise_three_angles_3d(self, exercise_name, joint1, joint2, joint3, up_lb, up_ub, down_lb, down_ub,
                               joint4, joint5, joint6, up_lb2, up_ub2, down_lb2, down_ub2,
                                joint7, joint8, joint9, up_lb3, up_ub3, down_lb3, down_ub3, use_alternate_angles=False,
                               left_right_differ=False):
        ################################################

        #time.sleep(2)
        ##############################################

        flag = True
        counter = 0
        list_joints = []
        while s.req_exercise == exercise_name:
            joints = self.get_skeleton_data()
            if joints is not None:
                right_angle = self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                                 joints[str("R_" + joint3)])
                left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                                joints[str("L_" + joint3)])

                right_angle2 = self.calc_angle_3d(joints[str("R_" + joint4)], joints[str("R_" + joint5)],
                                                 joints[str("R_" + joint6)])
                left_angle2 = self.calc_angle_3d(joints[str("L_" + joint4)], joints[str("L_" + joint5)],
                                                joints[str("L_" + joint6)])

                if use_alternate_angles:
                    right_angle3 = self.calc_angle_3d(joints[str("R_" + joint7)], joints[str("R_" + joint8)],
                                                      joints[str("L_" + joint9)])
                    left_angle3 = self.calc_angle_3d(joints[str("L_" + joint7)], joints[str("L_" + joint8)],
                                                     joints[str("R_" + joint9)])
                else:
                    right_angle3 = self.calc_angle_3d(joints[str("R_" + joint7)], joints[str("R_" + joint8)],
                                                      joints[str("R_" + joint9)])
                    left_angle3 = self.calc_angle_3d(joints[str("L_" + joint7)], joints[str("L_" + joint8)],
                                                     joints[str("L_" + joint9)])

                ##############################################################################
                print(left_angle, " ", right_angle)
                print(left_angle2, " ", right_angle2)
                print(left_angle3, " ", right_angle3)
                ##############################################################################

                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             joints[str("R_" + joint4)], joints[str("R_" + joint5)], joints[str("R_" + joint6)],
                             joints[str("L_" + joint4)], joints[str("L_" + joint5)], joints[str("L_" + joint6)],
                             joints[str("R_" + joint7)], joints[str("R_" + joint8)], joints[str("R_" + joint9)],
                             joints[str("L_" + joint7)], joints[str("L_" + joint8)], joints[str("L_" + joint9)],
                             right_angle, left_angle, right_angle2, left_angle2, right_angle3, left_angle3]
                list_joints.append(new_entry)
                if right_angle is not None and left_angle is not None and \
                        right_angle2 is not None and left_angle2 is not None and \
                        right_angle3 is not None and left_angle3 is not None:

                    if (up_lb < right_angle < up_ub) & (up_lb < left_angle < up_ub) & \
                            (up_lb2 < right_angle2 < up_ub2) & (up_lb2 < left_angle2 < up_ub2) & \
                            (up_lb3 < right_angle3 < up_ub3) & (up_lb3 < left_angle3 < up_ub3) & (not flag):
                        flag = True
                        counter += 1
                        s.patient_repititions_counting += 1
                        print("counter:" + str(counter))
                        self.change_count_screen(counter)
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

        self.end_exercise(counter)

    # s.ex_list.update({exercise_name: counter})
    # Excel.wf_joints(exercise_name, list_joints)


    def exercise_one_angle_3d_by_sides(self, exercise_name, joint1, joint2, joint3, one_lb, one_ub, two_lb, two_ub, side):
        flag = True
        counter = 0
        list_joints = []
        while s.req_exercise == exercise_name:
            joints = self.get_skeleton_data()
            if joints is not None:
                right_angle= self.calc_angle_3d(joints[str("R_" + joint1)], joints[str("R_" + joint2)],
                                          joints[str("R_" + joint3)])

                left_angle = self.calc_angle_3d(joints[str("L_" + joint1)], joints[str("L_" + joint2)],
                                         joints[str("L_" + joint3)])

                new_entry = [joints[str("R_" + joint1)], joints[str("R_" + joint2)], joints[str("R_" + joint3)],
                             joints[str("L_" + joint1)], joints[str("L_" + joint2)], joints[str("L_" + joint3)],
                             right_angle, left_angle]
                list_joints.append(new_entry)

                ##############################################################################
                print(left_angle, " ", right_angle)
                print("left wrist x: ", joints[str("L_wrist")].x)
                print("right wrist x: ", joints[str("R_wrist")].x)

                ##############################################################################

                if side == 'right':
                    if right_angle is not None and left_angle is not None:
                        if (one_lb < right_angle < one_ub) & (joints[str("R_wrist")].x>joints[str("L_wrist")].x) & (not flag):
                            flag = True
                            counter += 1
                            s.patient_repititions_counting += 1
                            print("counter:" + str(counter))
                            self.change_count_screen(counter)
                            # if not s.robot_count:
                            say(str(counter))
                        elif (two_lb < right_angle < two_ub) & (flag):
                            flag = False

                else:
                    if right_angle is not None and left_angle is not None:
                        if (one_lb < left_angle < one_ub) & (joints[str("R_wrist")].x>joints[str("L_wrist")].x)& (not flag):
                            flag = True
                            counter += 1
                            s.patient_repititions_counting += 1
                            print("counter:" + str(counter))
                            self.change_count_screen(counter)
                            #if not s.robot_count:
                            say(str(counter))
                        elif (two_lb < left_angle < two_ub) & (flag):
                            flag = False

            if counter == s.rep:
                s.req_exercise = ""
                s.success_exercise = True
                break

        self.end_exercise(counter)

       # s.ex_list.update({exercise_name: counter})
        #Excel.wf_joints(exercise_name, list_joints)


    def hello_waving(self):  # check if the participant waved
        time.sleep(1)
        #say('ready_wave')
        while s.req_exercise == "hello_waving":
            joints = self.get_skeleton_data()
            if joints is not None:
                right_shoulder = joints[str("R_shoulder")]
                right_wrist = joints[str("R_wrist")]
                if right_shoulder.y > right_wrist.y != 0:
                    s.waved_has_tool = True
                    # print(right_shoulder.y)
                    # print(right_wrist.y)
                    s.req_exercise = ""
######################################################### First set of ball exercises

    def bend_elbows_ball(self):  # EX1
        self.exercise_two_angles_3d("bend_elbows_ball", "shoulder", "elbow", "wrist",140, 180, 10, 50,
                                    "elbow", "shoulder", "hip", 0, 40, 0, 40)

    def raise_arms_above_head_ball(self):  # EX2
        self.exercise_two_angles_3d("raise_arms_above_head_ball", "hip", "shoulder", "elbow", 125, 170, 0, 50,
                                    "shoulder", "elbow", "wrist", 120, 180, 135, 180)

############################לבדוק זוויות כי קשה לי לעשות את התרגיל
    def raise_arms_forward_turn_ball(self):  # EX3
        self.exercise_two_angles_3d_with_axis_check("raise_arms_forward_turn_ball", "shoulder", "elbow","wrist", 130, 180, 140, 180,
                                    "wrist", "hip", "hip",105,140,35,60, True, True)
                                    #"wrist", "hip", "hip",95 ,135 , 35, 70, True, True)



######################################################### Second set of ball exercises

    def open_arms_and_forward_ball(self):  # EX4
        self.exercise_three_angles_3d("open_arms_and_forward_ball", "hip", "shoulder", "elbow", 40, 100, 80, 110,
                                      "shoulder", "elbow", "wrist",0,180,150,180,
                                    "elbow", "shoulder", "shoulder", 60, 135, 160,180,True)
                                    # "shoulder", "elbow", "wrist", 120, 180, 150, 180,
                                    #"hip", "shoulder", "elbow", 60, 90, 80, 110,
                                    #"elbow", "shoulder", "shoulder", 80, 120, 160,180,True)

    def open_arms_above_head_ball(self):  # EX5
        self.exercise_two_angles_3d("open_arms_above_head_ball", "elbow", "shoulder", "hip", 150,180, 80, 110,
                                   "shoulder", "elbow", "wrist", 140, 180, 140, 180)


########################################################### Set with a rubber band

    def open_arms_with_band(self):  # EX6
        self.exercise_two_angles_3d("open_arms_with_band","hip", "shoulder", "wrist", 75, 95, 70, 95,
                                    "wrist", "shoulder", "shoulder", 110,150,70,95,True)

        #"wrist", "shoulder", "shoulder", 100, 160,75, 95, True)

    def open_arms_and_up_with_band(self):  # EX7
        self.exercise_three_angles_3d("open_arms_and_up_with_band", "hip", "shoulder", "wrist", 135, 170, 60, 95,
                                    "shoulder", "elbow", "wrist", 130,180,135,180,
                                    "elbow", "shoulder", "shoulder", 105, 130, 70, 110, True)


    def up_with_band_and_lean(self):  # EX8
        self.exercise_two_angles_3d("up_with_band_and_lean", "shoulder", "elbow", "wrist", 125, 180, 125,180,
                                   "wrist", "hip", "hip", 120, 170, 50, 100, True, True)




################################################# Set with a stick ############################################################################

    def bend_elbows_stick(self):  # EX9
        self.exercise_two_angles_3d("bend_elbows_stick", "shoulder", "elbow", "wrist",150, 180, 10, 50,
                                    "elbow", "shoulder", "hip", 10, 40, 0, 30)

    def bend_elbows_and_up_stick(self):  # EX10
        self.exercise_two_angles_3d("bend_elbows_and_up_stick", "hip", "shoulder", "elbow", 100, 170, 10, 35,
                                 "shoulder", "elbow", "wrist", 120, 170, 30, 75)

    def arms_up_and_down_stick(self):  # EX11
        self.exercise_two_angles_3d("arms_up_and_down_stick", "hip", "shoulder", "elbow", 105, 150, 10, 35,
                                    "wrist", "elbow", "shoulder", 135,180,150,180)

    ############################לבדוק זוויות כי קשה לי לעשות את התרגיל
    def switch_with_stick(self):  # EX12
        self.exercise_two_angles_3d_with_axis_check("switch_with_stick", "shoulder", "elbow", "wrist", 135, 180, 135, 180,
                                    "wrist", "hip", "hip", 95, 130, 35, 70, True, True)

    ################################################# Set of exercises without accessories ############################################################################

    def hands_behind_and_lean_notool(self): # EX13
        self.exercise_two_angles_3d("hands_behind_and_lean_notool", "shoulder", "elbow", "wrist", 15,60,15,60,
                                    "elbow", "shoulder", "hip", 80, 110, 120, 170,False, True)

    #def hands_behind_and_turn_both_sides(self):  # EX14
     #   self.exercise_two_angles_3d("hands_behind_and_turn_both_sides", "elbow", "shoulder", "hip", 140,180,15,100,
      #                              "elbow", "hip", "knee", 130, 115, 80, 105, False, True)

    def right_hand_up_and_bend_notool(self):  # EX15
        self.exercise_one_angle_3d_by_sides("right_hand_up_and_bend_notool", "hip", "shoulder", "wrist", 120, 145, 0, 40, "right")

    def left_hand_up_and_bend_notool(self): #EX16
        self.exercise_one_angle_3d_by_sides("left_hand_up_and_bend_notool", "hip", "shoulder", "wrist", 120, 145, 0, 40, "left")

################################בעייתי כי אפשר לעשות גם תנועה לא מלאה
    def raising_hands_diagonally_notool(self): # EX17
        self.exercise_two_angles_3d_with_axis_check("raising_hands_diagonally_notool", "wrist", "shoulder", "hip", 0, 100, 105, 135,
                                    "elbow", "shoulder", "shoulder", 0, 180, 40, 75, True, True)


if __name__ == '__main__':
    s.exercise_amount = 6
    s.rep = 8
    s.req_exercise = ""
    s.finish_workout = False
    s.waved = False
    s.success_exercise = False
    s.calibration = False
    s.training_done = False
    s.gymmy_done= False
    s.camera_done = False
    s.robot_count = False
    s.demo_finish = True
    s.audio_path = 'audio files/Hebrew/Male/'
    s.screen = Screen()

    c = Camera()
    c.start()
    time.sleep(1)
    c.init_position()

    s.req_exercise = "right_hand_up_and_bend"
    # s.screen.mainloop()
    app = FullScreenApp(s.screen)
    s.screen.mainloop()