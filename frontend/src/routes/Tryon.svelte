<script lang="ts">
    import * as Vision from '@mediapipe/tasks-vision';
    let Drawing = undefined;
    const runningMode = "VIDEO";
    let handLandmarker = undefined;
    // import and load hand landmarker model from google
    const createHandLandmarker = async () => {
      const vision = await Vision.FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm"
      );
      handLandmarker = await Vision.HandLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task`,
          delegate: "GPU"
        },
        runningMode: runningMode,
        numHands: 2
      });
    };
    createHandLandmarker();

    let canvasElement;
    let videoElement;
    let canvasContext;

    async function startGestureWebcam() {
      canvasElement.style.width = videoElement.videoWidth;
      canvasElement.style.height = videoElement.videoHeight;
      canvasElement.width = videoElement.videoWidth;
      canvasElement.height = videoElement.videoHeight;

      let lastVideoTime = -1;
      let results = undefined;
      let startTime = Math.floor(performance.now());
      let previousPos = undefined;
      let currentPos = undefined;
      let swipeDistance = 0;
      let swipeDuration = 0;
      const MIN_SWIPE_DISTANCE = 0.15;
      const MAX_SWIPE_DURATION = 1.5;
      let frameCounter = 0;
      const EPS = 0.05;
      const PERPEPS = 0.1;
      let moving: boolean = false;

      // squared norm
      function dist(x1, y1, x2, y2) {
        return (x1-x2)**2 + (y1-y2)**2;
      }
      function disp() {
        return dist(currentPos.x, currentPos.y, previousPos.x, previousPos.y);
      }
      async function frameLoop() {
        console.log("LOOP");
        if (handLandmarker) {
          console.log("handlandmarker");
          let startTimeMs = performance.now();
          if (lastVideoTime !== videoElement.currentTime) {
            lastVideoTime = videoElement.currentTime;
            results = handLandmarker.detectForVideo(videoElement, startTimeMs);
          }
          canvasContext.clearRect(0, 0, canvasElement.width, canvasElement.height);
          if (results.landmarks && results.landmarks.length > 0 && results.landmarks[0].length > 8) {
            Drawing.drawLandmarks([results.landmarks[0][8]], {color: "FF0000", lineWidth: 2});
            currentPos = results.landmarks[0][8];
            if (previousPos !== undefined) {
              if (disp() < EPS) {
                if (moving) {
                  moving = false;
                  console.log("movement ended");
                  console.log("squared displacement", disp());
                }
              }
              else {
                console.log("movement started");
              }
            }
            else {
              previousPos = currentPos;
            }
          }
        }
        window.requestAnimationFrame(frameLoop);
      }
      await frameLoop();
    }

  
    function startWebcam() {
      if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            videoElement.srcObject = stream;
            videoElement.addEventListener("loadeddata", startGestureWebcam)
          })
          .catch(err => {
            console.error("Error accessing webcam:", err);
          });
      }
    }
  
    import { onMount } from 'svelte';
    onMount(() => {
      canvasContext = canvasElement.getContext('2d');
      Drawing = new Vision.DrawingUtils(canvasContext);
      startWebcam();
    });
  </script>

<style>

.webcam-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 50%;
  position: absolute;
  left: 0;
  top: 0;
}

.webcam-video {
  height: 100%;
  width: 100%;
  transform: scaleX(-1);
  object-fit: cover; 
}

  </style>
  
  <div class="webcam-container">
    <canvas bind:this={canvasElement}></canvas>
    <video bind:this={videoElement} autoplay class="webcam-video"></video>
  </div>
  