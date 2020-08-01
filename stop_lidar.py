from rplidar import RPLidar as Lidar
lidar = Lidar('/dev/ttyUSB0')
lidar.stop_motor()
