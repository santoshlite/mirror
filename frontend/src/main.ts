import './app.css';
import App from './App.svelte';
import { Router } from 'svelte-routing';

const app = new App({
  target: document.getElementById('app'),
  props: {
    // Router component as a prop
    Router: Router
  }
})

export default app
