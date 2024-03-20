import pyb
led = pyb.LED(3)
usb = pyb.USB_VCP()
import sensor
import time
clock = time.clock()
import image
import network
import socket

SSID = "BL_phone"  # Network SSID
KEY = "***"  # Network key
HOST = "172.20.10.4"  # Use first available interface
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

# Create a UDP server socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))  # Bind the socket to a specific address

# Send to this client
client_address = ('172.20.10.2', 8000)

# Init sensor
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.RGB565)

def start_streaming(server,client_address):
    while True:
            clock.tick()  # Track elapsed milliseconds between snapshots().
            frame = sensor.snapshot()
            data = frame.compressed(quality=35).bytearray()
           
            # Split the data into chunks
            chunk_size = 250  # Maximum UDP packet size
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i+chunk_size]
                server.sendto(chunk, client_address)
            #print("frame sent", len(data))
            server.sendto(b'END', client_address)  # send an empty chunk to signal the end of the frame
            print(clock.fps())


while True:
    try:
        start_streaming(server,client_address)
    except OSError as e:
        print("socket error: ", e)
        # sys.print_exception(e)

