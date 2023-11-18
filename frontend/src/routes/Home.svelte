<script lang="ts">
    import { Router, Route, Link } from 'svelte-routing';
	let cart = [];
	let products = [
		{id: 1, name: "Apple", image: "https://www.applesfromny.com/wp-content/uploads/2020/05/Jonagold_NYAS-Apples2.png", price: 10, quantity: 1},
		{id: 2, name: "Orange", image: "https://5.imimg.com/data5/VN/YP/MY-33296037/orange-600x600-500x500.jpg", price: 11, quantity: 1},
		{id: 3, name: "Grapes", image: "https://www.aicr.org/wp-content/uploads/2020/01/shutterstock_533487490-640x462.jpg", price: 12, quantity: 1},
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

	$: total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
</script>
  
  <h1>Select Products To Try</h1>

<p>There are {cart.length} items in your cart</p>
<div class="product-list">
	{#each products as product}
	<div>
		<div class="image" style="background-image: url({product.image})"></div>
	<h4>{product.name}</h4>
	<p>₹{product.price}</p>
	<button on:click={() => addToCart(product)}>Add to cart</button>
	</div>
	{/each}
</div>

<div class="cart-list">
	{#each cart as item }
		{#if item.quantity > 0}
		<div class="cart-item">
			<img width="50" src={item.image} alt={item.name}/>
			<p>₹{item.price * item.quantity}</p>
		</div>
		{/if}
	{/each}
	<div class="total">
		<h4>Total: ₹ {total}</h4>
	</div>
</div>


<Link to="/tryon">Try Now →</Link>


<style>
	.product-list, .cart-item {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
	}
	
	.image {
		height: 150px;
		width: 150px;
		background-size: contain;
		background-position: center;
		background-repeat: no-repeat;
	}
	.total {
		text-align: right;
	}
	
	.cart-list {
		border: 2px solid;
		padding: 10px;
	}
</style>