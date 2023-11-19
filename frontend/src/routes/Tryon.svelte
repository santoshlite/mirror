<script lang="ts">
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { navigate } from 'svelte-routing';
    import logo from '/src/assets/logo.png'; 
    import { clothes } from '../store.js'; 

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
        numHands: 1
      });
    };
    createHandLandmarker();

    // import and load gesture recognizer model from google
    let gestureRecognizer = undefined;
    const createGestureRecognizer = async() => {
      const vision = await MediaPipeVision.FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
      );
      gestureRecognizer = await MediaPipeVision.GestureRecognizer.createFromOptions(vision, {
        baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task",
        delegate: "GPU"
        },
        runningMode: runningMode
      });
    };
    createGestureRecognizer();

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
      let handLandmarkerResults = undefined;
      let gestureRecognizerResults = undefined;
      let startTime = Math.floor(performance.now());
      let previousPos = undefined;
      let currentPos = undefined;
      let startPos = undefined;
      let motionStartTime = undefined;
      let motionEndTime = undefined;
      let stillFrameCounter = 0;
      const STILL_FRAME_THRESHOLD = 10;
      const EPS = 0.05;
      const MIN_SWIPE_VELOCITY = 0.3;
      const MIN_UP_SWIPE_VELOCITY = 0.1;
      const MIN_SWIPE_BUFFER_TIME = 1;
      const DEFAULT_LAST_SWIPE_TIME = -(MIN_SWIPE_BUFFER_TIME + 100);
      let lastSwipeTime = DEFAULT_LAST_SWIPE_TIME;
      let moving: boolean = false;

      // "min"/"max" is rough terminology
      let slopeBounds = {
        "vertical": {
          "min": 2,
          "max": -2
        },
        "horizontal": {
          "min": -1,
          "max": 1
        }
      };
      
      // idea: check right/left/up/down based on slope
      // and check avg velocity to register as swipe or not


      function dist(x1, y1, x2, y2) {
        return Math.sqrt((x1-x2)**2 + (y1-y2)**2);
      }
      function dista(a,b) {
        return dist(a.x, a.y, b.x, b.y);
      }
      function now() {
        return Math.floor(performance.now()) / 1000;
      }
      function isVertical(slope) {
        return (slopeBounds.vertical.min <= slope || slopeBounds.vertical.max >= slope);
      }
      function isHorizontal(slope) {
        return (slopeBounds.vertical.min <= slope && slopeBounds.vertical.max >= slope);
      }
      async function frameLoop() {
        if (handLandmarker && gestureRecognizer) {
          let startTimeMs = performance.now();
          if (lastVideoTime !== videoElement.currentTime) {
            lastVideoTime = videoElement.currentTime;
            handLandmarkerResults = handLandmarker.detectForVideo(videoElement, startTimeMs);
          }
          handCanvasContext.clearRect(0, 0, handCanvasElement.width, handCanvasElement.height);
          if (handLandmarkerResults.landmarks && handLandmarkerResults.landmarks.length > 0 && handLandmarkerResults.landmarks[0].length > 8) {
            // console.log(results.landmarks[0][8]);
            console.log("pointing up");
            MediaPipeDrawing.drawLandmarks([handLandmarkerResults.landmarks[0][8]], {color: "FF0000", lineWidth: 2});
            currentPos = handLandmarkerResults.landmarks[0][8];
            if (previousPos !== undefined) {
              if (dista(currentPos, previousPos) < EPS) {
                stillFrameCounter++;
                if (moving && stillFrameCounter == STILL_FRAME_THRESHOLD) {
                  motionEndTime = now();
                  moving = false;
                  console.log("movement ended");
                  console.log("displacement", dista(currentPos, startPos));
                  stillFrameCounter = 0;
                  
                  let slope = (currentPos.y - startPos.y)/(currentPos.x - startPos.x);
                  let avgVelocity = (dista(currentPos, startPos)/(motionEndTime - motionStartTime));
                  if (avgVelocity >= MIN_UP_SWIPE_VELOCITY && isVertical(slope) && currentPos.y < previousPos.y) {
                    lastSwipeTime = motionEndTime;
                    console.log("up swipe");
                  }
                  else if (avgVelocity >= MIN_SWIPE_VELOCITY) {
                    console.log("fast enough to be a swipe");
                    console.log("slope", slope);
                    if (isVertical(slope)) {
                      lastSwipeTime = motionEndTime;
                      console.log("vertical swipe");
                    }
                    else if (isHorizontal(slope)) {
                      lastSwipeTime = motionEndTime;
                      console.log("horizontal swipe");
                      swipe()
                    }
                  }
                }
              }
              else {
                if (!moving && (now() - lastSwipeTime >= MIN_SWIPE_BUFFER_TIME)) {
                  lastSwipeTime = DEFAULT_LAST_SWIPE_TIME;
                  motionStartTime = now();
                  startPos = currentPos;
                  console.log("movement started");
                  moving = true;
                  stillFrameCounter = 0;
                }
                else if (now() - lastSwipeTime < MIN_SWIPE_BUFFER_TIME) {
                  console.log("TOO FAST!");
                }
              }
            }
            previousPos = currentPos;
          }
          else {
            previousPos = undefined;
          }
        }
        window.requestAnimationFrame(frameLoop);
      }
      await frameLoop();
    }

    const poses = writable([]); 
    const currentIndex = writable(0);
  
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
  

    function swipe() {
    currentIndex.update(n => {
      return $clothes.length === n + 1 ? 0 : n + 1;
    });
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
      MediaPipeDrawing = new MediaPipeVision.DrawingUtils(handCanvasContext);
      startWebcam();
      startCountdown();
      if ($clothes.length === 0) {
        navigate('/');
      }
    });

  </script>
  


<div class="top-bar">
  <div class="spacer"></div> 
  <a href="/" class="logo-container">
      <img src={logo} alt="Mirror Logo" class="logo"/>
  </a>
  <div class="spacer"></div> 
  <div class="icon-container">
    <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" class="text-xl" height="1.5em" width="1.5em" xmlns="http://www.w3.org/2000/svg"><path d="M6.50488 2H17.5049C17.8196 2 18.116 2.14819 18.3049 2.4L21.0049 6V21C21.0049 21.5523 20.5572 22 20.0049 22H4.00488C3.4526 22 3.00488 21.5523 3.00488 21V6L5.70488 2.4C5.89374 2.14819 6.19013 2 6.50488 2ZM19.0049 8H5.00488V20H19.0049V8ZM18.5049 6L17.0049 4H7.00488L5.50488 6H18.5049ZM9.00488 10V12C9.00488 13.6569 10.348 15 12.0049 15C13.6617 15 15.0049 13.6569 15.0049 12V10H17.0049V12C17.0049 14.7614 14.7663 17 12.0049 17C9.24346 17 7.00488 14.7614 7.00488 12V10H9.00488Z"></path></svg>
    <div class="popup">No Product on the cart.</div>
  </div>
</div>

  
  <div class="webcam-container">
    <canvas id="handCanvas" bind:this={handCanvasElement}></canvas>
    {#if timer > 0}
      <div class="timer">{timer}</div>
    {/if}

    <video bind:this={videoElement} autoplay class="webcam-video"></video>
    <canvas bind:this={canvasElement} style="display: none;"></canvas>
  </div>
  
  <div class="bottom-bar">
    {#each $clothes as item, index (item.id)}
      <img src={item.image}
           class="dock-icon { $currentIndex === index ? 'highlight' : '' }"
           alt={item.name}
           on:click={() => {$currentIndex = index;}}>
    {/each}
  </div>
  
  
  <div class="image-gallery">
    <button on:click={startCountdown}>Take pic</button>
    <div class="image-display">
      {#if $clothes.length > 0}
        <img src={$clothes[$currentIndex].image} class="displayed-image" alt="Displayed">
      {/if}
    </div>

    {#each $poses as image, index (image)}
      <img src={image}
           class="captured-image { $currentIndex === index ? 'highlight' : '' }"
           alt="Captured snapshot">
    {/each}
  </div>


  <style>
  .webcam-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 65px);
    width: 50%;
    position: absolute;
    left: 0;
    top: 65px; 
    overflow: hidden;
    }
  
  .webcam-video {
      height: 100%;
      width: 100%;
      transform: scaleX(-1);
      object-fit: cover;
    }
  
  #handCanvas {
      width: 100%;
      height: 100%;
      position: absolute;
      z-index: 2;
      transform: rotateY(180deg);
    }

    .timer {
      position: absolute;
      font-size: 3rem;
      color: white;
      z-index: 3;
    }

    #handCanvas {
      position: absolute;
      z-index: 1;
      transform: rotateY(180deg);
    }

    .image-gallery {
    position: absolute;
    top: 65px; 
    right: 0;
    width: 50%; 
    height: calc(100vh - 65px);
    overflow-y: auto; 
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    box-sizing: border-box;
  }

  .captured-image {
    max-width: 90%;
    margin-bottom: 1rem; 
    border-radius: 10px;
  }

  .displayed-image{
    max-width: 50%;
    margin-bottom: 1rem; 
    border-radius: 10px;
  }

  .bottom-bar {
  position: fixed;
  bottom: 0;
  margin-bottom: 10px;
  left: 50%; 
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80px;
  z-index: 100;
  background-color: rgba(55, 55, 55, 0.751); 
  border: 1px solid #2f2f2f;
  border-radius: 15px;
}

.bottom-bar img {
  max-width: 60px;
  margin: 0 8px;
  transition: transform 0.3s ease;
  border-radius: 10px; 
}

</style>