
function onclickme(id){
    // enabledloader()
    let subcategoriesList = $('#subcategoriesList')
    let catImgInfo = $('#cat_img_info')
    let category_name_info = $('#category_name_info')
    let desc = $('#desc')
    var ItemCategory = document.getElementById('ItemCategory').dataset.url;
    
    $.ajax({
        type: 'GET',
        url: ItemCategory,
        data: {
            categoryID: id,
        },
        success: function(res){
            disabledloader()
            subcategoriesList.empty();
            catImgInfo.empty();
            category_name_info.text(res.category.category_name)
            desc.text(res.category.description)
            // Add the new subcategories
            res.category.subcategories.forEach(sub => {
                anchorTag= `<a href="#" class="inline-flex items-center px-4 mt-5 py-2 text-sm font-medium text-center text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 ms-3">${sub.description}</a>`;
            });
            subcategoriesList.append(anchorTag);

            imgTag = `<img class="w-24 h-24 mb-3 rounded-full shadow-lg" src="${res.category.cat_img}" alt="${res.category.category_name} Image"/>`;
            catImgInfo.append(imgTag);

        }
    })

}

