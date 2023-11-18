<script lang="ts">
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';

    const poses = writable([]); 


    let videoElement;
    let canvasElement;
    let timer = 5;
    let countdown;
  
    function startWebcam() {
      if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            videoElement.srcObject = stream;
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