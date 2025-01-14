# class represent skeleton joint
import math



class Joint:
    def __init__(self, type, *args):
        """
        Initialize a Joint object.

        Parameters:
        - type: str, the type of the joint
        - *args: either a list or tuple (kp_3d) or three separate values (x, y, z)
        """
        self.type = type
        self.position = []  # Initialize an empty list to store previous positions

        if len(args) == 1 and isinstance(args[0], (list, tuple)):  # `kp_3d` option
            kp_3d = args[0]
            if self.is_nan(kp_3d[0]) or self.is_nan(kp_3d[1]) or self.is_nan(kp_3d[2]):
                self.x = 0
                self.y = 0
                self.z = 0
                self.visible = 0
            else:
                self.x, self.y, self.z = kp_3d
                self.visible = 1

        elif len(args) == 3:  # `x, y, z` option
            x, y, z = args
            if self.is_nan(x) or self.is_nan(y) or self.is_nan(z):
                self.x = 0
                self.y = 0
                self.z = 0
                self.visible = 0
            else:
                self.x = x
                self.y = y
                self.z = z
                self.visible = 1
        else:
            raise ValueError("Invalid arguments. Provide either kp_3d (list/tuple) or x, y, z values.")

    @staticmethod
    def is_nan(value):
        """Check if a value is NaN."""
        return value != value  # NaN is not equal to itself

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

