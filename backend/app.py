import asyncio
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from bleak import BleakScanner, BleakClient

#Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

#Standardized Bluetooth MIDI identifiers from Apple's doc specs
MIDI_SERVICE_UUID = "03b80e5a-ede8-4b33-a751-6ce34ec4c700"
MIDI_CHARACTERISTIC_UUID = "7772e5db-3868-4112-a1a9-f2669d106bf3"

#Flask renders templates/index.html
@app.route("/")
def index():
    #Load the frontend page
    return render_template("index.html")

def midi_callback(_sender, data):
    """This function accepts two parameters passes automatically by bleak library
    - _sender: identifies which Bluetooth device sent the data. This is intentionally unused
    - data: A raw sequence of bytes containing the MIDI information from a piano"""
    if len(data)<5:
        return #Ignore if the data is too short

    #Standard MIDI message
    #data[0] and data[1] are usually header and timestamp data bytes
    status = data[2] & 0xF0 #Note on or Note off
    note = data[3] #Musical pitch
    velocity = data[4] #Control the signal

    #144 is note on and velocity > 0 is pressing
    if status == 144 and velocity > 0:
        #use socketio.emit() to send data to the frontend
        socketio.emit("piano_note", {"status": "on", "note": note, "velocity": velocity})
    #128 is note off or velocity = 0 is not pressing
    elif status == 128 or (status == 144 and velocity == 0):
        socketio.emit("piano_note", {"status": "off", "note": note})

async def scan_and_connect():
    """This function is for scanning and connecting to a physical portable piano continuously."""
    while True:
        print("Scanning for MIDI piano...Make sure your piano is on!")
        try:
            #Make the scanning time 3 seconds
            devices = await BleakScanner.discover(timeout=3.0)
            piano_device = None

            for device in devices:
                #Search for name keywords, match with the list
                if device.name and any(keyword in device.name.lower() for keyword in ["piano", "midi"]):
                    piano_device = device
                    break

                #If searching for name keywords fails: Search for Bluetooth UUID services
                if not piano_device:
                    for uuid_device in devices:
                        if (uuid_device.details and hasattr(uuid_device.details, "uuids") and MIDI_SERVICE_UUID in uuid_device.details.uuids):
                            piano_device = device
                            break

                if piano_device:
                    print(f"Connecting to {piano_device.name} ({piano_device.address})...")
                    #Connect the device and send data to define the status, note, and velocity
                    async with BleakClient(piano_device.address) as client:
                        print("Connected successfully!")
                        await client.start_notify(MIDI_CHARACTERISTIC_UUID, midi_callback)

                        while client.is_connected:
                            await asyncio.sleep(1)
                else:
                    print("No Bluetooth piano found. Retrying in 3 seconds...")
        #Handle exception and allow the user to retry connecting
        except Exception as e:
            print(f"Connection error: {e}. Retrying in 3 seconds...")

        await asyncio.sleep(3)

def run_ble_loop():
    """This function is a bridge between Flask server and the bleak Bluetooth library.
    bleak relies heavily on Python's asyncio framework, it needs an active loop to run its await commands."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scan_and_connect())

if __name__ == "__main__":
    #Run the BLE scanning in a background thread so flask/socketio can run on main thread
    ble_thread = threading.Thread(target = run_ble_loop, daemon = True) #daemon = True tells the thread to shut down automatically when the user close the web server application
    ble_thread.start()
    #sockettio.run() run the web server while blocking the main thread to listen to the piano notes without being interrupted
    socketio.run(app, debug = True, port = 5000)
    #Open the website by using the html file in template while running this code
