
class Robot:
    def __init__(self, driver):
        self.__driver = driver

    def forward(self, distance):
        self.__driver.send_command('fwd', {'dist': distance})
        return self.__driver.get_response(True)

    def turn(self, angle, wait=True):
        self.__driver.send_command('turn', {'angle': angle})
        return self.__driver.get_response(True)

    def pick(self):
        self.__driver.send_command('pick', {})
        return self.__driver.get_response(True)

    def request_screenshot(self):
        return self.__driver.request_screenshot()
