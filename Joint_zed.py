# class represent skeleton joint
import math

class Joint(object):

    def __init__(self, type, kp_3d):
        self.type = type
        #self.kp_3d_joint=kp_3d

        if self.is_Nan(kp_3d):
            self.x = 0
            self.y = 0
            self.z = 0
            self.visible=0

        else:
            self.x = kp_3d[0]
            self.y = kp_3d[1]
            self.z = kp_3d[2]
            self.visible=1

    def __str__(self):
        return self.type+" "+str(self.x)+" "+str(self.y)+" "+str(self.z)

    def joint_to_array(self):
        arr = [self.type, self.x, self.y, self.z]
        return arr

    def is_joint_all_zeros(self):
        if self.x == 0 and self.y == 0 and self.z == 0:
            return True
        else:
            return False


    def is_Nan(self, point):
        value1 = float(point[0])
        value2 = float(point[1])
        value3 = float(point[2])

        if math.isnan(value1) and math.isnan(value2) and math.isnan(value3):
            return True

        return False

