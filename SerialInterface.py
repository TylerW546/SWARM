import time
import serial

SERIAL_PORT = '/dev/ttyAMA0'
BAUDRATE = 115200

class SerialInterface:
    def __init__(self, serial_port=SERIAL_PORT, baudrate=BAUDRATE):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.ser = self.open_serial()


        self.lines_read = []
        self.to_send_queue = []

    def send_message(self, message):
        try:
            self.ser.write((message + '\n').encode())
            print(f"Sent: {message}")
            return True
        except OSError as e:
            print(f"Serial I/O error: {e}")
            try:
                self.ser.close()
            except:
                pass
            time.sleep(1)
            self.ser = self.open_serial()
            return False

    def open_serial(self):
        while True:
            try:
                self.ser = serial.Serial(
                    self.serial_port,
                    self.baudrate,
                    timeout=1,        # 1 second timeout
                    write_timeout=1
                )
                print(f"Serial port {self.serial_port} opened.")
                return self.ser
            except Exception as e:
                print(f"Failed to open serial port: {e}")
                time.sleep(2)

    def update(self):
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode(errors="ignore").strip()
                self.lines_read.append(line)
        except OSError as e:
            print(f"Serial I/O error: {e}")
            try:
                self.ser.close()
            except:
                pass
            time.sleep(1)
            self.ser = self.open_serial()

        for message in self.to_send_queue:
            if self.send_message(message):
                self.to_send_queue.remove(message)


    def add_to_send_queue(self, message):
        self.to_send_queue.append(message)