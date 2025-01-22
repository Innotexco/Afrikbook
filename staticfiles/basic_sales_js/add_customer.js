    
    function Delete_Customer_Acct(res){
    
        $('#CustomerList .old').remove();
        $('#CustomerList .new').empty();
        res.data.forEach(function(customer, index) {
            let newRow = $('<tr class="text-gray-700 dark:text-gray-400" id="' + customer.id + '">');
            // Add data to the row
            newRow.append('<td class="px-4 py-1 text-sm">' + (index + 1) + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + customer.name + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + customer.phone + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + customer.email + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + customer.address + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + customer.company_name + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm"> ' + customer.id + ' </td>');
            newRow.append('<td class="px-4 py-1 text-sm"> ' + customer.category + ' </td>');
            var edit_customer = document.getElementById('edit_customer').dataset.url;
            
            let editUrl = edit_customer.replace('0', customer.id);

            let svgElement = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" >\
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path> </svg>');
            

            let svgElement2 = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" >\
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"\
                    clip-rule="evenodd"></path> </svg>');

            newRow.append('<td class="text-[11px]"> <div class="flex items-center justify-between"><a  href="'+ editUrl +'"> ' + svgElement[0].outerHTML  +'</a> <button onclick="Delete_acct_onclick('+customer.id +')" class="flex items-center justify-center text-red-600"\
                                        aria-label="Delete" id="Delete_Customer_Acct" >' + svgElement2[0].outerHTML  +'</button>  </div> </td></tr>');
            
                // Add more columns as needed
                $('#CustomerList .new').append(newRow);
        });
        // Append the row to the table body
    }
    
    // STOCK-IN HISTORY SEARCH
    function Delete_acct_onclick(id){
        var deleteCusAccount = document.getElementById('deleteCusAccount').dataset.url;

        ifconfirm = confirm('Do you want to delete this account?');
        if (ifconfirm){
            $.ajax({
                type: 'GET',
                url: deleteCusAccount,
                data: {
                    id:id 
                },
                success: function(res){
                    Delete_Customer_Acct(res)
                }
            });
        }
    };