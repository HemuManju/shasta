class Sensors(object):
    def __init__(self, p):
        self.p = p
        self.width = 256
        self.height = 256
        self.fov = 120
        self.aspect = 1.0
        self.nearplane = 0.01
        self.farplane = 10.0
        self.projection_matrix = self.p.computeProjectionMatrixFOV(
            self.fov, self.aspect, self.nearplane, self.farplane)

        self.upAxisIndex = 1
        return None

    def get_camera_image(self, target_pos, image_type):
        """Get the camera image of the scene

        Returns
        -------
        tuple
            Three arrays corresponding to rgb, depth, and segmentation image.
        """
        # Get depth values using the OpenGL renderer
        self.view_matrix = self.p.computeViewMatrixFromYawPitchRoll(
            target_pos, self.farplane, 0, 90, 0, self.upAxisIndex)
        width, height, rgbImg, depthImg, segImg = self.p.getCameraImage(
            self.width,
            self.height,
            self.view_matrix,
            self.projection_matrix,
            renderer=self.p.ER_BULLET_HARDWARE_OPENGL)

        if image_type == 'seg':
            image = segImg
        elif image_type == 'depth':
            image = depthImg
        elif image_type == 'rgb':
            image = rgbImg
        else:
            image = [rgbImg, depthImg, segImg]
        return image

    def ray_cast(self):
        raise NotImplementedError
