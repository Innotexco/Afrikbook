    

// function fetchAllItems() {
//     var fetch_all_items = document.getElementById('fetch_all_items').dataset.url;
//     let format = new Intl.NumberFormat()
//     $.ajax({
//         type: 'GET',
//         url: fetch_all_items,  
        
//         dataType: 'json',
//         success: function (data) {
//             itemlist(data, format)
//         },
//         error: function (error) {
//             console.error('Error fetching items by category:', error);
//         }
//     });
// }



// // Clear existing items
            // $('#items-container').empty();

            // // Append fetched items dynamically
            // data.items.forEach(function (item) {
            //     var itemHtml = `
            //         <div class="p-2 border rounded-md shadow-md" id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')">
            //             <img class="h-12 w-auto" src="media/${item.image}" alt="${item.item_name}" class="mb-2" />
            //             <div class="mt-4 md:mt-0">
            //                 <h2 class="text-sm font-semibold item_name line-clamp-1 truncate">${item.item_name}</h2>
            //                 <p class="mt-2 text-sm text-gray-600 hidden">${item.generated_code}</p>
            //                 <div class="mt-1 flex items-center">
            //                     <div class="flex items-center hidden">
            //                         <button id="reduce_qty" class="bg-gray-200 rounded-l-lg px-2 py-1" disabled>-</button>
            //                         <input type="text" class="w-6 qty px-2 py-1 text-gray-600" id="qty${item.id}" value="1" />
            //                         <button id="add_qty" class="bg-gray-200 rounded-r-lg px-2 py-1 cursor-pointer" disabled>+</button>
            //                     </div>
            //                     <span id="selling_price" class="font-medium text-sm item_price">$${item.selling_price}</span>
            //                 </div>
            //                 <div class="w-full px-2 hidden">
            //                     <button id="AddCart${item.generated_code}" onclick="AddToCart('${item.id}', '${item.generated_code}', '${item.image}', '${item.item_name}', '${item.selling_price}')"
            //                         class="add-to-cart-button w-10 bg-gray-900 dark:bg-gray-600 text-white p-2 rounded-full font-bold hover:bg-gray-800 dark:hover:bg-gray-700">
            //                         <svg xmlns="http://www.w3.org/2000/svg" class="h-8 inline-block " fill="none" viewBox="0 0 24 24" stroke="currentColor">
            //                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            //                         </svg>
            //                     </button>
            //                 </div>
            //             </div>
            //         </div>
            //     `;
            //     $('#items-container').append(itemHtml);
            // });