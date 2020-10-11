from math import cos, sin


class UaVPDController(object):
    def __init__(self,
                 dynamic_properties,
                 Kp_trans=[1, 1, 1],
                 Kp_rot=[25, 25, 25],
                 Kd_trans=[10, 10, 1]):

        # Proportional coefficients
        self.Kp_x, self.Kp_y, self.Kp_z = Kp_trans[0], Kp_trans[1], Kp_trans[2]
        self.Kp_roll, self.Kp_pitch, self.Kp_yaw = Kp_rot[0], Kp_rot[
            1], Kp_rot[2]
        self.Kd_x, self.Kd_y, self.Kd_z = Kd_trans[0], Kd_trans[1], Kd_trans[2]

        # Set the UAV properties
        self.mass = dynamic_properties['mass']
        self.g = 9.81
        self.des_yaw = 0

        return None

    def compute_torque(self,
                       current_pos,
                       current_orin,
                       desired_pos,
                       current_z_vel=0,
                       desired_vel=[0, 0, 0],
                       desired_acc=[0, 0, 0]):

        # The desired velocities and acceleration are by default zero
        des_x_acc, des_y_acc, des_z_acc = desired_acc[0], desired_acc[
            1], desired_acc[2]
        des_z_vel = desired_vel[2]
        des_z_pos = desired_pos[2]

        # Current pose
        z_pos = current_pos[2]
        roll, pitch, yaw = current_orin[0], current_orin[1], current_orin[2]

        # Calculate thrust
        thrust = self.mass * (self.g + des_z_acc + self.Kp_z *
                              (des_z_pos - z_pos) + self.Kd_z *
                              (des_z_vel - current_z_vel))

        # Calculate torques
        roll_torque = self.Kp_roll * (
            ((des_x_acc * sin(self.des_yaw) - des_y_acc * cos(self.des_yaw)) /
             self.g) - roll)
        pitch_torque = self.Kp_pitch * (
            ((des_x_acc * cos(self.des_yaw) - des_y_acc * sin(self.des_yaw)) /
             self.g) - pitch)
        yaw_torque = self.Kp_yaw * (self.des_yaw - yaw)

        return thrust, roll_torque, pitch_torque, yaw_torque
