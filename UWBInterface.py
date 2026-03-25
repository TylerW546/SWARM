import time
import os

class UWBMessage:
    regular_message_ID = 0
    range_id = 0
    
    def __init__(self, content, timestamp, id):
        self.content = content
        self.timestamp = timestamp
        self.message_id = id
        

class UWBInterface:
    def __init__(self, ser):
        self.ser = ser

        self.is_discovering = False
        self.finished_discovery = False
        self.is_leader = False
        self.messages = []
        
        self.uwb_messages_recieved = []


    def assign_id(self, id):
        self.ser.add_to_send_queue(f"*ASSIGN_ID~{id}~")

    def enter_discovery_mode(self):
        self.ser.add_to_send_queue("*DISCOVER~")
        self.is_discovering = True

    def enter_ranging_mode(self):
        uwb_message = UWBMessage(content=None, timestamp=time.time(), id=UWBMessage.range_id)
        self.ser.add_to_send_queue("*RANGE~")
        return uwb_message

    def send_uwb_message(self, message):
        uwb_message = UWBMessage(content=message, timestamp=time.time(), id=UWBMessage.regular_message_ID)
        self.ser.add_to_send_queue(f"*SEND:{uwb_message.message_id},{uwb_message.content}~")
        return uwb_message

    def enter_listen_mode(self):
        self.ser.add_to_send_queue("*LISTEN~")

    def check_ack_state(self, message):
        self.ser.add_to_send_queue(f"*ACK_QUERY:{message.message_id}~")

    def check_ranging_state(self, message):
        self.ser.add_to_send_queue(f"*RANGE_QUERY:{message.message_id}~")

    def reset(self):
        try:
            os.execv("/bin/bash", ["bash", "../start.sh", "no_new_screen"])
        except Exception as e:
            print(f"Failed to reset: {e}")

    def loop(self):
        for line in self.ser.lines_read:
            if line.startswith("*DISC_COMPLETE:"):
                self.is_discovering = False
                self.finished_discovery = True
                if line.startswith("*DISC_COMPLETE:LEADER"):
                    self.is_leader = True
                else:
                    self.is_leader = False
            elif line.startswith("*RESET~"):
                # Process reset message
                self.reset()
            elif line.startswith("*REC:"):
                # Process range response
                self.uwb_messages_recieved.append(line[5:-1])

            self.ser.lines_read.remove(line)
        self.ser.loop()
