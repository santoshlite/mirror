<script lang="ts">
    import { Router, Route, Link } from 'svelte-routing';
    import { clothes } from '../store.js'; 
    import Product from '/src/lib/Product.svelte';
    import logo from '/src/assets/logo.png'; 
    import { writable } from 'svelte/store';
    import habs2 from '/src/assets/habs2.png';
    
	let cart = [];
  let clothes_length;
  $: clothes_length = $clothes.length;

	let products = [
    {id: 1, name: "Airism Cotton T-Shirt",  prompt: "Generate an image of a plain forest green t-shirt. It should be short-sleeved with a round neckline and a regular fit. The fabric should look smooth with no logos or designs, and the hem should appear neatly stitched.", image: "https://image.uniqlo.com/UQ/ST3/WesternCommon/imagesgoods/457337/item/goods_54_457337.jpg?width=750", price: 12.99, manufacturer:"Uniqlo"},
    {id: 2, name: "Short Sleeve Polo Shirt", prompt: "Create an image of a white polo shirt with short sleeves and a soft collar. It should have a two-button placket, with the buttons undone. The shirt's fabric should look smooth and pristine, with a slight sheen indicating a quality material. The sleeves should have ribbed armbands and the shirt should have a straight hem. No logo or design should be visible, maintaining a classic and versatile appearance.", image: "https://image.uniqlo.com/UQ/ST3/WesternCommon/imagesgoods/455388/sub/goods_455388_sub14.jpg?width=750", price: 24.99, manufacturer:"Uniqlo"},
    {id: 3, name: "Montreal Canadiens Jersey", prompt: "Red Montreal Canadiens jersey", image: habs2, manufacturer: "Montreal Canadiens"},
		{id: 4, name: "Short Sleeve Polo Shirt", prompt: "Short Sleeve Polo Shirt", image: "https://image.uniqlo.com/UQ/ST3/WesternCommon/imagesgoods/455388/sub/goods_455388_sub14.jpg?width=750", price: 24.99, manufacturer:"Uniqlo"},
		{id: 5, name: "Flannel Long Sleeve Shirt", prompt: "Flannel Long Sleeve Shirt", image: "https://image.uniqlo.com/UQ/ST3/WesternCommon/imagesgoods/462408/sub/goods_462408_sub14.jpg?width=750", price: 15.99, manufacturer:"Uniqlo"},
		{id: 6, name: "Fleece Long Sleeve Jacket", prompt: "Fleece Long Sleeve Jacket", image: "https://image.uniqlo.com/UQ/ST3/WesternCommon/imagesgoods/462028/sub/goods_462028_sub14.jpg?width=750", price: 20.99, manufacturer:"Uniqlo"},
	]
	
	const addToCart = (product) => {
		for(let item of cart) {
				if(item.id === product.id) {
					product.quantity += 1
					cart = cart;
					return;
				}
		}
		cart = [...cart, product]
	}

	$: total = cart.reduce((sum, item) => sum + item.price, 0)
</script>

<div class="top-bar">
    <div class="spacer"></div> 
    <a href="/" class="logo-container">
        <img src={logo} alt="Mirror Logo" class="logo"/>
    </a>
    <div class="spacer"></div> 

    <!--
    <div class="icon-container">
      <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" class="text-xl" height="1.5em" width="1.5em" xmlns="http://www.w3.org/2000/svg"><path d="M6.50488 2H17.5049C17.8196 2 18.116 2.14819 18.3049 2.4L21.0049 6V21C21.0049 21.5523 20.5572 22 20.0049 22H4.00488C3.4526 22 3.00488 21.5523 3.00488 21V6L5.70488 2.4C5.89374 2.14819 6.19013 2 6.50488 2ZM19.0049 8H5.00488V20H19.0049V8ZM18.5049 6L17.0049 4H7.00488L5.50488 6H18.5049ZM9.00488 10V12C9.00488 13.6569 10.348 15 12.0049 15C13.6617 15 15.0049 13.6569 15.0049 12V10H17.0049V12C17.0049 14.7614 14.7663 17 12.0049 17C9.24346 17 7.00488 14.7614 7.00488 12V10H9.00488Z"></path></svg>
      <div class="popup">  No Product on the cart.</div>
            <div class="cart-list">
                {#each cart as item }
                    {#if item.quantity > 0}
                    <div class="cart-item">
                        <img width="50" src={item.image} alt={item.name}/>
                        <p>${item.price}</p>
                    </div>
                    {/if}
                {/each}
                <div class="total">
                    <h4>Total: $ {total}</h4>
                </div>  
  
    </div>
    -->

  </div>

  <p class="tagline">All of the benefits of shopping. <br> None of the pain.</p>

<div class="home-body">
  <h1>Select Products To Try</h1>
    <!--
    <p>There are {cart.length} items in your cart</p>
    -->
    <div class="product-list">
        {#each products as product}

        <Product 
        name={product.name} 
        prompt = {product.prompt}
        id = {product.id}
        manufacturer={product.manufacturer} 
        price={product.price} 
        image={product.image} />

        {/each}
    </div>
</div>


<br><br>
<p>Made with </p>

{#if clothes_length > 0}
  <div class="try-now-button-container">
    <span class="badge">{clothes_length}</span>
    <Link to="/tryon" class="try-now-button">Try Now →</Link>
  </div>
{:else}
<div class="try-now-button-container-disabled">
    <Link class="try-now-button" style="pointer-events:none">Try Now →</Link>
</div>
{/if}


<style>
    .try-now-button-container {
      position: fixed;
      bottom: 20px; 
      right: 20px; 
      z-index: 10;
      display: inline-block;
      padding: 10px 20px; 
      background-image: linear-gradient(180deg,#6ed489,#25c55e); 
      border: 1px solid #1eb957;
      text-decoration: none; 
      border-radius: 30px;
      box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2); 
      transition: background-color 0.3s ease;
      color: white;
      transition: background-color 0.2s, border-color 0.2s, transform 0.2s; 
    }

    .try-now-button-container-disabled {
      position: fixed;
      bottom: 20px; 
      right: 20px; 
      z-index: 10;
      display: inline-block;
      padding: 10px 20px; 
      background-image: linear-gradient(180deg,#cdcdcd,#828282);
      border: 1px solid #999999;
      text-decoration: none; 
      border-radius: 30px;
      box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2); 
      transition: background-color 0.3s ease;
      color: white;
      transition: background-color 0.2s, border-color 0.2s, transform 0.2s; 
    }

    .try-now-button-container:hover {
      background-color: #59a1ed;
      color: white;
      transform: scale(1.1);
    }
  
    .try-now-button {
     color: white;
      display: inline-block;
      padding: 10px 20px; 
      border-radius: 30px;
      text-decoration: none; 
      font-size: 16px; 
      box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2); 
    }
  
    .badge {
    position: absolute;
    top: -5px;
    right: -5px; 
    background-color: rgb(33, 110, 253);
    color: white;
    border-radius: 50%; 
    width: 20px; 
    height: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 0.75rem; 
    font-weight: 500;
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
}
  </style>