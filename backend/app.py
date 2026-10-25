import os
import threading
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import serial

#Initialize Flask and SocketIO
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "../template"))
socketio = SocketIO(app, async_mode="threading")

#Set the port environment to detect which one to connect
BLUETOOTH_PORT = os.environ.get("PIANO_PORT", "")
#This tuple's items are in order: 7 lower keys then 5 upper keys
KEY_NOTES = (60, 62, 64, 65, 67, 69, 71, 61, 63, 66, 68, 70)
current_bits = 0 #Keep track of the keys' states, it equals to 0 means it's not pressed
received_bits = None


def debug_snapshot():
    #This function is for reading the data and turn it into a formatted 12-charcter binary string of key states
    return {"bits": received_bits, "keys": f"{current_bits:012b}" if received_bits is not None else None}


def report_bluetooth(bits):
    #This function updates the bits
    global received_bits
    received_bits = bits
    socketio.emit("bluetooth_debug", debug_snapshot())


@socketio.on("connect")
def send_bluetooth_debug():
    #This function is to open a new tab whenevr the web sever is connected
    socketio.emit("bluetooth_debug", debug_snapshot(), to=request.sid)

#Load the prontend page
@app.route("/")
def index():
    return render_template("index.html")


def update_keys(bits):
    #We update the state of keys on piano by reading the bits
    global current_bits
    changed = current_bits ^ bits
    for bit, note in enumerate(KEY_NOTES):
        if changed & (1 << bit):
            pressed = bool(bits & (1 << bit))
            socketio.emit("piano_note", {
                "status": "on" if pressed else "off",
                "note": note, "velocity": 80 if pressed else 0,
            })
    current_bits = bits


def process_bits(line):
    #Cleans ther data by removing line converting 13 charcters ong into 12 bits
    data = line.rstrip(b"\r\n")
    if len(data) != 13 or any(value not in b"01" for value in data):
        return False
    update_keys(int(data, 2) & 0x0FFF)  #Only 12 keys; ignore unused input12.
    report_bluetooth(data.decode("ascii"))
    return True


def read_bluetooth():
    if not BLUETOOTH_PORT:
        print('Set $env:PIANO_PORT="COMx" to the Bluetooth port, then restart app.py.', flush=True)
        return
    while True:
        try:
            report_bluetooth(None)
            with serial.Serial(BLUETOOTH_PORT, baudrate=115200, timeout=0.1) as connection:
                print(f"Connected to ESP32_Inputs on {BLUETOOTH_PORT}", flush=True)
                pending = b""
                last_packet = time.monotonic()
                while True:
                    chunk = connection.readline(64)
                    pending += chunk
                    if chunk.endswith(b"\n"):
                        if process_bits(pending):
                            last_packet = time.monotonic()
                        pending = b""
                    elif len(pending) > 64:
                        pending = b"!"  #Ignore an oversized frame until its newline.
                    if time.monotonic() - last_packet > 1:
                        raise serial.SerialException("No valid key data for 1 second")
        except (serial.SerialException, OSError) as error:
            update_keys(0)  #Release keys if Bluetooth disconnects.
            report_bluetooth(None)
            print(f"Bluetooth: {error}. Retrying in 3 seconds...", flush=True)
            time.sleep(3)


if __name__ == "__main__":
    #Read Bluetooth in a background thread while the web server runs.
    bluetooth_thread = threading.Thread(target=read_bluetooth, daemon=True)
    bluetooth_thread.start()
    socketio.run(app, debug=True, use_reloader=False, port=5000)
    #Type http://localhost:5000 to access the website.
