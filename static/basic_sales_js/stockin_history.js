
    function myjaxfunct(res){
        
        $('#Stockin_History .default').remove();
        $('#Stockin_History .outlet').empty();
        currency_symbol = $('#currency_symbol').val();
    
        res.data.forEach(function(item, index) {
            let newRow = $('<tr id="' + item.id + '">');
            // Add data to the row
            newRow.append('<td class="px-4 py-1 text-sm">' + (index + 1) + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.datetx + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.item + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.item_code + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + currency_symbol +''+item.selling_price + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.quantity + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm"> ' + item.manufacture_date + ' </td>');
            newRow.append('<td class="px-4 py-1 text-sm"> ' + item.expiry_date + ' </td>');
            newRow.append('<td class="px-4 py-1 text-sm"> ' + item.token_id + ' </td>');
            newRow.append('<td class="px-4 py-1 text-sm"> ' + item.Userlogin + ' </td>');
    
            // Add more columns as needed
            let svgElement = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" >\
                                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" ></path> </svg>');
    
            newRow.append('<td class="px-4 py-1"> <div class="flex items-center space-x-4 text-sm">\
                            <button onclick="Delete_Stockin_History( ' + item.id + ')" class="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-red-600 rounded-lg focus:outline-none focus:shadow-outline-gray" aria-label="Delete">' + svgElement[0].outerHTML  +'</button> </div> </td></tr>');
            
                // Add more columns as needed
                $('#Stockin_History .outlet').append(newRow);
        });
        // Append the row to the table body
            
    
    }
    
    // DELETE STOCKIN HISTORY
        // function Delete_Stockin(res){
            
        //     $('#Stockin_History .old').remove();
        //     $('#Stockin_History .new').empty();
        //     res.data.forEach(function(stockin, index) {
        //         let newRow = $('<tr class="text-gray-700 dark:text-gray-400" id="' + stockin.id + '">');
        //         // Add data to the row
        //         newRow.append('<td class="px-4 py-1 text-sm">' + (index + 1) + '</td>');
        //         newRow.append('<td class="px-4 py-1 text-sm">' + stockin.datetx + '</td>');
        //         newRow.append('<td class="px-4 py-1 text-sm">' + stockin.item + '</td>');
        //         newRow.append('<td class="px-4 py-1 text-sm">' + stockin.item_code + '</td>');
        //         newRow.append('<td class="px-4 py-1 text-sm">' + stockin.quantity + '</td>');
        //         newRow.append('<td class="px-4 py-1 text-sm">' + stockin.selling_price + '</td>');
        //         newRow.append('<td class="px-4 py-1 text-sm">' + stockin.manufacture_date + '</td>');
        //         newRow.append('<td class="px-4 py-1 text-sm"> ' + stockin.expiry_date + ' </td>');
        //         newRow.append('<td class="px-4 py-1 text-sm"> ' + stockin.token_id + ' </td>');
        //         newRow.append('<td class="px-4 py-1 text-sm"> ' + stockin.Userlogin + ' </td>');
                
                
        //         let svgElement = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" >\
        //                 <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"\
        //                 clip-rule="evenodd" ></path> </svg>');
    
        //         newRow.append('<td class="px-4 py-1"> <div class="flex items-center space-x-4 text-sm">\
        //                 <button onclick="Delete_Stockin_History('+stockin.id +')"\
        //                 class="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-red-600 rounded-lg focus:outline-none focus:shadow-outline-gray"\
        //                 aria-label="Delete">' + svgElement[0].outerHTML  +'</button>  </div> </td></tr>');
                
        //             // Add more columns as needed
        //             $('#Stockin_History .new').append(newRow);
        //     });
        //     // Append the row to the table body
        // }
            
    
    // DELETE STOCKIN HISTORY
    function Delete_Stockin_History(id){
            ifconfirm = confirm('Do you want to delete this account?');
            if (ifconfirm){
                var Delete_Stockin_History = document.getElementById('Delete_Stockin_History').dataset.url;

                $.ajax({
                    type: 'GET',
                    url: Delete_Stockin_History,
                    data: {
                        id:id 
                    },
                    success: function(res){
                        myjaxfunct(res)
                    }
                });
            }
        }
        
        $(document).ready(function(){
            // SEARCH BY DATE RANGE
            $('#get_date_range').click(function() {
                let fromdate    =  $('#fromdate').val();
                let todate      =  $('#todate').val();
                var stockin_history = document.getElementById('stockin_history').dataset.url;

                $.ajax({
                    type: 'GET',
                    url: stockin_history,
                    data: {
                        fromdate: fromdate,   
                        todate: todate, 
                    },
                    success: function(res){
                        myjaxfunct(res)
                    }
                });
            });
    
            // SEARCH BY ITEM
            $('#searchItem').keyup(function() {
                let searchItem      =  $('#searchItem').val();
                var stockin_history = document.getElementById('stockin_history').dataset.url;
    
                $.ajax({
                    type: 'GET',
                    url: stockin_history,
                    data: {
                        searchItem: searchItem, 
                    },
                    success: function(res){
                        myjaxfunct(res)
                    }
                });
            });
    
            // SEARCH BY BARCODE
            // $('#scannerInput').on('input', function() {
            //         let searchItem      =  $('#scannerInput').val();
            //         var Scanned_code = document.getElementById('Scanned_code').dataset.url;
    
            //         $.ajax({
            //             type: 'GET',
            //             url: Scanned_code,
            //             data: {
            //                 searchItem: searchItem, 
            //             },
            //             success: function(data){
            //                 AddToCart(data.id, data.code, data.image, data.item, data.price);
    
            //             }
            //         });
            // });
        })
        
