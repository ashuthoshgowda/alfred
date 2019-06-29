
MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 10
LIDAR_DEVICE            = '/dev/ttyUSB0'


# Ideally we could use all 250 or so samples that the RPLidar delivers in one
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES   = 200

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar

import matplotlib.pyplot as plt
import time
import datetime
import os

from threading import Lock
mutex = Lock()

lidar_quit_now = False

def get_lidar_quit():
    mutex.acquire()
    global lidar_quit_now
    return_val = lidar_quit_now
    mutex.release()
    return return_val
    
def set_lidar_quit(quit_bool):
    mutex.acquire()
    global lidar_quit_now
    lidar_quit_now = quit_bool
    mutex.release()

def lidar_sense(do_plot=False, record_lidar=False):

    # Connect to Lidar unit
    lidar = Lidar(LIDAR_DEVICE)
    lidar.start_motor()
    print("Lidar Info: {}".format(lidar.get_info()))
    print("Lidar health: {}".format(lidar.get_health()))

    # Create an RMHC SLAM object with a laser model and optional robot model
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    # Initialize an empty trajectory
    trajectory = []

    # Initialize empty map
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

    # Create an iterator to collect scan data from the RPLidar
    iterator = lidar.iter_scans()

    # We will use these to store previous scan in case current scan is inadequate
    previous_distances = None
    previous_angles    = None

    # First scan is crap, so ignore it
    next(iterator)
    
    img = [[0 for x in range(MAP_SIZE_PIXELS)] for y in range(MAP_SIZE_PIXELS)]
    iter_no = 0
    
    if do_plot:
        plt.ion()
        plt.gray()
        plt.show()
        
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
        while get_lidar_quit() == False:

            # Extract (quality, angle, distance) triples from current scan
            items = [item for item in next(iterator)]

            # Extract distances and angles from triples
            distances = [item[2] for item in items]
            angles    = [item[1] for item in items]

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances
                previous_angles    = angles

            # If not adequate, use previous
            elif previous_distances is not None:
                slam.update(previous_distances, scan_angles_degrees=previous_angles)

            # Get current robot position
            x, y, theta = slam.getpos()
            print("\rX : {x} , Y : {y},theta : {theta}".format(x=x,y=y,theta=theta))
            print("\rDistances : {}".format(len(distances)))
            print("\rAngles : {}".format(len(angles)))

            # Get current map bytes as grayscale
            slam.getmap(mapbytes)
            #print("\r[MAP]{}".format(mapbytes))

            if do_plot or record_lidar:
                for row_num in range(0, MAP_SIZE_PIXELS):
                    start = row_num * MAP_SIZE_PIXELS
                    end = start + MAP_SIZE_PIXELS
                    img[row_num] = mapbytes[start:end]

            if do_plot:
                if iter_no % 100 == 0:
                    plt.imshow(img)
                    plt.draw()
                    plt.pause(1)
            elif record_lidar:
                if data_file is not None:
                    ts_cur_str = str(time.time())
                    #int.from_bytes(b, byteorder='big', signed=False)
                    data_file.write(ts_cur_str + " Ds : {}".format(distances))
                    data_file.write("\n")
                    data_file.write(ts_cur_str + " As : {}".format(angles))
                    data_file.write("\n")
                    data_file.write("\n")

    except:
        print("\rSomething went wrong with the Lidar, quitting...")

    finally:
        # Shut down the lidar connection
        lidar.stop_motor()
        lidar.stop()
        lidar.disconnect()
        
        if record_lidar:
            data_file.close()
