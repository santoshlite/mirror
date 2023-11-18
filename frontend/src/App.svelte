<script lang="ts">
  import { Router, Route, Link } from 'svelte-routing';
  import Tryon from './routes/Tryon.svelte';
</script>

<main>
  <Router>
    <div>
      <Link to="/tryon" class="nav-button">Go to Tryon</Link>
    </div>

    <Route path="/tryon" component={Tryon} />
  </Router>
</main>

<style>
  .nav-button {
    padding: 10px;
    background-color: #646cff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
    margin: 10px 0;
  }
</style>
