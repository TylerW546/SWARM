def enter_ranging_mode(ser):
        ser.add_to_send_queue("*START~")

def send_uwb_message(ser, message):
    ser.add_to_send_queue(f"*SEND: {message}~")

def enter_listen_mode(ser):
    ser.add_to_send_queue("*LISTEN~")