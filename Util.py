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
    
class PID_State(Enum):
    IDLE = 1
    WAITING = 2
    STRAIGHT = 3
    TURNING_RIGHT = 4