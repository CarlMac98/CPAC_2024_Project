import argparse
import sys
import time

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from utils import visualize

import globalvars


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
  start_time_2 = time.time()
  

  # Start capturing video input from the camera
  cap = cv2.VideoCapture("Video/Video in tre.mp4")
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

  # Visualization parameters
  row_size = 20  # pixels
  left_margin = 24  # pixels
  text_color = (0, 0, 255)  # red
  font_size = 1
  font_thickness = 1
  fps_avg_frame_count = 30
  frame_time = 1 / 33
  detection_result = None
  # Initialize the object detection model
  #model_path = 'efficientdet_lite2.tflite'
  base_options = python.BaseOptions(model_asset_path=model)
  options = vision.ObjectDetectorOptions(base_options=base_options,
                                         running_mode=vision.RunningMode.VIDEO,
                                         score_threshold=0.5,
                                        )
  detector = vision.ObjectDetector.create_from_options(options)


  # Continuously capture images from the camera and run inference
  while cap.isOpened():
    start_time = time.time()

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
        detection_result = detector.detect_for_video(mp_image, counter)
      current_frame = mp_image.numpy_view()
      current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)

      # Calculate the FPS
      if counter % fps_avg_frame_count == 0:
          end_time = time.time()
          fps = fps_avg_frame_count / (end_time - start_time_2)
          start_time_2 = time.time()

      # Show the FPS
      fps_text = 'FPS = {:.1f}'.format(fps)
      text_location = (left_margin, row_size)
      cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                  font_size, text_color, font_thickness)

      if detection_result:
          print(detection_result)
          vis_image = visualize(current_frame, detection_result)
          cv2.imshow('object_detector', vis_image)
      else:
          cv2.imshow('object_detector', current_frame)

      # Stop the program if the ESC key is pressed.
      if cv2.waitKey(1) == 27:
        break
      # Enforce frame rate
      elapsed_time = time.time() - start_time
      time_to_wait = max(0, frame_time - elapsed_time)
      time.sleep(time_to_wait)

  detector.close()
  cap.release()
  cv2.destroyAllWindows()


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
