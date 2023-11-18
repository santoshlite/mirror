<script lang="ts">
  import { Router, Route, Link } from 'svelte-routing';
  import Home from './routes/Home.svelte'; 
  import Tryon from './routes/Tryon.svelte';
</script>


<div class="top-bar">
  <h1>Mirror</h1>
</div>

<main>

  <Router>
    <Route path="/" component={Home} />
    <Route path="/tryon" component={Tryon} />
  </Router>

</main>
