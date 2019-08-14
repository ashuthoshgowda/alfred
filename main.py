import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED

import sys, traceback
from select import select
from bot import Bot

from working_lidar_aman import lidar_sense, set_lidar_quit

stop_after_threshold = False
threshold = 10 #seconds
Alfred = Bot("Alfred")

try:
    import tty, termios

    prev_flags = termios.tcgetattr(sys.stdin.fileno())
    tty.setcbreak(sys.stdin.fileno())
except ImportError:
    prev_flags = None

try:
    Alfred.lidar_sense()
    ts_start = time.time()
    motors.enable()
    while(True):

        key = Alfred.read_keyboard_input()
        print(key)
        if Alfred.lidar_sense_running() == False:
            raise ValueError("Lidar sense thread quit unexpectedly, quitting...")
            key = 'q'

        if stop_after_threshold:
            if time.time() - ts_start >= 10:
                print("Threshold time {} seconds passed, quitting now".\
                    format(threshold))
                key = 'q'

        if(key=='b'):
            Alfred.auto_brake()
        elif(key=='w'):
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
        elif(key=='r'):
            Alfred.lidar_sense_reset()
        elif(key=='f'):
            Alfred.fast_mode()
        elif(key=='e'):
            Alfred.easy_mode()
        elif(key=='q'):
            Alfred.set_lidar_quit(True)
            break



except Exception as e:
    exc_type, ex, tb = sys.exc_info()
    imported_tb_info = traceback.extract_tb(tb)[-1]
    line_number = imported_tb_info[1]
    print_format = '{}: Exception in line: {}, message: {}'
    print(print_format.format(exc_type.__name__, line_number, ex))
    print("Something went wrong with the Lidar, quitting...")

finally:
    # Stop the motors, even if there is an exception
    # or the user presses Ctrl+C to kill the process.
    Alfred.shut_motors()

    if prev_flags != None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, prev_flags)
    print("{} has shut it's motors".format(Alfred.name))
