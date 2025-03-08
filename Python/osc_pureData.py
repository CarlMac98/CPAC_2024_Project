from pythonosc import udp_client
import time
import random
import keyboard

# Configure the OSC client
osc_ip = "192.168.0.186"    # Replace with the target IP address if needed
osc_port = 7099             # Replace with the target port
client = udp_client.SimpleUDPClient(osc_ip, osc_port)
old_value = 0

def number_to_tuple(n):
    return tuple(0 if i < n else 1 for i in range(4))

def send_osc_trigger(n):
    global old_value

    random_tuple = number_to_tuple(n)
    if n < old_value:
        # if n is less than the old value, append a 1 in the last position
        random_tuple = random_tuple + (1,)
    else:
        # if n is greater than the old value, append a 0 in the last position
        random_tuple = random_tuple + (0,)
    old_value = n
    # Sends an OSC message with the address '/trigger' and a value of 1
    client.send_message("/trigger", random_tuple)
    print("OSC trigger sent: " + str(n))

if __name__ == "__main__":
    print("Press '0-4' to send OSC trigger. Press ESC to exit.")

    while True:
        if keyboard.is_pressed("0"):
            send_osc_trigger(0)
            while keyboard.is_pressed("0"):  # Avoid multiple triggers from a single press
                pass
        elif keyboard.is_pressed("1"):
            send_osc_trigger(1)
            while keyboard.is_pressed("1"):  # Avoid multiple triggers from a single press
                pass
        elif keyboard.is_pressed("2"):
            send_osc_trigger(2)
            while keyboard.is_pressed("2"):
                pass
        elif keyboard.is_pressed("3"):
            send_osc_trigger(3)
            while keyboard.is_pressed("3"):
                pass
        elif keyboard.is_pressed("4"):
            send_osc_trigger(4)
            while keyboard.is_pressed("4"):
                pass
        elif keyboard.is_pressed("esc"):
            print("Stopped sending OSC triggers.")
            break
