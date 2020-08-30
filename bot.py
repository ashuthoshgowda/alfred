import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED
import sys, traceback
from select import select
import tty, termios

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import datetime
import os
from image_helper.ImageHelper import capture_image,save_image

from threading import Thread, Lock
mutex = Lock()
lidar_quit_now = False

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
        * shut_motors()
        * read_keyboard_input()
        * fast_mode()
        * slow_mode()
        * record_motion_path()

    Slam Methods:
        * get_lidar_quit()
        * set_lidar_quit()
        * alfred_stats()
        * lidar_sense()
        * lidar_sense_running()
        * lidar_sense_reset()
        * record_map_data()
        * find_path()
        * go_to_path()
        * print_image()
        * start_motor()
        * stop_motor()


    """
    def __init__(self,
                 name,
                 motor_run_time = 0.01,
                 motor_speed = 50,
                 motor_speed_increment = 45,
                 motor_turn_time = 0.01,
                 turn_motor_speed = 250,
                 timeout = 0.1,
                 max_allowed_speed = 180,
                 MAP_SIZE_PIXELS = 500,
                 MAP_SIZE_METERS = 10,
                 LIDAR_DEVICE = '/dev/ttyUSB0',
                 MIN_SAMPLES = 200):
        self.name = name
        self.motor_run_time = motor_run_time
        self.motor_speed = motor_speed
        self.motor_speed_increment = motor_speed_increment
        self.motor_turn_time = motor_turn_time
        self.turn_motor_speed = turn_motor_speed
        self.timeout = timeout
        self.max_allowed_speed = max_allowed_speed
        self.MAP_SIZE_PIXELS = MAP_SIZE_PIXELS
        self.MAP_SIZE_METERS = MAP_SIZE_METERS
        self.LIDAR_DEVICE = LIDAR_DEVICE
        self.MIN_SAMPLES = MIN_SAMPLES
        self.lidar = Lidar(LIDAR_DEVICE)
        # Create an RMHC SLAM object with a laser model and optional robot model
        self.slam = RMHC_SLAM(LaserModel(), self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS)

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


    def turn_towards_theta(self, turn_theta):
        print("Entered Auto Pilot Turning Mode")
        current_theta = self.theta
        while self.theta > current_theta + turn_theta + 20:
            self.turn_left()
            self.alfred_stats(alfred_speed=self.turn_motor_speed)
        while self.theta < current_theta + turn_theta - 20:
            self.turn_right()
            self.alfred_stats(alfred_speed=self.turn_motor_speed)

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

    def read_theta_from_keyboard(self):
        return input("Enter the angle to move to")

    def fast_mode(self):
        print("fast_mode")
        self.motor_speed = 180
        self.motor_speed_increment = 60

    def easy_mode(self):
        print("easy_mode")
        self.motor_speed = 60
        self.motor_speed_increment = 20

    def get_lidar_quit(self):
        mutex.acquire()
        global lidar_quit_now
        return_val = lidar_quit_now
        mutex.release()
        return return_val

    def set_lidar_quit(self, quit_bool):
        mutex.acquire()
        global lidar_quit_now
        lidar_quit_now = quit_bool
        mutex.release()

    def start_motor(self):
        self.lidar.start_motor()

    def stop_motor(self):
        self.lidar.stop_motor()

    def print_image(self):
         # Initialize empty map
        room_image = capture_image(self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS, self.slam)
        save_image(room_image)


    def alfred_stats(self,
                    alfred_speed):

        print("X : {x} , Y : {y},theta : {theta}, \
        Distances Sample Rate : {distance_sample_rate}, \
        Angle Sample Rate : {angle_sample_rate}, \
        Alfred Speed: {alfred_speed} ".format(x=self.x,
                                            y=self.y,
                                            theta=self.theta,
                                            distance_sample_rate =  len(self.distances),
                                            angle_sample_rate = len(self.angles),
                                            alfred_speed = alfred_speed))

    def print_distance_angle(self):
        print("Distance Array {distances}".format(distances=self.distances))
        print("Angle Array {angle}".format(angle=self.angles))
        print(" The theta to turn towards is : " + str(self.angles[self.distances.index(max(self.distances))]))
        self.turn_towards_theta(turn_theta=self.angles[self.distances.index(max(self.distances))])

    def lidar_sense(self, do_plot=False, record_lidar=False):
        self.lidar_thread = Thread(target=self.__lidar_sense, args=[do_plot, record_lidar])
        self.lidar_thread.start()

    def lidar_sense_running(self):
        return self.lidar_thread.isAlive()

    def lidar_sense_reset(self):
        print("Lidar reset - starting")
        self.set_lidar_quit(True)
        self.lidar_thread.join()
        self.set_lidar_quit(False)
        print("Lidar reset - finished")
        self.lidar_sense()

    def __lidar_sense(self, do_plot=False, record_lidar=False):

        # Connect to Lidar unit
        print("Enter Lidar Sense")

        self.lidar.start_motor()

        print("Lidar Info: {}".format(self.lidar.get_info()))
        print("Lidar health: {}".format(self.lidar.get_health()))


        # Initialize an empty trajectory
        trajectory = []

        # Create an iterator to collect scan data from the RPLidar
        iterator = self.lidar.iter_scans(1000)

        # We will use these to store previous scan in case current scan is inadequate
        previous_distances = None
        previous_angles    = None

        # First scan is crap, so ignore it
        next(iterator)
        iter_no = 0

        # if do_plot:
        #     plt.ion()
        #     plt.gray()
        #     plt.show()

        ts = time.time()
        ts_str = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
        data_dir_name = os.path.join(os.getcwd(), "lidar_data")
        data_file_name = os.path.join(data_dir_name, "lidar_" + ts_str + \
            ".txt")
        if record_lidar == True:
            if not os.path.exists(data_dir_name):
                os.mkdir(data_dir_name)
            if os.path.isfile(data_file_name):
                os.remove(data_file_name)
            data_file = open(data_file_name, 'w')

        try:
            print("Entering Lidar Sense")
            while self.get_lidar_quit() == False:

                # Extract (quality, angle, distance) triples from current scan
                items = [item for item in next(iterator)]

                # Extract distances and angles from triples
                self.distances = [item[2] for item in items]
                self.angles    = [item[1] for item in items]

                # Update SLAM with current Lidar scan and scan angles if adequate
                if len(self.distances) > self.MIN_SAMPLES:
                    self.slam.update(self.distances, scan_angles_degrees=self.angles)
                    previous_distances = self.distances
                    previous_angles    = self.angles

                # If not adequate, use previous
                elif previous_distances is not None:
                    print("Not enough samples")
                    self.slam.update(previous_distances, scan_angles_degrees=previous_angles)

                # Get current robot position
                self.x, self.y, self.theta = self.slam.getpos()


                # if do_plot or record_lidar:
                    # Get current map bytes as grayscale

                # if do_plot:
                #     if iter_no % 300 == 0:
                #         plt.imshow(img)
                #         plt.savefig('testIterData.png')
                        # plt.draw()
                        # plt.pause(1)
                # elif record_lidar:
                #     if data_file is not None:
                #         ts_cur_str = str(time.time())
                #         #int.from_bytes(b, byteorder='big', signed=False)
                #         data_file.write(ts_cur_str + " Ds : {}".format(self.distances))
                #         data_file.write("\n")
                #         data_file.write(ts_cur_str + " As : {}".format(self.angles))
                #         data_file.write("\n\n")

        except Exception as e:
            exc_type, ex, tb = sys.exc_info()
            imported_tb_info = traceback.extract_tb(tb)[-1]
            line_number = imported_tb_info[1]
            print_format = '{}: Exception in line: {}, message: {}'
            print(print_format.format(exc_type.__name__, line_number, ex))
            print("Something went wrong with the Lidar, quitting...")

        finally:
            # Shut down the lidar connection
            self.lidar.stop_motor()
            self.lidar.stop()
            self.lidar.disconnect()

            if record_lidar:
                data_file.close()
