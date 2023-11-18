<script>
    import { clothes } from '../store.js'; 
    export let name = "";
    export let manufacturer = "";
    export let price = "";
    export let image = "";
    export let id; 

    let isSelected = false;

    function toggleSelection() {
      clothes.update(items => {
        let index = items.findIndex((product) => product.id === id);

        if (index !== -1) {
          let filteredItems = items.filter((product) => product.id !== id);
          console.log('Item removed, new length:', filteredItems.length);
          isSelected = false; 
          return filteredItems;
        } else {
          let newItems = [...items, { id, name, manufacturer, price, image }];
          console.log('Item added, new length:', newItems.length);
          isSelected = true; 
          return newItems;
        }
      });
    
    }
</script>

<div class="product-card">
    <img src={image} alt={name} class="product-image" />
    <div class="product-details">
        <div class="product-name">{name}</div>
        <div class="product-manufacturer">from {manufacturer}</div>
        <button class="buy-button" on:click={toggleSelection}
                class:selected={isSelected}>
            {#if isSelected}
                Selected
            {:else}
            Select
            {/if}
        </button>
    </div>
</div>
  
  
  
  <style>
    .product-card {
    background: #FFF;
    border-radius: 10px;
    border: 1.5px solid #e4e7eb;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    max-width: 200px;
    margin: 10px;
    }
    
    .favorite {
      align-self: flex-end;
      padding: 10px;
      cursor: pointer;
    }
  
    .product-image {
        width: 100%;
        height: 150px; 
        object-fit: cover;
        background: #FAFAFA; 
}

  
    .product-details {
      padding: 16px;
    }
  
    .product-name {
      font-size: 1rem;
      font-weight: bold;
      margin-bottom: 4px;
    }
  
    .product-manufacturer {
      font-size: 0.8rem;
      color: #666;
      margin-bottom: 4px;
    }
  
    .product-metadata {
      font-size: 0.9rem;
      color: #333;
      margin-bottom: 8px;
    }
  
    .product-price {
      font-size: 1rem;
      font-weight: bold;
      color: #333;
      margin-bottom: 8px;
    }
  
  
.buy-button {
  padding: 8px 10px;
  margin-top: 5px;
  font-size: medium;
  font-weight: 700;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  background-image: linear-gradient(180deg, #6ed489, #25c55e); 
  border: 1px solid #1eb957;
  color: white;
  transition: background-color 0.2s, border-color 0.2s;
}

.buy-button:hover {
  background-image: linear-gradient(180deg, #57c478, #1db954); 
  border: 1px solid #169a48; 
  color: #f8f8f8;
  transform: scale(1.02);
}

.buy-button.selected {
    background-image: linear-gradient(180deg, #5a5a5a, #010101); 
    border: 1px solid #020202;
    color: white;
    }

.buy-button:not(.selected):hover {
        transform: scale(1.02);
    }


  </style>
  