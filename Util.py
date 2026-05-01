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

SEEN_FRAMES_THRESHOLD = 2

# seconds
FRAME_DURATION = 0.080

MOTOR_SPEED = 30
TURN_SPEED = 20

# Wheel encoder to distance values
WHEEL_CIRC_METERS = 2 * 3.1415 * 0.035 # Circumference in meters
ENCODER_COUNT = 20 # Counts per rotation
COUNT_TO_METERS = WHEEL_CIRC_METERS / ENCODER_COUNT

# Right motor
IN1 = 23
IN2 = 24
ENA = 25 # PWM 25
ENCODER_R = 16

# Left motor
IN3 = 17
IN4 = 27
ENB = 22 # PWM 22
ENCODER_L = 19

# IR sensor
IR_PIN = 26

# Ultrasonic sensor
US_ECHO_PIN = 9
US_TRIGGER_PIN = 26
DISTANCE_THRESHOLD = 0.3

CONVERGED_THRESHOLD = -0.1
CLOSENESS_THRESHOLD = 0.2

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
    CONVERGENCE = 6

class PID_State(Enum):
    IDLE = 1
    WAITING = 2
    STRAIGHT = 3
    TURNING_RIGHT = 4
    TURNING_LEFT = 5
    COAST = 6
    OVERRIDE = 7
    