<script lang="ts">
  import { Router, Route, Link } from 'svelte-routing';
  import Home from './routes/Home.svelte'; 
  import Tryon from './routes/Tryon.svelte';
  import logo from './assets/logo.png'; 
</script>


<div class="top-bar">
  <div class="spacer"></div> 
  <a href="/" class="logo-container">
      <img src={logo} alt="Mirror Logo" class="logo"/>
  </a>
  <div class="spacer"></div> 
  <div class="icon-container">
    <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" class="text-xl" height="1.5em" width="1.5em" xmlns="http://www.w3.org/2000/svg"><path d="M6.50488 2H17.5049C17.8196 2 18.116 2.14819 18.3049 2.4L21.0049 6V21C21.0049 21.5523 20.5572 22 20.0049 22H4.00488C3.4526 22 3.00488 21.5523 3.00488 21V6L5.70488 2.4C5.89374 2.14819 6.19013 2 6.50488 2ZM19.0049 8H5.00488V20H19.0049V8ZM18.5049 6L17.0049 4H7.00488L5.50488 6H18.5049ZM9.00488 10V12C9.00488 13.6569 10.348 15 12.0049 15C13.6617 15 15.0049 13.6569 15.0049 12V10H17.0049V12C17.0049 14.7614 14.7663 17 12.0049 17C9.24346 17 7.00488 14.7614 7.00488 12V10H9.00488Z"></path></svg>
  </div>
</div>


<main>

  <Router>
    <Route path="/" component={Home} />
    <Route path="/tryon" component={Tryon} />
  </Router>

</main>
