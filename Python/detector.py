import argparse
import sys, os
import time
import math
import numpy as np
import json
import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from utils import visualize

from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

import threading
import globalvars
import find_clusters as fc
import imageUpload
import style_transfer_module as style

# Create the OSC client
osc_address = "127.0.0.1"
osc_port_touch = 5009
osc_port_touch_rec = 5010
osc_port_pure_data = 7099
osc_client_pure_data = udp_client.SimpleUDPClient(osc_address, osc_port_pure_data)
osc_client_touch = udp_client.SimpleUDPClient(osc_address, osc_port_touch)

# Event to signal stop of tracking
stop_event = threading.Event()

# Incoming OSC handler
def on_stop(unused_addr, *args):
    print("Received stop tracking command")
    stop_event.set()

# Function called when stop command is received
def handle_stop_action():
    # Your custom function logic here
    time.sleep(0.2)
    base_dir = os.getcwd()
    # Perform style transfer
    style_path = os.path.abspath(os.path.join(base_dir, "TouchDesigner", "bicicletta.JPG"))
    content_path = os.path.abspath(os.path.join(base_dir, "TouchDesigner", "Rush.jpg"))
    output_path = os.path.abspath(os.path.join(base_dir, "TouchDesigner", "stylized_image.jpg"))
    style.perform_style_transfer(content_path, style_path, output_path)
    time.sleep(0.2)
    imageUpload.upload_image_and_generate_qr()  # Call the image upload function
    time.sleep(0.2)
    # After done, send confirmation
    osc_client_touch.send_message("/imageSaved", 1)
    # Wait 30 seconds before resuming tracking
    time.sleep(15)
    osc_client_touch.send_message("/reset", 1)
    stop_event.clear()

# Set up OSC server in separate thread
def start_osc_server():
    disp = dispatcher.Dispatcher()
    disp.map("/stopTracking", on_stop)
    server = osc_server.ThreadingOSCUDPServer((osc_address, osc_port_touch_rec), disp)
    print(f"OSC server listening on {osc_address}:{osc_port_touch_rec}")
    server.serve_forever()

old_value = 0
end_total = False

def run(model: str, camera_id: int, width: int, height: int) -> None:
  """Continuously run inference on images acquired from the camera.

  Args:
    model: Name of the TFLite object detection model.
    camera_id: The camera id to be passed to OpenCV.
    width: The width of the frame captured from the camera.
    height: The height of the frame captured from the camera.
  """

  # Variables to calculate FPS
  counter, fps = 0, 0
  start_time = time.time()

  # Start capturing video input from the camera
  cap = cv2.VideoCapture(camera_id)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

  # Visualization parameters
  row_size = 20  # pixels
  left_margin = 24  # pixels
  text_color = (0, 0, 255)  # red
  font_size = 1
  font_thickness = 1
  fps_avg_frame_count = 10

  detection_result_list = []

  # Callback function of the tracking to visualize the results
  def visualize_callback(result: vision.ObjectDetectorResult,
                         output_image: mp.Image, timestamp_ms: int):
      result.timestamp_ms = timestamp_ms
      detection_result_list.append(result)
  

  # Initialize the object detection model
  model_path = 'efficientdet_lite2.tflite'
  base_options = python.BaseOptions(model_asset_path=model)
  options = vision.ObjectDetectorOptions(base_options=base_options,
                                         running_mode=vision.RunningMode.LIVE_STREAM,
                                         score_threshold=0.3,
                                         category_allowlist=['person'], # Only detect persons
                                         result_callback=visualize_callback)
  detector = vision.ObjectDetector.create_from_options(options)
  

  #center_x = 0
  #center_y = 0
  last_execution_time = 0
  timeout = 0.2

  is_cluster = False
  changed = False

  radius = 350
  
  # Initialize the cluster tracker
  # The radius is the distance in pixels to consider two people as part of the same cluster
  tracker = fc.ClusterTracker(radius=radius, width=width)

  # Continuously capture images from the camera and run inference
  while cap.isOpened():
    # Check if the stop event is set
    if stop_event.is_set():
      handle_stop_action()

    success, image = cap.read()
    
    if not success:
      #sys.exit(
      #    'ERROR: Unable to read from webcam. Please verify your webcam settings.'
      #)
      cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
      counter += 1
      image = cv2.flip(image, 1)

      # Convert the image from BGR to RGB as required by the TFLite model.
      rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

      # Run object detection using the model.
      if counter % 17 == 0:
         detection_result_list.clear()
      if counter % 5 == 0:
        
        # test_time = time.time()
        detector.detect_async(mp_image, counter)
        # print(f"Detection time: {time.time() - test_time:.4f} seconds")

        # We don't track at every frame, but only every 0.2 seconds
        # This is to avoid too many detections and clusters
        current_time = time.time()

        # if(current_time - last_execution_time >= timeout): 
        # If there are detections, track them
        if detection_result_list :
          # print("Hello, I have detections")
          if len(detection_result_list[-1].detections) >= 1: #and detection_result_list[0].categories:
            is_cluster, cluster_centers, tracker = track_people(tracker, detection_result_list[-1].detections, width)
            last_execution_time = time.time()
          else:
            # If there are no detections, send empty clusters
            is_cluster, cluster_centers, tracker = track_people(tracker, [], width)

        if is_cluster != changed:
          #print(is_cluster)
          # Send a message to the OSC server to indicate if there are clusters or not
          osc_client_touch.send_message("/activate", is_cluster)
          changed = is_cluster

        if is_cluster:
          #print(cluster_centers)
          osc_client_touch.send_message("/clusters", json.dumps(cluster_centers))
          send_osc_trigger(len(cluster_centers))
        else:
          osc_client_touch.send_message("/clusters", json.dumps({}))
          send_osc_trigger(0)

        # print("time passed: ", time.time() - current_time)

      current_frame = mp_image.numpy_view()
      current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)

      # Calculate the FPS
      # if counter % fps_avg_frame_count == 0:
      #     end_time = time.time()
      #     fps = fps_avg_frame_count / (end_time - start_time)
      #     start_time = time.time()

      # Show the FPS
      # fps_text = 'FPS = {:.1f}'.format(fps)
      # text_location = (left_margin, row_size)
      # cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
      #             font_size, text_color, font_thickness)

      if detection_result_list:
          vis_image = visualize(current_frame, detection_result_list[0])
          #cv2.circle(vis_image, center=(int(center_x),int(center_y)), radius=3, color=(0, 0, 255), thickness=1)
          cv2.imshow('object_detector', vis_image)
          
          #detection_result_list.clear()
      else:
          cv2.imshow('object_detector', current_frame)
      
      # Stop the program if the ESC key is pressed.
      if cv2.waitKey(1) == 27:
        break

  detector.close()
  cap.release()
  cv2.destroyAllWindows()

sensitivity = 1

def track_people(tracker, detections, k):
  l = len(detections)
  center_x = np.zeros(l)
  center_y = np.zeros(l)
  #center_z = np.zeros(l)
  points = []
  diagonals = []
  is_cluster = False

  #calculate the center of each person 
  for i in range(l):
    #print(i)
    center_x[i] = detections[i].bounding_box.origin_x + detections[i].bounding_box.width/2
    center_y[i] = detections[i].bounding_box.origin_y + (4*detections[i].bounding_box.height/5)
    #center_z[i] = (k - detections[i].bounding_box.width)

    #points.append((center_x[i], center_y[i], center_z[i]))
    points.append((center_x[i], center_y[i]))
    diagonals.append((detections[i].bounding_box.width**2 + detections[i].bounding_box.height**2)**0.5)
    
  tracker.update(points, diagonals)
  tracker.decrease_life()
  clusters = tracker.get_cluster_centers_dict()

  is_cluster = len(clusters) > 0    
  return is_cluster, clusters, tracker

def number_to_tuple(n):
    return tuple(0 if i < n else 1 for i in range(4))

def send_osc_trigger(n):
    global old_value

    random_tuple = number_to_tuple(n)
    if n != old_value:
      if n < old_value:
          # if n is less than the old value, append a 1 in the last position
          random_tuple = random_tuple + (1,)
      else:
          # if n is greater than the old value, append a 0 in the last position
          random_tuple = random_tuple + (0,)
      old_value = n
      # Sends an OSC message with the address '/trigger' and a value of 1
      osc_client_pure_data.send_message("/trigger", random_tuple)
      print("OSC trigger sent: " + str(n))
    
def main():
  # Start OSC server thread for recieving stop message from touchdesigner
  server_thread = threading.Thread(target=start_osc_server, daemon=True)
  server_thread.start()

  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model',
      help='Path of the object detection model.',
      required=False,
      default=globalvars.model_path)
  parser.add_argument(
      '--cameraId', help='Id of camera.', required=False, type=int, default=0)
  parser.add_argument(
      '--frameWidth',
      help='Width of frame to capture from camera.',
      required=False,
      type=int,
      default=1280)
  parser.add_argument(
      '--frameHeight',
      help='Height of frame to capture from camera.',
      required=False,
      type=int,
      default=720)
  args = parser.parse_args()
  
  run(args.model, int(args.cameraId), args.frameWidth, args.frameHeight)


if __name__ == '__main__':
  main()
