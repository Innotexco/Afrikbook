
//XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -->

    // DEVELOPER: LILY
    // PHONE: 08124767155 
    // DATE: OCT 2023 
    function generateID(){
        return Math.random().toString(10).substr(2, 3);
    }

    function advoidDuplicatedTr(allOptionValues) {
        
        // *************************************************************************************
                let count = 0;
                for (let i = 0; i < allOptionValues.length; i++) {
                    if (allOptionValues[i] === '_ _Choose an Option_ _') {
                        count++;
                        if (count > 1) {
                            // Find the index of the current <tr> element to remove
                            const trIndexToRemove = i;
                            // Remove the corresponding <tr> element
                            $('#stock_row_add tr:eq(' + trIndexToRemove + ')').remove();
                        }
                    }
                }
        // *************************************************************************************

    }



    function isItemDuplicated(array, item) {
        // Count occurrences of the item in the array
        let count = 0;
        // Iterate through the array
        for (let i = 0; i < array.length; i++) {
            if (array[i] === item) {
                count++;
                // If the item appears more than once, return true
                if (count > 1) {
                    return true;
                }
            }
        }
        // If the loop completes without finding duplicates, return false
        return false;
        }


    function disabledbutton(){
        $('#allowed').addClass('bg-[#f7fee7] cursor-not-allowed');
        $('#allowed').removeClass('bg-[#B2BEB5]');
        $("#allowed").attr('disabled', true);
    }
    function enabledbutton(){
        $("#allowed").removeAttr('disabled');
        $('#allowed').removeClass('bg-[#f7fee7] cursor-not-allowed');
        $('#allowed').addClass('bg-[#B2BEB5]');
    }
    function enabledloader(){
        $('#hiddenN').addClass('loadercontainer');
        $('#loader').addClass('loader');
        $('#loading').text('Loading...');
    }
    function disabledloader(){
        $('#hiddenN').removeClass('loadercontainer');
        $('#loader').removeClass('loader');
        $('#loading').text('');
    }
    function clonedtTableRow(e, selectedOption){
        // *************************************************************************************
            closeTR =  $(e).closest('tr')
            const inputField = closeTR.find('#desc');
            const inputField2 = closeTR.find('.qtty');
            const inputField3 = closeTR.find('#item');
            const inputField4 = closeTR.find('#price');
            const inputField5 = closeTR.find('#wholesale_price');
            inputField2.data("button-name");
            
            // cloning each row in the next line
            const newRow = $('#stock_row_add tr:first').clone();
            // making the cloned input empty
            newRow.find('input').val('');

            // adding the cloned to the table by ID
            $('#stock_row_add').append(newRow);

            // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                // creating a random ID for delete btn
                const uniqueId =  generateID();

                // adding a class for the same table #stock_row_ad, using the generated ID
                newRow.addClass('fordelete' + uniqueId);
            
                // creating an id for the delete btn using the generated ID 
                newRow.find('.stock_remove_W_W').attr('id', 'delete_' + uniqueId);
            // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                // giving attr to class for code refrence
                newRow.find('.qtty').attr('id', 'label_' + uniqueId);
                newRow.find('.your_label_class').attr('for', 'label_' + uniqueId);



            // Find the second-to-last row in #stock_row_add
            const secondToLastRow = $('#stock_row_add tr:last').prev();
            const LastRow = $('#stock_row_add tr:last')

            // Find the label within the second-to-last row with a specific data-forerrors attribute
            const lastLabel = secondToLastRow.find('label[data-forerrors]');
            const lastLabel2 = LastRow.find('label[data-forerrors]');

            // Assign a value to the data-forerrors attribute of the found label
            // if(!selectedOption.includes('_ _') ){
                lastLabel.attr("data-forerrors", selectedOption);
                lastLabel2.attr("data-forerrors", '');
            
            // }


          
        // *************************************************************************************


        // ******************************AJAX******************************************************
        var stokinURL = document.getElementById('stokinURL').dataset.url;

            $.ajax({
                type:'GET',
                url:stokinURL,
                data: {
                    data: selectedOption,
                },
                success: function(response){
                    inputField.val(response.des);
                    inputField2.val(1);
                    inputField3.val(response.item);
                    inputField4.val(response.price);
                    inputField5.val(response.wholesale_price);
                    inputField2.data("button-name", response.code);
                    disabledloader()
                    const allOptionValues = $('.select-dropdown').map(function() {
                        return $(this).val();
                    }).get();

                },
                error: function() {
                    // Handle errors
                },
            })
        // ***********************************END AJAX**************************************************


    }

    function avoidDuplicatedRow(selectedOption){
        // *************************************************************************************
            // map through the select option
            const allOptionValues = $('.select-dropdown').map(function() {
                return $(this).val();
            }).get();


            if (isItemDuplicated(allOptionValues, selectedOption)) {
                toastr.options = {
                    closeButton: true,
                    positionClass: 'toast-top-right',
                    progressBar: true,
                };
                toastr.error("already selected", "Error");
                    const secondToLastIndex = $('#stock_row_add tr').length - 2;
                $('#stock_row_add tr:eq(' + secondToLastIndex + ')').remove();
            } 
            advoidDuplicatedTr(allOptionValues)
        // *************************************************************************************

    }


  


    $(document).on('change', '#select', function(){
         enabledbutton()
        
        const selectedOption = $(this).val();
     // *************************************************************************************
        // function for cloned row
        clonedtTableRow(this, selectedOption)
     // *************************************************************************************
     // *************************************************************************************
        // map through the select option
        avoidDuplicatedRow(selectedOption)
     // *************************************************************************************

    });


    $(document).on('click', '.stock_remove_W_W', function(){
        var button_id = $(this).attr("id");
        var row_id = button_id.replace('delete_', '');
        $('.fordelete'+row_id).remove();
        // check for other auth
            var errortag = $('.your_label_class').text()
            if(errortag == ''){
                enabledbutton()
            }
    });




    function onkeyboard(e){
        VAL = $(e).val()
        var inputId = $(e).attr('id');
        labelFor =  $('label[for="' + inputId + '"]')
        // for qty auth
        let buttonName = $(e).data("button-name");
        let buttonoutlet = $(e).data("button-outlet");
        let from = $('#from').val();
        // console.log(buttonName, from)

        if(VAL == ''){
            $(e).addClass('error-border');
            labelFor.text('Invalid input');
            disabledbutton()

        }
        else{
            $(e).removeClass('error-border');
            labelFor.text('');
            enabledbutton()
        }
     
    }


 

   // DELETE SALES HISTORY
   function SalesData(expandSearch, res){
    
        // console.log(expandSearch, 'expandSearchexpandSearchexpandSearchexpandSearch')
        if(expandSearch == null){
            $('#Saleslist .new').empty();
        }

        let cusID  = $('#cusID').val()
        let currency_symbol  = $('#currency_symbol').val()
        $('#Saleslist .old').remove();

        res.data.forEach(function(sale, index) {
            // get_ID = sale.cusID ? cusID == 'cusID' : sale.invoiceID
            get_ID = (cusID === 'cusID') ? sale.cusID : sale.invoiceID;
            // let newTable = $('<tbody class="bg-white divide-y new"> </tbody>');
            let newRow = $('<tr class="text-gray-700 dark:text-gray-400" id="' + sale.id + '">');
            // Add data to the row
            newRow.append('<td class="px-4  text-sm">' + (index + 1) + '</td>');
            newRow.append('<td class="px-4  text-sm">' + sale.customer_name + '</td>');
            newRow.append('<td class="px-4  text-sm">' + sale.item_name + '</td>');
            newRow.append('<td class="px-4  text-sm">' + currency_symbol +''+ sale.unit_p + '</td>');
            newRow.append('<td class="px-4  text-sm">' + sale.qty + '</td>');
            newRow.append('<td class="px-4  text-sm">' + currency_symbol +''+ sale.amount + '</td>');
            newRow.append('<td class="px-4  text-sm"> ' + sale.payment_method + ' </td>');
            var SalesHistoryURL = document.getElementById('SalesHistoryURL').dataset.url;
            
            let editUrl = SalesHistoryURL.replace('0', get_ID);

            // let svgElement = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" >\
            //         <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"\
            //         clip-rule="evenodd" ></path> </svg>');


            newRow.append('<td class="text-[11px]"> <a  href="'+ editUrl +'" class="flex items-center justify-center text-blue-500 border px-3"\
                        aria-label="View">View</a></td>');
            
            // newRow.append('<td class="px-4 "> <div class="flex items-center space-x-4 text-sm"> <button onclick="Delete_Sales_History('+ sale.id +')"\
            //         class="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-red-600 rounded-lg focus:outline-none focus:shadow-outline-gray"\
            //         aria-label="Delete">' + svgElement[0].outerHTML  +'</button> </div>  </td></tr>');

                      
                // Add more columns as needed
            $('#Saleslist .new').append(newRow);
                
           
        });
        if(expandSearch != null){
            sum = ('<tr class="text-gray-700 dark:text-gray-400">\
            <td class="px-4  text-sm">Sales Total Money: '+ currency_symbol +'<span class="text-gray-700"></span>\</td>\
            <td class="px-4  text-sm"></td>\
            <td class="px-4  text-sm"></td>\
            <td class="px-4  text-sm"></td>\
            <td class="px-4  text-sm"></td>\
            <td class="px-4  text-sm"></td>\
            <td class="px-4  text-sm"></td>\
            <td class="px-4  text-sm"></td>\
            <td class="px-4  text-sm">\
                <input \
                    type="text"\
                    class="totalqty1 block w-[100px] px-2 text-[15px] border-2 rounded-md focus:border-slate-300 focus:outline-none focus:shadow-outline-green text-slate-600 form-input"\
                    placeholder=""\
                    value="'+ res.total_sum +'"\
                    readonly\
                    id="totalqty1"\
                />\
            </td> </tr>');

            $('#Saleslist .new').append(sum);
            // $('#SalesTotalMoney').addClass('hidden')
            let total = 0;
            $('.totalqty1').each(function(){
                value = parseFloat($(this).val());
                total += value;
            });
           $('#totalqty').val(total)
        }else{
            // $('#SalesTotalMoney').removeClass('hidden')
            
            $('#totalqty').val(res.total_sum)
        }
        
    }
    
   
    // STOCK-IN HISTORY SEARCH
    $(document).ready(function(){

        

        // GET SALES DATA WHILE SEARCHING
        $('#searchby').keyup(function() {
            let searchItem   =  $('#searchby').val();
            let from_CSH      =  $('#from_CSH').val();
            var SalesURL = document.getElementById('SalesURL').dataset.url;

            $.ajax({
                type: 'GET',
                url: SalesURL,
                data: {
                    searchItem: searchItem, 
                    from_CSH: from_CSH, 
                },
                success: function(data){
                    expandSearch = null
                    
                    SalesData(expandSearch, data)
                }
            });
        
        });

        // GET SALES DATA WHEN CLICKED (FOR DATE)
        $('#search_by_date').on('click',function() {
            let fromdate    =  $('#fromdate').val();
            let todate      =  $('#todate').val();
            let from_CSH      =  $('#from_CSH').val();
            var SalesURL = document.getElementById('SalesURL').dataset.url;

            $.ajax({
                type: 'GET',
                url: SalesURL,
                data: {
                    fromdate: fromdate,   
                    todate: todate, 
                    from_CSH: from_CSH, 
                },
                success: function(data){
                    expandSearch = null
                    const expand_history = document.getElementById('Expand_history');
                    // expand_history.addEventListener('change', function() {
                        
                        // Check if the checkbox is checked

                        if(expand_history.checked){
                            // alert('true')
                            expandSearch = true
                        }else{
                            // alert('null')

                            expandSearch = null
                        }
                        SalesData(expandSearch, data)
                    // });
                    
                }
            });
        });

    });
    // DELETE SALES HISTORY
function Delete_Sales_History(id){
    ifconfirm = confirm('Do you want to delete this account?');
    if (ifconfirm){
        var DeleteSalesURL = document.getElementById('DeleteSalesURL').dataset.url;

        $.ajax({
            type: 'GET',
            url: DeleteSalesURL,
            data: {
                id:id 
            },
            success: function(res){
                SalesData(expandSearch, res)
            }
        });
    }
};
    




    function get_element_value(key){
        const keyval = $(key).val();
        return keyval;
    }
    function set_element_text(key, text_value){
        const keyval =$(key).text(text_value);
        return keyval;
    }
    function set_element_value(key, value){
        const keyval =$(key).val(value);
        return keyval;
    }

    // GENERATE ID
    function generateID2() {
        // Define characters for the random part of the ID
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var randomChars = '';
        // Generate a random string of 6 characters
        for (var i = 0; i < 6; i++) {
            randomChars += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        // Combine the constant part "CUS_" with the random characters
        var id =  randomChars;
        return id;
    }
    // CONFIRM CHECK-OUT ITEM



// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -->
