from config import motor_run_time,\
                    motor_speed,\
                    motor_speed_increment,\
                    motor_turn_time,\
                    turn_motor_speed,\
                    timeout,\
                    max_allowed_speed,\
                    disable_motor_flag

movement_state = {
                motor_run_time=motor_run_time,
                motor_speed=motor_speed,
                motor_speed_increment=motor_speed_increment,
                motor_turn_time=motor_turn_time,
                turn_motor_speed=turn_motor_speed,
                timeout=timeout,
                max_allowed_speed=max_allowed_speed,
                disable_motor_flag=disable_motor_flag
}

import time
if not disable_motor_flag:
    from dual_g2_hpmd_rpi import motors, MAX_SPEED
import sys
from select import select
import tty, termios


try:


    prev_flags = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
except ImportError:
    prev_flags = None

try:
    if not disable_motor_flag:
        motors.enable()
    while(True):


        rl, wl, xl = select([sys.stdin], [], [], timeout)
        print("\r{}".format(rl))
        print("\r{}".format(wl))
        print("\r{}".format(xl))
        if rl: # some input
            key = sys.stdin.read(1)
        else:
            #auto brake
            if motor_speed > 0:
                motor_speed -= motor_speed_increment
            elif motor_speed < 0:
                motor_speed += motor_speed_increment
            if not disable_motor_flag:
                motors.setSpeeds(motor_speed, motor_speed)
            time.sleep(motor_run_time)
            continue

        if(key=='w'):
            if not disable_motor_flag:
                motors.setSpeeds(motor_speed, motor_speed)
            time.sleep(motor_run_time)
            if (motor_speed < max_allowed_speed):
                motor_speed += motor_speed_increment
        elif(key=='s'):
            if (motor_speed > -max_allowed_speed):
                motor_speed -= motor_speed_increment
            if not disable_motor_flag:
                motors.setSpeeds(motor_speed, motor_speed)
            time.sleep(motor_run_time)
        elif(key=='d'):
            if not disable_motor_flag:
                motors.setSpeeds(-turn_motor_speed,turn_motor_speed)
            time.sleep(motor_turn_time)
        elif(key=='a'):
            if not disable_motor_flag:
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
    print("Process Quit")
    if not disable_motor_flag:
        motors.setSpeeds(0, 0)
        motors.disable()
