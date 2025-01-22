

    // CHECK IF SESSION ITEM EXISTS
    function CheckIfItemExist(Itemlist, generated_code){
        const entry = Itemlist.find(([CART]) => CART === generated_code);
        if(entry){
            return true;
        }
    }
    //  ADD TO CART FROM VIEW ITEM PAGE
    function AddToCart(id, generated_code, image, item_name, selling_price){
        
        const FormalItem = sessionStorage.getItem('Items');
        let list;

        if(FormalItem === null){
            list = [];
        }else{
            list = JSON.parse(FormalItem);
        }

        if(!CheckIfItemExist(list, generated_code)){

            let AddedItems = [generated_code, image, item_name, selling_price, 1]

            list.push(AddedItems);

            sessionStorage.setItem('Items', JSON.stringify(list));
        }else {
            // Find the index of the existing item in the cart
            const existingItemIndex = list.findIndex(item => item[0] === generated_code);

            // Increment the quantity of the existing item
            //list[existingItemIndex][4] += 1;

            list[existingItemIndex][4] = Number(list[existingItemIndex][4]) + 1 || 1;
            sessionStorage.setItem('Items', JSON.stringify(list));
        }
    }
