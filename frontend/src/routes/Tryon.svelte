<script lang="ts">
    let videoElement;
  
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
  
    import { onMount } from 'svelte';
    onMount(() => {
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
    <video bind:this={videoElement} autoplay class="webcam-video"></video>
  </div>
  