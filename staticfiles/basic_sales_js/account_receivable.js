
    
    function get_account_recievable(id) {
        account_recievable_payment.showModal()
        set_element_value('#CustomerID', null);
        set_element_value('#Balance', null);
        var AccountReceivableURL2 = document.getElementById('AccountReceivableURL2').dataset.url;

        $.ajax({
            type: 'GET',
            url: AccountReceivableURL2,
            data: {
                id: id,
            },
            success: function(res){

                set_element_value('#CustomerID', res.cusID);
                set_element_value('#Balance', res.balance);
            }
        })
    }

    // GET OUTPUT FOR ACCOUNT RECEIVABLES
    function acct_receivable_output(res){
        
        let currency_symbol =  $('#currency_symbol').val();
        $('#acct_receivable .old').remove();
            $('#acct_receivable .new').empty();
            res.data.forEach(function(item, index) {
            let newRow = $('<tr id="' + item.id + '">');
            // Add data to the row
            newRow.append('<td class="px-4 py-1 text-sm">' + (index + 1) + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.customer_code + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.name + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + currency_symbol +''+item.Balance + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.phone + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm">' + item.address + '</td>');
            newRow.append('<td class="px-4 py-1 text-sm"><a class="items-left justify-left py-2 px-4 mb-12 mt-5 cursor-pointer font-bold font-semibold bg-[#fcd34d] text-white rounded-full">Owing</a></td>');
            newRow.append('<td class="px-4 py-1 text-sm"> <button type="button" onclick="account_recievable_payment.showModal(), get_account_recievable(\'' + item.customer_code + '\')" class="items-left justify-left py-2 px-2 mx-2 cursor-pointer text-[12px] font-semibold bg-[#86efac] text-dark rounded-md">Make Payment</button> </td>');
            
            
                // Add more columns as needed
            $('#acct_receivable .new').append(newRow);
        });
    }
    
    $(document).ready(function(){

        // GET ACCOUNT RECEIVABLE DATA WHEN CLICKED(FOR DATE)
        $('#search').keyup(function() {
            let search      =  $('#search').val();
            var AccountReceivableURL = document.getElementById('AccountReceivableURL').dataset.url;

            $.ajax({
                type: 'GET',
                url: AccountReceivableURL, 
                data: {
                    search: search,   
                },
                success: function(data){
                    acct_receivable_output(data)
                }
            });
        });
    });
