
        
    function generateRandomNumber(e) {

        if(e.isTrusted){
            e.preventDefault();
            const min = 1; // Minimum value for the random number
            const max = 100000000000000; // Maximum value for the random number
            const randomNumber = Math.floor(Math.random() * (max - min + 1)) + min;
    
            document.getElementById('randomNumber').value = randomNumber;
            // generatebarcode()
        }else {
            document.getElementById('randomNumber').value;
        }
        
    }
    $(document).ready(function() {
        $('#submitItem').click(function() {
            // Manually trigger the form submission
            $('#itemForm').submit();
        });
    });
    $('#generateButton').click(function() {

        // function generatebarcode(){
            const barcode = $("#randomNumber").val();
            // return barcode;
        // }
        // Generate a barcode with the value "123456789" and append it to the #barcodeContainer
        JsBarcode("#barcodeContainer", barcode);
    });



    $(document).ready(function() {
        // When the select option changes
        $('#mySelect').on('change', function() {
            // Get the selected value
            var selectedOption = $(this).val();
            var additem = document.getElementById('additem').dataset.url;

            // Send the selected value to the server using AJAX
            $.ajax({
                type: 'GET',  // Change to 'GET' if you're retrieving data
                url:additem,  // Replace with your server endpoint URL
                data: {
                    data: selectedOption
                },
                success: function(response) {
                    var resultDiv = $("#result");
                    resultDiv.empty();
                    var data = response.data;
                    response.data.forEach(function(item, index) {
                        selectOpt = '<option value="'+ item.description +'">' + item.description + '</option>';
                    resultDiv.append(selectOpt);
                    });
                },
                error: function() {
                    // Handle errors
                }
            });
        });
    });


    function Delete_Item(id){
        confirmval = confirm("Do you want to delete this item?")
        var Delete_Item = document.getElementById('Delete_Item').dataset.url;

        if(confirmval){ 
            $.ajax({
                type:'POST',
                url: Delete_Item,
                data:{
                    id:id,
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                
                success: (function(res){
                    let currency_symbol =  $('#currency_symbol').val();
                    $('#itemTable .old').remove();
                        $('#itemTable .new').empty();
                        res.data.forEach(function(item, index) {
                        let newRow = $('<tr id="' + item.id + '">');
                        var update_item = document.getElementById('update_item').dataset.url;
                        var view_item = document.getElementById('View_item').dataset.url;

                        let editUrl = update_item.replace('0', item.id);
                        let View_item = view_item.replace('0', item.id);
                        image = item.image ? '<img src="'+ item.image +'" alt="'+ item.item_name +' Image" class="h-8 w-8 rounded-md">' : '<p>No image available</p>'
                        // Add data to the row
                        newRow.append('<td class="px-4 py-1 text-sm">' + (index + 1) + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm"> <a href="'+ View_item +'" class="text-blue-500 font-semibold text-sm"> '+ item.item_name + '</a></td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.generated_code + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.category + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.sub_category + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + currency_symbol +''+item.selling_price + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + currency_symbol +''+item.wholesale_price + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' +  image + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + currency_symbol +''+ item.discount_price + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.discount_percentage + '</td>');

                        
                        let svgElement = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor"\
                                    viewBox="0 0 20 20"  > <path  d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"\
                                    ></path> </svg>');

                        let svgElement2 = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor"\
                                    viewBox="0 0 20 20" > <path fill-rule="evenodd"\
                                    d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"\
                                    clip-rule="evenodd" ></path> </svg>');

                        newRow.append('<td class="px-4 py-1 text-sm"><a href="'+ editUrl +'"\
                                class="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-blue-500 rounded-lg focus:outline-none focus:shadow-outline-gray"\
                                aria-label="Edit" > '+ svgElement[0].outerHTML +'</a></td>');

                        newRow.append('<td class="px-4 py-1 text-sm"> <a onclick="Delete_Item('+ item.id +')"\
                                class="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-red-600 rounded-lg focus:outline-none focus:shadow-outline-gray"\
                                aria-label="Delete" >'+ svgElement2[0].outerHTML +' </a></td>');
                        
                            // Add more columns as needed
                        $('#itemTable .new').append(newRow);
                    });
                }),
            })
         }
       
    }


    

