import pyb # Import module for board related functions
import sensor # Import the module for sensor related functions
import image # Import module containing machine vision algorithms
import time # Import module for tracking elapsed time
import network
import socket

SSID = "BL_phone"  # Network SSID
KEY = "bl123167"  # Network key
HOST = "172.20.10.4" 
PORT = 8000  # Arbitrary non-privileged port

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('172.20.10.4', '255.255.255.240', '172.20.10.1', '172.20.10.1'))
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

# We should have a valid IP now via DHCP
print("WiFi Connected ", wlan.ifconfig())

sensor.reset() # Resets the sensor
sensor.set_pixformat(sensor.GRAYSCALE) # Sets the sensor to grayscale
sensor.set_framesize(sensor.QVGA) # Sets the resolution to 320x240 px
sensor.skip_frames(time = 2000) # Skip some frames to let the image stabilize

# Create server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

# Bind and listen
s.bind(('0.0.0.0', PORT))  # Binds to all interfaces
s.listen()

# Set server socket to blocking
#s.setblocking(True)

# Init NICLA sensor
#sensor.reset()
#sensor.set_framesize(sensor.QVGA)
#sensor.set_pixformat(sensor.RGB565)

def start_streaming(s):
    print("Waiting for connections..")
    client, addr = s.accept()
    # set client socket timeout to 5s
    #client.settimeout(5.0)
    print("Connected to " + addr[0] + ":" + str(addr[1]))

    # Read request from client
    data = client.recv(1024)
    # Should parse client request here

    # Send multipart header
    client.sendall(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )

    # FPS clock
    clock = time.clock()

    # Start streaming images
    # NOTE: Disable IDE preview to increase streaming FPS.
    while True:
        clock.tick()  # Track elapsed milliseconds between snapshots().
        frame = sensor.snapshot()
        cframe = frame.compressed(quality=35)
        header = (
            "\r\n--openmv\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
        )
        client.sendall(header)
        client.sendall(cframe)
        print(clock.fps())


while True:
    try:
        start_streaming(s)
    except OSError as e:
        print("socket error: ", e)
        # sys.print_exception(e)
