$(document).ready(function() {

    // SIDEBAR
    const body = document.querySelector("body"),
    sidebar = body.querySelector(".sidebar",)
    toggle = body.querySelector(".toggle",)

    toggle.addEventListener("click", () => {
        
        sidebar.classList.toggle("close");
    });




    const menu_btn = document.querySelector("button.menu-button");
    const dropdown_menu = document.querySelector(".open-menu");
    
    if (menu_btn != null){

        menu_btn.addEventListener("click", () => {
            alert("kkkk")
            dropdown_menu.classList.toggle("hidden");
        });
    
        menu_btn.addEventListener("click", () => {
            window.classList.toggle("hidden");
        });
    }



    // UPDATE ITEM 

    // Handle form submission with AJAX === ADD ITEM TAGS 
    $('#AddItemSize').on('click', function (e) {
        e.preventDefault();

        $item_code = $('#item_code').val();
        $size = $('#size').val();

        if($item_code == "" || $size == " "){
            alert("Please complete the required fields");
        }
        else{
            $.ajax({
                url: '../../../add_item_size/',
                type: "POST",
                data: {
                    item_code: $item_code,
                    size: $size,
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function () {
                    Read();
                    $('#item_code').val('');
                    $('#size').val('');
                    alert("New Size Was Successfully Added")
                }
            });
        }
    });


    // Handle form submission with AJAX === ADD ITEM SIZE 
    $('#AddItemSize').on('click', function (e) {
        e.preventDefault();

        $item_code = $('#item_code').val();
        $size = $('#size').val();

        if($item_code == "" || $size == " "){
            alert("Please complete the required fields");
        }
        else{
            $.ajax({
                url: '../../../add_item_size/',
                type: "POST",
                data: {
                    item_code: $item_code,
                    size: $size,
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function () {
                    Read();
                    $('#item_code').val('');
                    $('#size').val('');
                    alert("New Size Was Successfully Added")
                }
            });
        }
    });




});