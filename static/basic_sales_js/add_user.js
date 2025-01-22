    // EDIT USER
    function edit_user(id){
        var edit_user = document.getElementById('edit_user').dataset.url;

        $.ajax({
            type: 'GET',
            url: edit_user,
            data: {
                id:id,
            },
            success: function(res){
                set_element_value('#usernameUpD', res.username)
                set_element_value('#emailUpD', res.email)
                set_element_value('#UpdateId', res.update)
                set_element_value('#id', id)
                set_element_value('#password', res.password)
                
            }
        });
    }
    // DELETE USER
    function Delete_user(id){
        confirmdelete = confirm('Delete User Account?')
        var delete_user = document.getElementById('delete_user').dataset.url;

        if(confirmdelete){
            $.ajax({
                type: 'GET',
                url: delete_user,
                data: {
                    id:id,
                },
                success: function(res){
                    $('#USER .old').remove();
                    $('#USER .new').empty();
                    res.data.forEach(function(item, index) {
                        let newRow = $('<tr id="' + item.id + '">');
                        // Add data to the row
                        newRow.append('<td class="px-4 py-1 text-sm">' + (index + 1) + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.date_joined + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.username + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.email + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.last_login + '</td>');
                        newRow.append('<td class="px-4 py-1 text-sm">' + item.Token_ID + '</td>');

                        // Add more columns as needed
                        let svgElement = $('<svg class="w-5 h-5" ria-hidden="true"\
                                        fill="currentColor" viewBox="0 0 20 20">\
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" ></path> </svg>');

                        let svgElement2 = $('<svg class="w-5 h-5" aria-hidden="true" fill="currentColor"\
                                            viewBox="0 0 20 20"> <path fill-rule="evenodd"\
                                            d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"\
                                            clip-rule="evenodd" ></path> </svg>');

                        newRow.append('<td class="px-4 py-1"> <div class="flex items-center space-x-4 text-sm">\
                                        <a onclick="edit_user(' + item.id + ')" class="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-blue-500 rounded-lg focus:outline-none focus:shadow-outline-gray"\
                                        aria-label="Edit" id="EditUser" > '+ svgElement[0].outerHTML +'</a> ');


                        newRow.append('<button onclick="Delete_user(' + item.id + ')" class="flex items-center justify-between px-2 py-2 text-sm font-medium leading-5 text-red-600 rounded-lg focus:outline-none focus:shadow-outline-gray"\
                                    aria-label="Delete">'+ svgElement2[0].outerHTML +'   </button> </div> </td>');
                        
                            // Add more columns as needed
                            $('#USER .new').append(newRow);
                    });
                    // Append the row to the table body
                        
                    
                }
            });
        }
    }
