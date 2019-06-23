import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED
import sys
from select import select
from bot import Bot
motor_run_time = 0.01
motor_speed = 60
motor_speed_increment = 60
motor_turn_time = 0.01
turn_motor_speed = 200
timeout = 0.1
max_allowed_speed = 400

Alfred = Bot("Alfred")

try:
    import tty, termios

    prev_flags = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
except ImportError:
    prev_flags = None

try:
    motors.enable()
    while(True):
        key = Alfred.read_keyboard_input()

        if(key=='w'):
            Alfred.move_forward()
        elif(key=='s'):
            Alfred.move_back()
        elif(key=='d'):
            Alfred.turn_right()
        elif(key=='a'):
            Alfred.turn_left()
        elif(key=='q'):
            break
        if(key=='a' or key=='d'):
            print("\r{}".format(Alfred.turn_motor_speed))
        else:
            print("\r{}".format(Alfred.motor_speed))






finally:
  # Stop the motors, even if there is an exception
  # or the user presses Ctrl+C to kill the process.
    Alfred.shut_motors()

    if prev_flags != None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, prev_flags)
    print("\r{} has shut it's motors".format(Alfred.name))
