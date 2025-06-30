# RUSH: Rediscover Unity, Sharing Humanity

RUSH: Rediscover Unity, Sharing Humanity is a public, interactive art installation that transforms groups of passersby into living canvases, triggering generative visuals and music, to foster spontaneous connections and bridge social divides. By simply gathering in front of the screen, participants co-create a shared artistic experience that turns everyday encounters into moments of collective unity.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology](#technology)
3. [Features](#features)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Dependencies](#dependencies)
8. [Troubleshooting](#troubleshooting)
9. [Examples / Demos](#examples--demos)
10. [Challenges](#challenges)
11. [Accomplishments](#accomplishments)
12. [Lessons learned](#lessons-learned)
13. [Creators](#creators)

---

## Project Overview
This repository contains our final project for the Creative Programming and Computing (CPAC) course 2024/2025 at Politecnico di Milano (Music Engineering), which we decided to call it "RUSH: Rediscover Unity, Sharing Humanity", an immersive public-art installation designed to dissolve urban isolation and celebrate collective creativity. By harnessing real-time video capture, generative music, and dynamic visuals, the project transforms everyday cityscapes into living stages where strangers become collaborators.

### **Core Message**
At its heart, RUSH champions the idea that art is a universal language capable of bridging social divides. In a world marked by growing economic inequality and fragmented communities, the installation invites participants to rediscover empathy and shared purpose simply by coming together.

### **Artistic Medium and Format**

* **Installation Type:** A large-scale outdoor or gallery-mounted screen paired with a camera sensor.
* **Technology Stack:** Live video streaming, computer-vision algorithms to detect group formations, generative-audio software, and real-time graphics rendering.
* **Aesthetic:** Minimalist interface that lets the visuals and soundscape shine—ethereal generative patterns and harmonious melodies that respond to human presence.

### **User Experience Journey**

1. **Discovery:** People notice a screen with a webcam feed pointing at them in a public plaza or exhibition space.
2. **Activation:** When two or more individuals stand together before the camera’s field of view, the system recognizes them as a “group”.
3. **Co‑creation:**

   * **Visuals:** A resonant particle system ripples around the groups.
   * **Sound:** A generative musical score evolves in complexity and tonality based on group size.
4. **Reflection:** Participants witness how their simple act of gathering instantly transforms the environment into a shared artwork—prompting conversations, eye contact, and a sense of unity.
5. **Continuity:** Each interaction generates a unique audiovisual moment, ensuring no two experiences are alike and encouraging repeat visits.

By blending cutting-edge technology with participatory art, RUSH turns transient encounters into meaningful human connections, reminding city dwellers that unity and shared creativity are always within reach.

## Technology
- **Python**: mediapipe, dbscan
- **TouchDesigner**: particle systems, image accumulation
- **Processing**: Chladni pattern generation
- **Pure Data**: music generation with Markov-Chain

## Features
- **Real-time Tracking**: Detects and clusters groups of people from a webcam feed using Python and TouchDesigner.
- **Generative Music**: Creates adaptive generative music in real time using Markov chains in Pure Data.
- **Chladni Pattern Particle Systems**: Background display with dynamic Chladni pattern-inspired particle systems.
- **Style Transfer & QR Code Output**: Applies artistic style transfer to a final generated image of each performance and generates a unique QR code for participants to access or download their personalized result.
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

### 3. OSC Addresses and Ports:
- Configure the OSC (Open Sound Control) addresses and ports in both TouchDesigner, Pure Data, and `detector.py` to ensure correct communication between components. Make sure these match in all relevant scripts and tools.

**Tip:**  
Double-check all paths and keys, and test communication between Python, TouchDesigner, and Pure Data before running a full performance!

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
  Cyclone library, used for MAX/MSP objects inside Pd.
  [cyclone library](https://github.com/porres/pd-cyclone)


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

https://github.com/user-attachments/assets/ebf040da-ada0-4da3-ade9-e09af333d0b3

## Challenges

* Accurately gauging depth to distinguish whether people were standing close or further back proved tricky, so we ultimately relied on 2D clustering of silhouettes.
* Finding the right balance between responsiveness and system load meant throttling the tracking rate to prevent overload without sacrificing interactivity.

## Accomplishments

* Developed an image‑accumulation feature that layers snapshots over time into a single “temporal image,” then renders it as a dynamic QR‑code particle system for participants to take home.
* Built the entire audiovisual pipeline using Python, TouchDesigner, and Pure Data, with OSC communication stitching these tools together in real time to synchronize visuals and sound across installations.

## Lessons Learned

* Even simple interaction concepts can spark rich, spontaneous performances and genuine human connection in public spaces.
* Integrating diverse software tools through OSC proved immensely rewarding—and underscored how inter‑program communication can unlock capabilities far beyond any single application.


## Creators
- **Galadini Giuliano**: Programmed the generative music pipeline using Pure data, by appying Markov-Chains. Also helped with the implementation of the feedback effect in TouchDesigner
- **Lenoci Alice**: Programmed and included the style transfer pipeline for the final image of the performance
- **Macrì Carlo**: Programmed the tracking algorithm in Python
- **Messina Francisco**: Programmed the TouchDesigner implementation, also helped partially in the tracking algorithm
