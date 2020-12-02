import numpy as np
from math import cos, sin


def transformation_matrix(x, y, z, roll, pitch, yaw):
    T = np.array(
        [[
            cos(yaw) * cos(pitch),
            -sin(yaw) * cos(roll) + cos(yaw) * sin(pitch) * sin(roll),
            sin(yaw) * sin(roll) + cos(yaw) * sin(pitch) * cos(roll), x
        ],
         [
             sin(yaw) * cos(pitch),
             cos(yaw) * cos(roll) + sin(yaw) * sin(pitch) * sin(roll),
             -cos(yaw) * sin(roll) + sin(yaw) * sin(pitch) * cos(roll), y
         ], [-sin(pitch),
             cos(pitch) * sin(roll),
             cos(pitch) * cos(yaw), z]])
    return T


def rotation_matrix(roll, pitch, yaw):
    """
    Calculates the ZYX rotation matrix.
    Args
        Roll: Angular position about the x-axis in radians.
        Pitch: Angular position about the y-axis in radians.
        Yaw: Angular position about the z-axis in radians.
    Returns
        3x3 rotation matrix as NumPy array
    """
    R = np.array([[
        cos(yaw) * cos(pitch),
        -sin(yaw) * cos(roll) + cos(yaw) * sin(pitch) * sin(roll),
        sin(yaw) * sin(roll) + cos(yaw) * sin(pitch) * cos(roll)
    ],
                  [
                      sin(yaw) * cos(pitch),
                      cos(yaw) * cos(roll) + sin(yaw) * sin(pitch) * sin(roll),
                      -cos(yaw) * sin(roll) + sin(yaw) * sin(pitch) * cos(roll)
                  ],
                  [-sin(pitch),
                   cos(pitch) * sin(roll),
                   cos(pitch) * cos(yaw)]])
    return R
