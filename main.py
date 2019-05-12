import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED
import sys
from select import select
#clean this soon
sys.path.append("/home/pi/.local/lib/python2.7/site-packages/")
import readchar


from config import motor_run_time,
                   motor_speed,
                   motor_speed_increment,
                   motor_turn_time,
                   turn_motor_speed,
                   timeout,
                   max_allowed_speed






try:
    import tty, termios

    prev_flags = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
except ImportError:
    prev_flags = None

try:
    motors.enable()
    while(True):
        rl, wl, xl = select([sys.stdin], [], [], timeout)
        if rl: # some input
            key = sys.stdin.read(1)
        else:
            if motor_speed > 0:
                motor_speed -= motor_speed_increment
            elif motor_speed < 0:
                motor_speed += motor_speed_increment
            motors.setSpeeds(motor_speed, motor_speed)
            time.sleep(motor_run_time)
            continue
        if(key=='w'):
            motors.setSpeeds(motor_speed, motor_speed)
            time.sleep(motor_run_time)
            if (motor_speed < max_allowed_speed):
                motor_speed += motor_speed_increment
        elif(key=='s'):
            if (motor_speed > -max_allowed_speed):
                motor_speed -= motor_speed_increment
            motors.setSpeeds(motor_speed, motor_speed)
            time.sleep(motor_run_time)
        elif(key=='d'):
            motors.setSpeeds(-turn_motor_speed,turn_motor_speed)
            time.sleep(motor_turn_time)
        elif(key=='a'):
            motors.setSpeeds(turn_motor_speed,-turn_motor_speed)
            time.sleep(motor_turn_time)
        elif(key=='q'):
            break
        if(key=='a' or key=='d'):
            print("\r{}".format(turn_motor_speed))
        else:
            print("\r{}".format(motor_speed))






finally:
  # Stop the motors, even if there is an exception
  # or the user presses Ctrl+C to kill the process.
    motors.setSpeeds(0, 0)
    motors.disable()
