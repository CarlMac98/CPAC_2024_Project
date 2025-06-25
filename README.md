# CPAC_2024_Project

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Dependencies](#dependencies)
7. [Troubleshooting](#troubleshooting)
8. [Examples / Demos](#examples--demos)
9. [Creators](#creators)

---

## Project Overview
This repository contains our final project for the Creative Programming and Computing (CPAC) course 2024/2025 at Politecnico di Milano (Music Engineering).
Our project explores the theme of loneliness in large cities by creating an interactive artistic installation. Using Python and TouchDesigner, we analyze webcam feeds to detect and cluster groups of people in real time. This visual data is then combined with generative music created in Pure Data, resulting in a dynamic and immersive audio-visual experience that reflects patterns of social interaction and isolation within urban environments.

## Features
- **Real-time Tracking**: Detects and clusters groups of people from a webcam feed using Python and TouchDesigner.
- **Generative Music**: Creates adaptive generative music in real time using Markov chains in Pure Data.
- **Chladni Pattern Particle Systems**: Background display with dynamic Chladni pattern-inspired particle systems.
- **Style Transfer & QR Code Output**: Applies artistic style transfer to a final gegnerated image of each performance and generates a unique QR code for participants to access or download their personalized result.
- **OSC communication**: all the programs comunicate to each other by using OSC messages.

## Installation
Before setting up or running the project, make sure you have the following tools installed:

### Python
- Use the provided `.yml` file to create a conda or virtual environment with all required Python dependencies.
### Processing
- Required for generating the Chladni pattern mask used by the particle system. [Download Processing](https://processing.org/download).
### Pure Data (Pd)
- Needed for the generative music component. [Download Pure Data](https://puredata.info/downloads/pure-data).
### TouchDesigner
Used for real-time video analysis, clustering, and overall installation management. [Download TouchDesigner](https://derivative.ca/download).

## Configuration

Before running the project, please complete the following setup steps:

### 1. Python Setup

- **Create `globalvars.py`:**  
  Inside the `Python` folder, create a file named `globalvars.py`.  
  Define a variable called `model_path` and set it to the filename of the tracking model you wish to use (models are provided in the same folder with `.tflite` extension).  
  ```python
  # Example globalvars.py
  model_path = "your_tracking_model.tflite"
  ```

- **Edit `imageUpload.py`:**  
  - Set the `IMAGE_PATH` variable to the path of the image you want to upload for the QR code.
  - Set the `QR_PATH` variable to the desired output destination (TouchDesigner will use this path).
  - Change the `API_KEY` variable to your [imgbb API key](https://api.imgbb.com/).
  ```python
  # Example section in imageUpload.py
  IMAGE_PATH = "path/to/your/image.jpg" # mind the file extension, it should be jpg
  QR_PATH = "path/to/output/qr_code.png"
  API_KEY = "YOUR_IMGBB_API_KEY"
  ```

### 2. TouchDesigner Setup

- **Chladni Pattern Path:**  
  In TouchDesigner, set the file path for the Chladni pattern image in the `moviefilein1` block. Choose an image from the `Chladni_patterns_image_generation` folder.

- **OSCIn Block Configuration:**  
  - Set the`QR_PATH` path to match what you used in `imageUpload.py`.
  - In the `update_clusters` function (inside the `oscIn` block), set the path to your Chladni pattern folder, leave the last part as `\chladni_{a}_{b}.png`.
  - In the `osc_receive` function, set the corresponding local folders as needed.

- **OSC Addresses and Ports:**  
  Configure the OSC (Open Sound Control) addresses and ports in both TouchDesigner, Pure Data, and `detector.py` to ensure correct communication between components.  
  Make sure these match in all relevant scripts and tools.

### 3. Pure Data (Pd) Setup

- **OSC Configuration:**  
  In Pure Data, set the appropriate OSC addresses and ports to match your configuration in TouchDesigner.

**Tip:**  
Double-check all paths and keys, and test communication between Python, TouchDesigner, and Pure Data before running a full performance!

Here’s a clear, step-by-step “Usage” section for your README, based on your instructions:

---

## Usage

1. **Chladni Patterns**  
   The Chladni patterns have already been generated, so you do not need to run the Processing code in the `Chladni_Patterns_image_generation` folder.

2. **Start Pure Data**  
   - Open the `polyModal.pd` file in Pure Data.
   - Activate the DSP (Digital Signal Processing).
   - Set your desired audio output devices.

3. **Start TouchDesigner**  
   - Open the `ParticleSystem.toe` file in TouchDesigner.
   - In the `videodevin1` block, select your webcam device.  
     **Important:** This webcam should be different from the one you use for tracking in Python.
   - Set the display to fullscreen from the `window1` block.

4. **Start the Python Tracker**  
   - Open the `detector.py` file inside the `Python` folder.
   - At the bottom of the file (where the arguments are parsed), select the default camera ID for the tracking webcam.
   - Ensure all configuration steps have been completed (see [Configuration](#configuration)).

5. **Run the System**  
   - Run the Python script (`detector.py`).  
   - After a few seconds, the system should start, sending information from Python to TouchDesigner.
   - You should see in TouchDesigner a real-time clustering effect and hear sounds when a group of at least two people is detected.
   - If no clusters are detected after one minute of the performance, a QR code will appear after a few seconds (internet connection required). The QR code will be displayed for 30 seconds, then the system will reset for the next performance.

## Project Structure
- Briefly explain the folder and file organization.
- Mention where to find code, assets, and configuration files.

Here’s a clear “Dependencies” section for your README, incorporating your notes and leaving a placeholder for the Pure Data dependencies:

---

## Dependencies

This project relies on several key libraries and external services:

- **TensorFlow (Style Transfer Module)**  
  Used for applying artistic style transfer to images.  
  [TensorFlow Hub Style Transfer](https://www.kaggle.com/models/google/arbitrary-image-stylization-v1/tensorFlow1/256/2)

- **MediaPipe (Tracking Algorithm)**  
  Google’s MediaPipe is used for real-time body and group tracking from the webcam feed.  
  [MediaPipe](https://mediapipe.dev/)

- **imgbb API**  
  Used for uploading the style-transferred image and retrieving a URL for QR code generation.  
  [imgbb API](https://api.imgbb.com/)

- **Pure Data (Pd) External Dependencies**  
  _[Add here the specific Pure Data externals or libraries you use, such as OSC libraries, audio effects, or any custom externals. Be specific about required versions or where to download them.]_

Here’s a “Troubleshooting” section you can add to your README, addressing this specific issue:

---

## Troubleshooting

### ValueError: Trying to load a model of incompatible/unknown type

If you encounter the following error when running `detector.py`:

```
ValueError: Trying to load a model of incompatible/unknown type. 'C:\Users\username\AppData\Local\Temp\tfhub_modules\f843094219bf78a99e8ea6c8d71f1bc74f07101a' contains neither 'saved_model.pb' nor 'saved_model.pbtxt'.
```

**Solution:**  
Delete the entire folder located at:
```
C:\Users\username\AppData\Local\Temp\tfhub_modules\
```
Then, re-run the Python code. This will force TensorFlow Hub to re-download the required model files.

## Examples / Demos

https://github.com/user-attachments/assets/9cf1c21d-d2c1-41af-be23-71018423c3e9

## Creators
- **Galadini Giuliano**: Pure data
- **Lenoci Alice**: Style Transfer
- **Macrì Carlo**: Tracking
- **Messina Francisco**: TouchDesigner
