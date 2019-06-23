import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED
import sys
from select import select
import tty, termios

class Bot(object):
    """
    docstring for Bot
    ---------
    Variables
    ---------
    Motor Variables:
        * motor_run_time = 0.01
        * motor_speed = 60
        * motor_speed_increment = 60
        * motor_turn_time = 0.01
        * turn_motor_speed = 200
        * timeout = 0.1
        * max_allowed_speed = 400

    LiDar Variables:
        * MAP_SIZE_PIXELS = 500
        * MAP_SIZE_METERS = 10
        * distances_array
        * angles_array
        * X
        * Y
        * theta

    -------
    Methods
    -------
    Motion Methods:
        * move_forward()
        * move_back()
        * turn_left()
        * turn_right()
        * auto_brake()
        * read_keyboard_input()
        * record_motion_path()

    Slam Methods:
        * record_map_data()
        * find_path()
        * go_to_path()

    """
    def __init__(self,
                 name,
                 motor_run_time = 0.01,
                 motor_speed = 60,
                 motor_speed_increment = 60,
                 motor_turn_time = 0.01,
                 turn_motor_speed = 200,
                 timeout = 0.1,
                 max_allowed_speed = 400):
        self.name = name
        self.motor_run_time = motor_run_time
        self.motor_speed = motor_speed
        self.motor_speed_increment = motor_speed_increment
        self.motor_turn_time = motor_turn_time
        self.turn_motor_speed = turn_motor_speed
        self.timeout = timeout
        self.max_allowed_speed = max_allowed_speed

    def move_forward(self):
        motors.setSpeeds(self.motor_speed, self.motor_speed)
        time.sleep(self.motor_run_time)
        if (self.motor_speed < self.max_allowed_speed):
            self.motor_speed += self.motor_speed_increment

    def move_back(self):
        motors.setSpeeds(self.motor_speed, self.motor_speed)
        time.sleep(self.motor_run_time)
        if (self.motor_speed > -self.max_allowed_speed):
            self.motor_speed -= self.motor_speed_increment

    def turn_left(self):
        motors.setSpeeds(self.turn_motor_speed,-self.turn_motor_speed)
        time.sleep(self.motor_turn_time)

    def turn_right(self):
        motors.setSpeeds(-self.turn_motor_speed,self.turn_motor_speed)
        time.sleep(self.motor_turn_time)

    def auto_brake(self):
        if self.motor_speed > 0:
            self.motor_speed -= self.motor_speed_increment
        elif self.motor_speed < 0:
            self.motor_speed += self.motor_speed_increment
        motors.setSpeeds(self.motor_speed, self.motor_speed)
        time.sleep(self.motor_run_time)

    def shut_motors(self):
        motors.setSpeeds(0, 0)
        motors.disable()

    def read_keyboard_input(self):
        rl, wl, xl = select([sys.stdin], [], [], self.timeout)
        if rl: # some input
            key = sys.stdin.read(1)
        else:
            key = 'b'
        return key
