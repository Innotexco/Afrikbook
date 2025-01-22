
            
function showFilter() {

    var x = document.getElementById("filterMenu");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

    
$(document).ready(function () {
    // Function to fetch and display items
    function fetchAndDisplayItems() {
        
        $.ajax({
            type: 'GET',
            url: 'fetch-items/',  
            dataType: 'json',
            success: function (data) {
                // Clear existing items
                $('#items-container').empty();

                // Append fetched items dynamically
                data.items.forEach(function (item) {
                    var itemHtml = `
                        <div class="p-2 border rounded-md shadow-md" id="AddCart`+item.generated_code+`" onclick="AddToCart('`+item.id+`', '`+item.generated_code+`', '`+item.image+`', '`+item.item_name+`', '`+item.selling_price+`')">
                            <img class="h-20 w-full rounded-md" src="media/${item.image}" alt="${item.item_name}" class="mb-2" />
                            <div class="mt-4 md:mt-0">
                                <h2 class="text-sm font-semibold item_name line-clamp-1 truncate">${item.item_name}</h2>
                                <p class="mt-1 text-sm text-gray-600 hidden">${item.generated_code}</p>
                                <div class="mt-1 flex items-center">
                                    <div class="items-center hidden">
                                        <button id="reduce_qty" class="bg-gray-200 rounded-l-lg px-2 py-1" disabled>-</button>
                                        <input type="text" class="w-6 qty px-2 py-1 text-gray-600" id="qty${item.id}" value="1" />
                                        <button id="add_qty" class="bg-gray-200 rounded-r-lg px-2 py-1 cursor-pointer" disabled>+</button>
                                    </div>
                                    <span id="selling_price" class="font-medium text-sm item_price">$${item.selling_price}</span>
                                </div>
                                <div class="w-full px-2 hidden">
                                    <button id="AddCart`+item.generated_code+`" onclick="AddToCart('`+item.id+`', '`+item.generated_code+`', '`+item.image+`', '`+item.item_name+`', '`+item.selling_price+`')"
                                        class="add-to-cart-button w-10 bg-gray-900 dark:bg-gray-600 text-white p-2 rounded-full font-bold hover:bg-gray-800 dark:hover:bg-gray-700">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 inline-block " fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    $('#items-container').append(itemHtml);
                });
            },
            error: function (error) {
                console.error('Error fetching items:', error);
            }
        });
    }

    // Initial fetch and display items
    fetchAndDisplayItems();

    // You can call fetchAndDisplayItems on button click or any other event
    // Example:
    $('#fetch-items-button').on('click', function () {
        fetchAndDisplayItems();
    });

    displayCartItems();


});


function CheckIfItemExist(Itemlist, generated_code){
    const entry = Itemlist.find(([CART]) => CART === generated_code);
    if(entry){
        return true;
    }
}


function AddToCart(id, generated_code, image, item_name, selling_price){
    
    const FormalItem = sessionStorage.getItem('Items');
    let list;

    if(FormalItem === null){
        list = [];
    }else{
        list = JSON.parse(FormalItem);
    }

    if(!CheckIfItemExist(list, generated_code)){

        let qty = document.getElementById('qty'+id).value;
        alert(qty);
        let AddedItems = [generated_code, image, item_name, selling_price, qty]

        list.push(AddedItems);

        sessionStorage.setItem('Items', JSON.stringify(list));

        console.log(JSON.parse(sessionStorage.getItem('Items')));
        console.log(JSON.parse(sessionStorage.getItem('Items'[4])));
        alert(JSON.parse(sessionStorage.getItem('Items')));

        displayCartItems();
    }
    else {
        // alert("Eyi Item Already Exit !!!")
        // Find the index of the existing item in the cart
        const existingItemIndex = list.findIndex(item => item[0] === generated_code);

        // Increment the quantity of the existing item
        //list[existingItemIndex][4] += 1;

        list[existingItemIndex][4] = Number(list[existingItemIndex][4]) + 1 || 1;


        console.log(list[existingItemIndex][4])
        sessionStorage.setItem('Items', JSON.stringify(list));

        console.log(JSON.parse(sessionStorage.getItem('Items')));
        displayCartItems();
    }

}


function CartItemCount() {
    const cartItems = JSON.parse(sessionStorage.getItem('Items')) || [];
    const itemCountElement = document.getElementById('cart-item-count');

    // Count the number of items in the cart
    const itemCount = cartItems.length;

    // Display the item count on your HTML template
    if (itemCountElement) {
        itemCountElement.textContent = itemCount.toString();
    }
}
            

// Initialize cartItems with a valid array
let cartItems = [];

// Call functions that depend on cartItems
displayCartItems();


function displayCartItems() {
    const cartContainer = document.getElementById('cart-container');
    const totalcartContainer = document.getElementById('total-cart-container');
    const checkoutContainer = document.getElementById('checkout-container');
    const totalcheckoutContainer = document.getElementById('checkout-total-cart-container');
    const cartItems = JSON.parse(sessionStorage.getItem('Items'));

    // Clear existing cart items
    cartContainer.innerHTML = '';
    totalcartContainer.innerHTML = '';
    checkoutContainer.innerHTML = '';
    totalcheckoutContainer.innerHTML = '';

    let itemCount = 0;
    let totalPrice = 0;

    // Check if there are items in the cart
    if (cartItems && cartItems.length > 0) {
        cartItems.forEach(function (item) {

            itemCount += item[4]; // Assuming item[4] represents the quantity
            totalPrice += item[3] * item[4]; // Assuming item[3] is the price and item[4] is the quantity
            
            const cartItemHtml = `
                <div class="card sm:overflow-x">
                    <div class="mb-3 bg-blue-gray-50 rounded-lg w-full text-blue-gray-700 py-2 px-2 flex justify-between items-center">
                        <div class="flex justify-between items-center">
                            <div class="w-16 sm:w-24 md:w-32 flex gap-2">
                                <img src="media/${item[1]}" alt="" class="rounded-lg h-10 w-10 bg-white shadow mr-2"/>
                                <article>
                                    <h5 class="text-sm font-semibold">${item[2]}</h5>
                                    <p class="text-xs hidden">$${item[3]}</p>
                                    <p class="text-xs block font-semibold"> $${(item[3] * item[4]).toFixed(2)}</p>
                                </article>
                            </div>
                            <div class="w-28 grid grid-cols-3 justify-center gap-2 ml-12 sm:ml-12 md:ml-12 xl:ml-24">
                                <button id="ReduceCart`+item[0]+`" onclick="ReduceQty('`+item.id+`', '`+item[0]+`', '`+item.image+`', '`+item.item_name+`', '`+item.selling_price+`')" class="rounded-lg text-center py-1 text-white bg-blue-gray-600 hover:bg-blue-gray-700 focus:outline-none">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-3 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                                    </svg>
                                </button>

                                <input type="text" id="qty${item.id}" value="${item[4]}" class="bg-white rounded-lg text-center shadow focus:outline-none focus:shadow-lg text-sm">
                                
                                <button id="AddCart`+item[0]+`" onclick="AddQty('`+item.id+`', '`+item[0]+`', '`+item.image+`', '`+item.item_name+`', '`+item.selling_price+`')" class="rounded-lg text-center py-1 text-white bg-blue-gray-600 hover:bg-blue-gray-700 focus:outline-none">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-3 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                        <div class="flex-grow text-right text-lg p-1 w-8">
                            <button id="RmvFromCart`+item[0]+`" onclick="RemoveItem('`+item.id+`', '`+item[0]+`', '`+item.image+`', '`+item.item_name+`', '`+item.selling_price+`')" class="text-blue-gray-300 hover:text-pink-500 focus:outline-none">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            `;

            cartContainer.innerHTML += cartItemHtml;

            const checkoutReceiptHtml = `
                <article >
                    <tr class="text-center">
                        <td class="py-2 text-center" >*</td>
                        <td class="py-2 text-left">
                            <span >${item[2]}</span>
                            <br />
                            <small >$${item[3]}</small>
                        </td>
                        <td class="py-2 text-center">${item[4]}</td>
                        <td class="py-2 text-right">$${(item[3] * item[4]).toFixed(2)}</td>
                    </tr>
                </article>

            `;
            checkoutContainer.innerHTML += checkoutReceiptHtml;

        });
    } else {
        // Display a message if the cart is empty
        const emptyCartHtml = `
            <div class="flex-1 w-full p-4 opacity-25 select-none flex flex-col flex-wrap content-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <p>
                    CART IS EMPTY
                </p>
            </div>
        `;
        cartContainer.innerHTML = emptyCartHtml;
    }


    // Display the count and total price
    const cartSummaryHtml = `
        <b>TOTAL:</b>
        <p id="totalPrice" class="text-right w-full">$${totalPrice.toFixed(2)}</p>
    `;
    totalcartContainer.innerHTML += cartSummaryHtml;

    // Display Chectout total price 
    const checkoutSummaryHtml = `
        <b>TOTAL:</b>
        <p class="text-right w-full">$${totalPrice.toFixed(2)}</p>
    `;
    totalcheckoutContainer.innerHTML += checkoutSummaryHtml;

    CartItemCount();

    calculateChange();

}

// Function to calculate and display change
function calculateChange() {
    // Get the total price
    const totalPrice = parseFloat(document.getElementById('totalPrice').innerText.replace('$', ''));

    // Get the cash input value
    const cashInput = parseFloat(document.getElementById('cashInput').value);

    // Calculate the change
    const change = cashInput - totalPrice;

    // Display the change
    if (change > 0) {
        // Change is positive
        document.getElementById('changeDisplay').innerHTML = `
            <div class="flex mb-3 text-lg font-semibold text-blue-gray-700 rounded-lg py-2 px-3">
                <div class="text-cyan-800">CHANGE</div>
                <div class="text-right flex-grow text-cyan-600">
                    $${change.toFixed(2)}
                </div>
            </div>
        `;
    } else if (change < 0) {
        // Change is negative
        document.getElementById('changeDisplay').innerHTML = `
            <div class="flex mb-3 text-lg font-semibold bg-cyan-50 text-blue-gray-700 rounded-lg py-2 px-3">
                <p class="flex text-right w-full font-semibold text-pink-300">
                    $${Math.abs(change).toFixed(2)}
                </p>
            </div>
        `;
    } else {
        // Change is zero
        document.getElementById('changeDisplay').innerHTML = '';
    }
}
            

function AddQty(id, generated_code, image, item_name, selling_price) {
    alert("Eyia Tiyai Ofu !!!" + generated_code);

    const cartItems = JSON.parse(sessionStorage.getItem('Items'));

    let list;

    if (cartItems === null) {
        list = [];
    } else {
        list = cartItems; 
    }

    // Find the index of the existing item in the cart
    const existingItemIndex = list.findIndex(item => item[0] === generated_code);

    console.log(existingItemIndex);
    // Increment the quantity of the existing item
    if (existingItemIndex !== -1 && list[existingItemIndex] && list[existingItemIndex][4] !== undefined) {
        list[existingItemIndex][4] = Number(list[existingItemIndex][4]) + 1 || 1;

        
        sessionStorage.setItem('Items', JSON.stringify(list));

        displayCartItems();
    } else {
        console.error("Error: Item not found or missing required properties.");
    }
}


function ReduceQty(id, generated_code, image, item_name, selling_price) {
    
    alert("Eyia minus Ofu !!!" + generated_code);

    const cartItems = JSON.parse(sessionStorage.getItem('Items'));

    let list;

    if (cartItems === null) {
        list = [];
    } else {
        list = cartItems; 
    }

    // Find the index of the existing item in the cart
    const existingItemIndex = list.findIndex(item => item[0] === generated_code);

    console.log(existingItemIndex);
    // Increment the quantity of the existing item
    if (existingItemIndex !== -1 && list[existingItemIndex] && list[existingItemIndex][4] !== undefined) {
        list[existingItemIndex][4] = Number(list[existingItemIndex][4]) - 1 || 1;

        
        sessionStorage.setItem('Items', JSON.stringify(list));

        displayCartItems();
    } else {
        console.error("Error: Item not found or missing required properties.");
    }
}


function RemoveItem(id, generated_code, image, item_name, selling_price) {
    
    alert(generated_code + "Eyia K Egia");

    const cartItems = JSON.parse(sessionStorage.getItem('Items'));

    let list;

    if (cartItems === null) {
        list = [];
    } else {
        list = cartItems; 
    }

    // Find the index of the existing item in the cart
    const selectedIndex = list.findIndex(item => item[0] === generated_code);

    if (selectedIndex !== null && selectedIndex !== undefined && cartItems && cartItems.length > selectedIndex) {
        // Remove the selected item from the cartItems array
        cartItems.splice(selectedIndex, 1);

        // Save the updated cartItems array back to sessionStorage
        sessionStorage.setItem('Items', JSON.stringify(cartItems));

        // Refresh the displayed cart items
        displayCartItems();
    }

}


function clearCart() {
    // Clear the cart items from session storage
    sessionStorage.removeItem('Items');

    displayCartItems();
}


function generateReceipt() {

    Checkout.showModal();
    // Generate a random receipt number (you can modify this logic based on your requirements)
    const receiptNumber = Math.floor(Math.random() * 1000000) + 1;

    // Get the current date and time
    const currentDate = new Date();
    const formattedDate = currentDate.toLocaleDateString();
    const formattedTime = currentDate.toLocaleTimeString();

    // Display the generated receipt number, date, and time on your HTML template
    const receiptNumberElement = document.getElementById('receipt-number');
    const dateElement = document.getElementById('receipt-date');
    const timeElement = document.getElementById('receipt-time');

    if (receiptNumberElement && dateElement && timeElement) {
        receiptNumberElement.textContent = `No: ${receiptNumber}`;
        dateElement.textContent = `Date: ${formattedDate}`;
        timeElement.textContent = `Time: ${formattedTime}`;
    }
}
           
 
function searchItems() {
    var keyword = document.querySelector('[x-model="keyword"]').value.trim().toLowerCase();
    
    // If the keyword is empty, clear the items container
    if (keyword === '') {
        // $('#items-container').empty();
        displayCartItems();
        //return;
    }

    $.ajax({
        type: 'GET',
        url: '/fetch-items-by-keyword/', 
        data: {
            'keyword': keyword
        },
        dataType: 'json',
        success: function (data) {
            // Clear existing items
            $('#items-container').empty();

            // Append fetched items dynamically
            data.items.forEach(function (item) {
                var itemHtml = `
                    <div class="p-2 border rounded-md shadow-md" id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')">
                        <img class="h-12 w-auto" src="media/${item.image}" alt="${item.item_name}" class="mb-2" />
                        <div class="mt-4 md:mt-0">
                            <h2 class="text-sm font-semibold item_name line-clamp-1 truncate">${item.item_name}</h2>
                            <p class="mt-2 text-sm text-gray-600 hidden">${item.generated_code}</p>
                            <div class="mt-1 flex items-center">
                                <div class="items-center hidden">
                                    <button id="reduce_qty" class="bg-gray-200 rounded-l-lg px-2 py-1" disabled>-</button>
                                    <input type="text" class="w-6 qty px-2 py-1 text-gray-600" id="qty${item.id}" value="1" />
                                    <button id="add_qty" class="bg-gray-200 rounded-r-lg px-2 py-1 cursor-pointer" disabled>+</button>
                                </div>
                                <span id="selling_price" class="font-medium text-sm item_price">$${item.selling_price}</span>
                            </div>
                            <div class="w-full px-2 hidden">
                                <button id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')"
                                    class="add-to-cart-button w-10 bg-gray-900 dark:bg-gray-600 text-white p-2 rounded-full font-bold hover:bg-gray-800 dark:hover:bg-gray-700">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 inline-block " fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                $('#items-container').append(itemHtml);
            });
        },
        error: function (error) {
            console.error('Error fetching items by keyword:', error);
        }
    });
}


function fetchItemsByCategory(category) {
    $.ajax({
        type: 'GET',
        url: '/fetch-items-by-category/' + category,  
        data: {
            'category_name': category
        },
        dataType: 'json',
        success: function (data) {
            // Clear existing items
            $('#items-container').empty();

            // Append fetched items dynamically
            data.items.forEach(function (item) {
                var itemHtml = `
                    <div class="p-2 border rounded-md shadow-md" id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')">
                        <img class="h-12 w-auto" src="media/${item.image}" alt="${item.item_name}" class="mb-2" />
                        <div class="mt-4 md:mt-0">
                            <h2 class="text-sm font-semibold item_name line-clamp-1 truncate">${item.item_name}</h2>
                            <p class="mt-2 text-sm text-gray-600 hidden">${item.generated_code}</p>
                            <div class="mt-1 flex items-center">
                                <div class="flex items-center hidden">
                                    <button id="reduce_qty" class="bg-gray-200 rounded-l-lg px-2 py-1" disabled>-</button>
                                    <input type="text" class="w-6 qty px-2 py-1 text-gray-600" id="qty${item.id}" value="1" />
                                    <button id="add_qty" class="bg-gray-200 rounded-r-lg px-2 py-1 cursor-pointer" disabled>+</button>
                                </div>
                                <span id="selling_price" class="font-medium text-sm item_price">$${item.selling_price}</span>
                            </div>
                            <div class="w-full px-2 hidden">
                                <button id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')"
                                    class="add-to-cart-button w-10 bg-gray-900 dark:bg-gray-600 text-white p-2 rounded-full font-bold hover:bg-gray-800 dark:hover:bg-gray-700">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 inline-block " fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                $('#items-container').append(itemHtml);
            });
        },
        error: function (error) {
            console.error('Error fetching items by category:', error);
        }
    });
}


function fetchAllItems() {
    $.ajax({
        type: 'GET',
        url: 'fetch-all-items/',  
        
        dataType: 'json',
        success: function (data) {
            // Clear existing items
            $('#items-container').empty();

            // Append fetched items dynamically
            data.items.forEach(function (item) {
                var itemHtml = `
                    <div class="p-2 border rounded-md shadow-md" id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')">
                        <img class="h-12 w-auto" src="media/${item.image}" alt="${item.item_name}" class="mb-2" />
                        <div class="mt-4 md:mt-0">
                            <h2 class="text-sm font-semibold item_name line-clamp-1 truncate">${item.item_name}</h2>
                            <p class="mt-2 text-sm text-gray-600 hidden">${item.generated_code}</p>
                            <div class="mt-1 flex items-center">
                                <div class="flex items-center hidden">
                                    <button id="reduce_qty" class="bg-gray-200 rounded-l-lg px-2 py-1" disabled>-</button>
                                    <input type="text" class="w-6 qty px-2 py-1 text-gray-600" id="qty${item.id}" value="1" />
                                    <button id="add_qty" class="bg-gray-200 rounded-r-lg px-2 py-1 cursor-pointer" disabled>+</button>
                                </div>
                                <span id="selling_price" class="font-medium text-sm item_price">$${item.selling_price}</span>
                            </div>
                            <div class="w-full px-2 hidden">
                                <button id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')"
                                    class="add-to-cart-button w-10 bg-gray-900 dark:bg-gray-600 text-white p-2 rounded-full font-bold hover:bg-gray-800 dark:hover:bg-gray-700">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 inline-block " fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                $('#items-container').append(itemHtml);
            });
        },
        error: function (error) {
            console.error('Error fetching items by category:', error);
        }
    });
}

            

