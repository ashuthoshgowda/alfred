
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

if __name__ == '__main__':

    # Connect to Lidar unit
    lidar = Lidar(LIDAR_DEVICE)

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

    while True:

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
        print("X : {x} , Y : {y},theta : {theta}".format(x=x,y=y,theta=theta))
        print("Distances : {}".format(distances))
        print("Angles : {}".format(angles))

        # Get current map bytes as grayscale
        slam.getmap(mapbytes)

    # Shut down the lidar connection
    lidar.stop()
    lidar.disconnect()
