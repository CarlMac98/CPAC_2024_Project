from pythonosc import udp_client
import time
import random
import keyboard

# Configure the OSC client
osc_ip = "192.168.0.186"   # Replace with the target IP address if needed
osc_port = 7099        # Replace with the target port
client = udp_client.SimpleUDPClient(osc_ip, osc_port)

def number_to_tuple(n):
    return tuple(0 if i < n else 1 for i in range(4))

def send_osc_trigger():
    random_int = random.randint(0, 4)
    random_tuple = number_to_tuple(random_int)
    # Sends an OSC message with the address '/trigger' and a value of 1
    client.send_message("/trigger", random_tuple)
    print("OSC trigger sent: " + str(random_int))

if __name__ == "__main__":
    print("Press 'C' to send OSC trigger. Press ESC to exit.")

    while True:
        if keyboard.is_pressed("c"):
            send_osc_trigger()
            while keyboard.is_pressed("c"):  # Avoid multiple triggers from a single press
                pass
        elif keyboard.is_pressed("esc"):
            print("Stopped sending OSC triggers.")
            break
