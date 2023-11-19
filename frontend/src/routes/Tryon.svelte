<script lang="ts">
    import { onMount } from 'svelte';
    import { get, writable } from 'svelte/store';
    import { navigate } from 'svelte-routing';
    import logo from '/src/assets/logo.png'; 
    import { clothes } from '../store.js'; 
    import Icon from '@iconify/svelte';
    import OpenAI from 'openai';

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
    let api_result = [];
    let seg_result;
    let cameraSound = new Audio('/src/assets/camera.mp3');
    let showSpinner = true;
    let handCanvasContext: CanvasRenderingContext2D;
    let videoElement;
    let timer;
    let imageDataURL;
    let canvasElement;
    let countdown;
    let countdown_on = false;
    let newResult;


    function getAllPrompts() {
    const items = get(clothes); 
    return items.map(item => item.name);
  }

    let promptsArray = getAllPrompts(); // Call the function to get all images

    console.log(promptsArray);

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

      const TAKE_PHOTO_GESTURE = "Victory";
      const TAKE_PHOTO_SCORE_THRESHOLD = 0.7;
      let victorySignCurrentlyActive : boolean = false;

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
        return (slopeBounds.horizontal.min <= slope && slopeBounds.horizontal.max >= slope);
      }

      async function frameLoop() {
        if (handLandmarker && gestureRecognizer) {
          let startTimeMs = performance.now();
          if (lastVideoTime !== videoElement.currentTime) {
            lastVideoTime = videoElement.currentTime;
            handLandmarkerResults = handLandmarker.detectForVideo(videoElement, startTimeMs);
            gestureRecognizerResults = gestureRecognizer.recognizeForVideo(videoElement, startTimeMs);
          }
          let gestures = gestureRecognizerResults.gestures;
          if (gestures && gestures.length > 0 && gestures[0].length > 0 && gestures[0][0].categoryName === TAKE_PHOTO_GESTURE && gestures[0][0].score >= TAKE_PHOTO_SCORE_THRESHOLD) {
          
            if (!victorySignCurrentlyActive) {
                console.log("user activated picture");
                startCountdown();
                victorySignCurrentlyActive = true;
              }
          }
          else {
            victorySignCurrentlyActive = false;
          }

          handCanvasContext.clearRect(0, 0, handCanvasElement.width, handCanvasElement.height);
          if (handLandmarkerResults.landmarks && handLandmarkerResults.landmarks.length > 0 && handLandmarkerResults.landmarks[0].length > 8) {
            MediaPipeDrawing.drawLandmarks([handLandmarkerResults.landmarks[0][8]], {color: "lime", lineWidth: 2});
            currentPos = handLandmarkerResults.landmarks[0][8];
            if (previousPos !== undefined) {
              if (dista(currentPos, previousPos) < EPS) {
                stillFrameCounter++;
                if (moving && stillFrameCounter == STILL_FRAME_THRESHOLD) {
                  motionEndTime = now();
                  moving = false;
                  console.log("movement ended");
                  
                  // Calculate the slope and average velocity
                  let slope = (currentPos.y - startPos.y) / (currentPos.x - startPos.x);
                  let avgVelocity = (dista(currentPos, startPos) / (motionEndTime - motionStartTime));

                  // Check if enough time has passed since the last swipe
                  let currentTime = now();
                  if (avgVelocity >= MIN_SWIPE_VELOCITY && (currentTime - lastSwipeTime) > MIN_SWIPE_BUFFER_TIME) {
                    console.log("fast enough to be a swipe");
                    
                  
                    if (isHorizontal(slope)) {
                      swipe();
                      lastSwipeTime = currentTime; // Update last swipe time
                    }
                  }
                }
              }
              else {
                if (!moving) {
                  motionStartTime = now();
                  startPos = currentPos;
                  console.log("movement started");
                  moving = true;
                  stillFrameCounter = 0;
                }
              }
            }
            previousPos = currentPos;
          }
        }
        window.requestAnimationFrame(frameLoop);
      }
      await frameLoop();
    }

    
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
  
  if(!countdown_on){
    countdown_on = true;
    timer = 5;
    countdown = setInterval(() => {
      timer -= 1;
      if (timer <= 0) {
        clearInterval(countdown);
        takePicture();
        countdown_on = false;
      }
    }, 1000);
  }
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
    imageDataURL = canvasElement.toDataURL('image/png');
    cameraSound.play();
   makeApiCall("Montreal Canadiens Jersey", imageDataURL);
  }

  async function analyzeImage(image_url) {

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${import.meta.env.VITE_OPENAI_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "You are a professional stylist. Give pros and cons of my style based on layering, colouring and contrast. Be short and consice. Use bullet points. Bold key words. Max 4 bullet points total. No full sentences."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": image_url
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  })
  });
  const data = await response.json();
  console.log(data[0]);
}


  // This function will be called to make the API request
  async function makeApiCall(prompt, imageBase64) {
    imageBase64 = imageBase64.split(',')[1];

    try {
      const response = await fetch('https://fine-elegant-dragon.ngrok-free.app/seg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          img: imageBase64
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      seg_result = await response.json();

    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
    }

    for(prompt in promptsArray){
        try {
        const response = await fetch('https://fine-elegant-dragon.ngrok-free.app/inpaint', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            prompt: prompt
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        newResult = await response.json();
        api_result.push(newResult); 

      } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
      }
    }

    showSpinner = false;
  }


    onMount(() => {
      handCanvasContext = handCanvasElement.getContext('2d');
      MediaPipeDrawing = new MediaPipeVision.DrawingUtils(handCanvasContext);
      startWebcam();
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

</div>
  
  <div class="webcam-container">
    <canvas id="handCanvas" bind:this={handCanvasElement}></canvas>
    <img src={imageDataURL} class="captured-image-display" />

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
    {#if showSpinner}
      <Icon icon="gg:spinner" style="font-size: 75px; animation: spin 1.5s linear infinite;" />
    {:else}
      <img src={"data:image/png;base64,"+api_result[$currentIndex].img} class="displayed-image" alt="Displayed">
    {/if}
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
      height: 95%;
      width: 95%;
      transform: scaleX(-1);
      object-fit: cover;
      border-radius: 10px;
      border: 2px solid var(--translucent-grey);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

  #handCanvas {
      height: 95%;
      width: 95%;
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

  .image-gallery {
    display: flex; 
    justify-content: center;
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

.highlight {
    border: 3px solid #25c55e; 
  }

.captured-image-display {
  position: absolute;
  top: 18px;
  right: 20px;
  border: 2px solid var(--translucent-grey);
  border-radius: 10px;
  max-width: 125px; 
  transition: opacity 0.5s ease; 
  z-index: 10;
}

</style>