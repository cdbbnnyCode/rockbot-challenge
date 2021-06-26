import numpy as np

class Robot:
    """Robot: the API to the outside world
    This class provides several methods to drive the on-screen robot, as well as
    a function to request a picture of the field as an OpenCV image.
    """

    def __init__(self, driver):
        """Create a robot instance. This requires an internal driver object, and
        shouldn't be called by external code.
        """
        self.__driver = driver

    def forward(self, distance):
        """Attempt to move the robot forward a specific distance. This method
        blocks (waits) for the robot to finish moving before returning.

        If the move is successful, returns the following data structure:
        ('fwd', {'s': True, 'd': <the distance that you requested>})

        If the move is unsuccessful, however, it returns:
        ('fwd', {'s': False, 'e': <error message>, 'd': <the distance actually moved>})
        If the value of 'e' is 'collision', another element 'c' exists, which
        describes the type of object that the robot is colliding with. This can
        be 'rock', 'barrier', or 'edge'.
        """
        self.__driver.send_command('fwd', {'dist': distance})
        return self.__driver.get_response(True)

    def turn(self, angle):
        """Turn a specific angle (in radians). This method blocks (waits) for
        the robot to finish moving before returning.

        This method always succeeds, and it returns the following:
        ('turn', {'s': True, 'd': <the angle you requested>})
        """
        self.__driver.send_command('turn', {'angle': angle})
        return self.__driver.get_response(True)

    def pick(self):
        """Attempt to pick up a rock. This method blocks (waits) for the operation
        to finish, which normally only takes a few milliseconds.

        If multiple rocks are within the robot's pick-up radius, they are all
        picked up.

        This method returns the following data structure:
        ('pick', {'n': <how many rocks were picked up>})
        """
        self.__driver.send_command('pick', {})
        return self.__driver.get_response(True)

    def request_screenshot(self):
        """Request an image of the field in OpenCV format.

        This function returns a 3-channel, 8-bit-per-channel image (type CV_8UC3)
        in RGB format. User code should convert this to BGR for compatibility
        with other OpenCV functions.

        This method may cause issues if the display has a different color depth
        than 8 bits per channel.

        This method is fairly inefficient, and should not be called many times
        per second.
        """
        return self.__driver.request_screenshot().transpose(1, 0, 2)
