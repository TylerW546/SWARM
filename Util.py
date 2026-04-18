import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

PIXEL_COUNT_THRESHOLD = 300
PIXEL_COUNT_UPPER_THRESHOLD = 3000

IMAGE_WIDTH = 640//2
IMAGE_HEIGHT = 480//2

VISUALIZE = False

MOTOR_SPEED = 60
TURN_SPEED = 40

# Wheel encoder to distance values
WHEEL_CIRC_METERS = 2 * 3.1415 * 0.035 # Circumference in meters
ENCODER_COUNT = 20 # Counts per rotation
COUNT_TO_METERS = WHEEL_CIRC_METERS / ENCODER_COUNT

# Right motor
IN1 = 17
IN2 = 27
ENA = 22 # PWM
ENCODER_R = 16

# Left motor
IN3 = 23
IN4 = 24
ENB = 25 # PWM
ENCODER_L = 19

# IR sensor
IR_PIN = 26

# Ultrasonic sensor
US_ECHO_PIN = 9
US_TRIGGER_PIN = 11
DISTANCE_THRESHOLD = 0.3

from enum import Enum 


class State(Enum):
    INIT_DEVICE_DISCOVERY = 1
    INIT_PARENTING = 2
    INIT_CHILD = 3
    WANDER = 4
    ACTIVE_SLEEP = 5

class MovementState(Enum):
    IDLE = 1
    HUB_SPOKE = 2
    BOUSTROPHEDON = 3
    FOLLOW_TARGET_COLOR = 4
    CELEBRATION = 5

class PID_State(Enum):
    IDLE = 1
    WAITING = 2
    STRAIGHT = 3
    TURNING_RIGHT = 4
    TURNING_LEFT = 5
    COAST = 6
    OVERRIDE = 7
    