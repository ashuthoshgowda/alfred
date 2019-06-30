import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED

import sys
from select import select
from bot import Bot

from working_lidar_aman import lidar_sense, set_lidar_quit
from threading import Thread


stop_after_threshold = False
threshold = 10 #seconds
Alfred = Bot("Alfred")

try:
    import tty, termios

    prev_flags = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
except ImportError:
    prev_flags = None

try:

    lidar_thread = Thread(target=Alfred.lidar_sense(do_plot=False, record_lidar=True))
    lidar_thread.start()
    ts_start = time.time()
    motors.enable()
    while(True):
        key = Alfred.read_keyboard_input()

        if lidar_thread.isAlive() == False:
            raise ValueError("\rLidar thread quite unexpectedly, quitting...")
            key = 'q'

        if stop_after_threshold:
            if time.time() - ts_start >= 10:
                print("\rThreshold time {} seconds passed, quitting now".\
                    format(threshold))
                key = 'q'

        if(key=='b'):
            Alfred.auto_brake()
        if(key=='w'):
            Alfred.move_forward()
            alfred_stats(Alfred.motor_speed)
        elif(key=='s'):
            Alfred.move_back()
            alfred_stats(Alfred.motor_speed)
        elif(key=='d'):
            Alfred.turn_right()
            alfred_stats(Alfred.turn_motor_speed)
        elif(key=='a'):
            Alfred.turn_left()
            alfred_stats(Alfred.turn_motor_speed)
        elif(key=='q'):
            Alfred.set_lidar_quit(True)
            break







finally:
    # Stop the motors, even if there is an exception
    # or the user presses Ctrl+C to kill the process.
    Alfred.shut_motors()

    if prev_flags != None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, prev_flags)
    print("\r{} has shut it's motors".format(Alfred.name))

    lidar_thread.join()
