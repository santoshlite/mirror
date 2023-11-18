<script lang="ts">
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import * as MediaPipeVision from '@mediapipe/tasks-vision';
    let MediaPipeDrawing: MediaPipeVision.DrawingUtils;
    const runningMode = "VIDEO";
    let handLandmarker = undefined;
    // import and load hand landmarker model from google
    const createHandLandmarker = async () => {
      const vision = await MediaPipeVision.FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm"
      );
      handLandmarker = await MediaPipeVision.HandLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task`,
          delegate: "GPU"
        },
        runningMode: runningMode,
        numHands: 2
      });
    };
    createHandLandmarker();

    let handCanvasElement;
    let handCanvasContext: CanvasRenderingContext2D;
    let videoElement;
    let canvasElement;
    let timer = 5;
    let countdown;

    async function startGestureWebcam() {

      handCanvasElement.style.width = videoElement.videoWidth;;
      handCanvasElement.style.height = videoElement.videoHeight;
      handCanvasElement.width = videoElement.videoWidth;
      handCanvasElement.height = videoElement.videoHeight;
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
      const EPS = 0.01;
      const PERPEPS = 0.1;
      let moving: boolean = false;

      function dist(x1, y1, x2, y2) {
        return Math.sqrt((x1-x2)**2 + (y1-y2)**2);
      }
      function disp() {
        return dist(currentPos.x, currentPos.y, previousPos.x, previousPos.y);
      }
      async function frameLoop() {
        if (handLandmarker) {
          let startTimeMs = performance.now();
          if (lastVideoTime !== videoElement.currentTime) {
            lastVideoTime = videoElement.currentTime;
            results = handLandmarker.detectForVideo(videoElement, startTimeMs);
          }
          handCanvasContext.clearRect(0, 0, handCanvasElement.width, handCanvasElement.height);
          if (results.landmarks && results.landmarks.length > 0 && results.landmarks[0].length > 8) {
            // console.log(results.landmarks[0][8]);
            MediaPipeDrawing.drawLandmarks([results.landmarks[0][8]], {color: "FF0000", lineWidth: 2});
            currentPos = results.landmarks[0][8];
            if (previousPos !== undefined) {
              if (frameCounter == 10) {
                frameCounter = 0;
                if (disp() < EPS) {
                  if (moving) {
                    moving = false;
                    console.log("movement ended");
                    console.log("squared displacement", disp());
                  }
                }
                else {
                  console.log("movement started");
                  moving = true;
                }
              }
            }
            previousPos = currentPos;
            frameCounter++;
          }
        }
        window.requestAnimationFrame(frameLoop);
      }
      await frameLoop();
    }
    const poses = writable([]); 
  
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
  
    function startCountdown() {
      timer = 5;
      countdown = setInterval(() => {
        timer -= 1;
        if (timer <= 0) {
          clearInterval(countdown);
          takePicture();
        }
      }, 1000);
    }
  
    function takePicture() {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    canvasElement.getContext('2d').drawImage(videoElement, 0, 0);
    const imageDataURL = canvasElement.toDataURL('image/png');
    poses.update(currentImages => [...currentImages, imageDataURL]); 
  }

    onMount(() => {
      
      handCanvasContext = handCanvasElement.getContext('2d');
      // handCanvasContext = handCanvasElement.getContext('2d');
      MediaPipeDrawing = new MediaPipeVision.DrawingUtils(handCanvasContext);
      startWebcam();
      startCountdown();
    });
  </script>
  
  <style>
    .webcam-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 70px);
    width: 50%;
    position: absolute;
    left: 0;
    top: 70px; 
    overflow: hidden;
    }
  
    .webcam-video {
      height: 100%;
      width: 100%;
      transform: scaleX(-1);
      object-fit: cover;
    }

    
  
    .timer {
      position: absolute;
      font-size: 3rem;
      color: white;
      z-index: 10;
    }

    #handCanvas {
      position: absolute;
      z-index: 1;
      transform: rotateY(180deg);
    }

    .image-gallery {
    position: absolute;
    top: 70px; 
    right: 0;
    width: 50%; 
    height: calc(100vh - 70px);
    overflow-y: auto; 
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    box-sizing: border-box;
  }

  .captured-image {
    max-width: 100%;
    margin-bottom: 1rem; /* Space between images */
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Optional: adds some depth to images */
  }

  </style>
  
  <div class="webcam-container">
    <canvas id="handCanvas" bind:this={handCanvasElement}></canvas>

    {#if timer > 0}
      <div class="timer">{timer}</div>
    {/if}

    <video bind:this={videoElement} autoplay class="webcam-video"></video>
    <canvas bind:this={canvasElement} style="display: none;"></canvas>
  </div>
  
  <div class="image-gallery">
    {#each $poses as image (image)}
      <img src={image} class="captured-image" alt="Captured snapshot">
    {/each}
    <button on:click={startCountdown}>Take pic</button>
  </div>