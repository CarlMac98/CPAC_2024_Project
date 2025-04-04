import argparse
import sys
import time
import math
import numpy as np

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from utils import visualize

from pythonosc import udp_client
#from pythonosc import osc_server

import globalvars
import find_clusters as fc


def run(model: str, camera_id: int, width: int, height: int) -> None:
  """Continuously run inference on images acquired from the camera.

  Args:
    model: Name of the TFLite object detection model.
    camera_id: The camera id to be passed to OpenCV.
    width: The width of the frame captured from the camera.
    height: The height of the frame captured from the camera.
  """

  # Create the OSC client
  osc_address = "192.168.109.38"
  osc_port = 5008

  osc_client = udp_client.SimpleUDPClient(osc_address, osc_port)

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

  def visualize_callback(result: vision.ObjectDetectorResult,
                         output_image: mp.Image, timestamp_ms: int):
      result.timestamp_ms = timestamp_ms
      
      #Append only people detections to the list
      
      detection_result_list.append(result)
  

  # Initialize the object detection model
  model_path = 'efficientdet_lite2.tflite'
  base_options = python.BaseOptions(model_asset_path=model)
  options = vision.ObjectDetectorOptions(base_options=base_options,
                                         running_mode=vision.RunningMode.LIVE_STREAM,
                                         score_threshold=0.5,
                                         result_callback=visualize_callback)
  detector = vision.ObjectDetector.create_from_options(options)

  #center_x = 0
  #center_y = 0
  last_execution_time = 0
  timeout = 1.5

  is_cluster = False
  changed = False

  joint_center = [0,0]

  curr_n_people = 0

  # Continuously capture images from the camera and run inference
  while cap.isOpened():

    success, image = cap.read()
    
    if not success:
      #sys.exit(
      #    'ERROR: Unable to read from webcam. Please verify your webcam settings.'
      #)
      cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
      counter += 1
      #image = cv2.flip(image, 1)

      # Convert the image from BGR to RGB as required by the TFLite model.
      rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

      # Run object detection using the model.
      if counter % 10 == 0:
        detection_result_list.clear()
        detector.detect_async(mp_image, counter)

      current_time = time.time()
      
      if(current_time - last_execution_time >= timeout): 
        if detection_result_list :
          if len(detection_result_list[0].detections) >= 2: #and detection_result_list[0].categories:
            # print(detection_result_list[0].detections[0].class_id)
            if curr_n_people != len(detection_result_list[0].detections):
              curr_n_people = len(detection_result_list[0].detections)
              changed = not is_cluster
            
            #center_x, center_y = 
            is_cluster, joint_center = cluster_present(detection_result_list[0].detections)
            last_execution_time = current_time
            # print(is_cluster)          
            center_x = joint_center[0]/cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            center_y = joint_center[1]/cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            #print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

            
            print(center_x, center_y)
          else:
            curr_n_people = 0
            is_cluster = False
            #print(is_cluster)
            center_x = 0
            center_y = 0
        # else:
        #   curr_n_people = 0
        #   is_cluster = False
        #   #print(is_cluster)
        #   center_x = 0
        #   center_y = 0
     
      if is_cluster != changed:
        print(is_cluster)
        # Send a message
        osc_client.send_message("/cluster", is_cluster)
        if is_cluster:
          osc_client.send_message("/center", [center_x, center_y])
        changed = is_cluster

      current_frame = mp_image.numpy_view()
      current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)

      # Calculate the FPS
      if counter % fps_avg_frame_count == 0:
          end_time = time.time()
          fps = fps_avg_frame_count / (end_time - start_time)
          start_time = time.time()

      # Show the FPS
      fps_text = 'FPS = {:.1f}'.format(fps)
      text_location = (left_margin, row_size)
      cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                  font_size, text_color, font_thickness)
      
      

      if detection_result_list:
          #print(detection_result_list[0].detections[0].bounding_box)
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

def cluster_present(detections):
  l = len(detections)
  # print(l)
  # print(detections[0].bounding_box)
  center_x = np.zeros(l)
  center_y = np.zeros(l)

  # joint_center

  is_cluster = False

  for i in range(l):
    #print(i)
    center_x[i] = detections[i].bounding_box.origin_x + detections[i].bounding_box.width/2
    center_y[i] = detections[i].bounding_box.origin_y + detections[i].bounding_box.height/2
    #cv2.circle(frame, center=(int(center_x),int(center_y)), radius=3, color=(0, 0, 255), thickness=1)
    # print(str(center_x) + " - " + str(center_y))

  joint_center = [0,0]
  for i in range(l):
    for j in range(l):
      if(j > i):
          if math.dist((center_x[i], center_y[i]), (center_x[j], center_y[j])) <= (detections[i].bounding_box.width/2 + 
                                                                                        detections[j].bounding_box.width/2):
            is_cluster = True
            if joint_center[0] == 0 == joint_center[1]:
              joint_center = [((center_x[j] + center_x[i])/2) , ((center_y[j] + center_y[i])/2)]
            else:
              joint_center = [((center_x[j] + center_x[i])/2 + (joint_center[0]))/2 , ((center_y[j] + center_y[i])/2 + (joint_center[1])/2)]
            #print(joint_center)

              # else:
          #   #joint_center = [0,0]
          #   is_cluster = False
  if joint_center != [0,0]:
    is_cluster = True

      

  return is_cluster, joint_center
    
    


def main():
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
