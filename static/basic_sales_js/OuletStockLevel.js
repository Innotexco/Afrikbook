

function getStocklevel(url){
    let fromdate    =  $('#fromdate').val();
    let todate    =  $('#todate').val();
    let Itemcode    =  $('#Itemcode').val();
    let searchItem    =  $('#searchItem').val();     
    let store  =  $('#store').val();       
    $.ajax({
        type: 'GET',
        url: url,
        data: {
            Itemcode: Itemcode,
            searchItem: searchItem,   
            fromdate: fromdate,   
            todate: todate, 
            // onchange
            store: store,
        },
        success: function(res){
            $('#storestocklevel .default').remove();
            $('#storestocklevel .result').empty();
            $('#totalqty').empty();
            res.data.forEach(function(item, index) {
                let newRow = $('<tr id="campareTR'+ item.id + '">');
                // Add data to the row
                newRow.append('<td class="text-[10px]">' + (index + 1) + '</td>');
                newRow.append('<td class="text-[10px]">' + item.datetx + '</td>');
                newRow.append('<td class="text-[10px]">' + item.items + '</td>');
                newRow.append('<td class="text-[10px]">' + item.items + '</td>');
                newRow.append('<td class="text-[10px]">' + item.qty + '</td>');
                newRow.append('<td class="text-[10px]">' + item.itemcode + '</td>');
                newRow.append('<td class="text-[10px]"> ' + item.store + ' </td>');
                newRow.append('<td class="text-[10px]"> ' + item.low_stock_level + ' </td>');
                newRow.append('<td class="text-[10px]"> ' + item.wholesale_price + ' </td>');
                newRow.append('<td class="text-[10px]"> ' + item.wholesale_price + ' </td>');
                newRow.append('<td class="text-[10px]"> ' + item.selling_price + ' </td>');
                newRow.append('<td class="text-[10px]"> ' + item.selling_price + ' </td>');
                    // Add more columns as needed
                    $('#storestocklevel .result').append(newRow);
            });
            // Append the row to the table body
            let newtotal = $('#totalqty')
            newtotal.val(res.totalqty );
        }
    })
}

var OutletStockLevel = document.getElementById('OutletStockLevel').dataset.url;

$(document).on('click', '.Search', function(){
    getStocklevel(OutletStockLevel)
}); 

$(document).on('change', '.commonClass', function(){
    getStocklevel(OutletStockLevel)
}) 