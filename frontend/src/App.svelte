<script lang="ts">
  import { Router, Route, Link } from 'svelte-routing';
  import Home from './routes/Home.svelte'; 
  import Tryon from './routes/Tryon.svelte';
  import logo from './assets/logo.png'; 
</script>


<main>

  <Router>
    <Route path="/" component={Home} />
    <Route path="/tryon" component={Tryon} />
  </Router>

</main>
