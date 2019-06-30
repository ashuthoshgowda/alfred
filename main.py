import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED

import sys, traceback
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

    lidar_thread = Thread(target=Alfred.lidar_sense, args=[False, True])
    lidar_thread.start()
    ts_start = time.time()
    motors.enable()
    while(True):
        key = Alfred.read_keyboard_input()

        if lidar_thread.isAlive() == False:
            raise ValueError("\rLidar thread quit unexpectedly, quitting...")
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
            Alfred.alfred_stats(alfred_speed=Alfred.motor_speed)
        elif(key=='s'):
            Alfred.move_back()
            Alfred.alfred_stats(alfred_speed=Alfred.motor_speed)
        elif(key=='d'):
            Alfred.turn_right()
            Alfred.alfred_stats(alfred_speed=Alfred.turn_motor_speed)
        elif(key=='a'):
            Alfred.turn_left()
            Alfred.alfred_stats(alfred_speed=Alfred.turn_motor_speed)
        elif(key=='q'):
            Alfred.set_lidar_quit(True)
            break

except Exception as e:
    exc_type, ex, tb = sys.exc_info()
    imported_tb_info = traceback.extract_tb(tb)[-1]
    line_number = imported_tb_info[1]
    print_format = '{}: Exception in line: {}, message: {}'
    print(print_format.format(exc_type.__name__, line_number, ex))
    print("\rSomething went wrong with the Lidar, quitting...")

finally:
    # Stop the motors, even if there is an exception
    # or the user presses Ctrl+C to kill the process.
    Alfred.shut_motors()

    if prev_flags != None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, prev_flags)
    print("\r{} has shut it's motors".format(Alfred.name))

    lidar_thread.join()
