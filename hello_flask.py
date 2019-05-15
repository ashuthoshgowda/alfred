# Python Script To Control Garage Door

# Load libraries

from bottle import route, run, template
from config import motor_run_time,\
                    motor_speed,\
                    motor_speed_increment,\
                    motor_turn_time,\
                    turn_motor_speed,\
                    timeout,\
                    max_allowed_speed,\
                    disable_motor_flag
import time

if not disable_motor_flag:
    from dual_g2_hpmd_rpi import motors, MAX_SPEED
# Handle http requests to the root address
@route('/')
def index():
    return 'Go away.'

@route('/turn_left')
def turn_left():
    motors.enable()
    if not disable_motor_flag:
        motors.setSpeeds(turn_motor_speed,-turn_motor_speed)
    time.sleep(motor_turn_time*1000)
    motors.setSpeeds(0, 0)
    motors.disable()

@route('/turn_right')
def turn_right():
    motors.enable()
    if not disable_motor_flag:
        motors.setSpeeds(-turn_motor_speed,turn_motor_speed)
    time.sleep(motor_turn_time*1000)
    motors.setSpeeds(0, 0)
    motors.disable()

<<<<<<< HEAD
@route('/move',methods=['POST','GET'])
def move_forward():
    print("hit forward with : {}".format(request))
    if request.method == 'GET':
        print("It's a GET")
    elif request.method == 'POST':
        motors.enable()
        if not disable_motor_flag:
            motors.setSpeeds(-turn_motor_speed,turn_motor_speed)
        time.sleep(motor_turn_time*100)
        motors.setSpeeds(0, 0)
        motors.disable()
=======
@route('/move',methods=['POST'])
def move_forward(request):
    print(request)
    motors.enable()
    if not disable_motor_flag:
        motors.setSpeeds(-turn_motor_speed,turn_motor_speed)
    time.sleep(motor_turn_time*100)
    motors.setSpeeds(0, 0)
    motors.disable()
>>>>>>> 1f9dfc0b736d3d32b3d10c226cd17ce8a57cd38f


run(host='0.0.0.0', port=80)
