// (function($) {
//     $(document).ready(function() {
//         var categoryField = $('select#id_category'); // Category dropdown
//         var subcategoryField = $('select#id_subcategory'); // Subcategory dropdown

//         // Update subcategory options when category is selected
//         categoryField.change(function() {
//             var categoryId = $(this).val(); // Get selected category ID
//             if (categoryId) {
//                 $.ajax({
//                     url: '/get-subcategories/', // The endpoint we will create next
//                     data: {
//                         'category_id': categoryId,
//                     },
//                     success: function(data) {
//                         subcategoryField.empty(); // Clear the subcategory dropdown
//                         $.each(data.subcategories, function(index, subcategory) {
//                             subcategoryField.append('<option value="' + subcategory.id + '">' + subcategory.title + '</option>');
//                         });
//                     }
//                 });
//             } else {
//                 subcategoryField.empty(); // Clear the subcategory dropdown if no category is selected
//             }
//         });

//         // Trigger change on page load to load existing data
//         categoryField.change();
//     });
// })(django.jQuery);
console.log("loaded sub category filtering js!")
    // document.addEventListener('DOMContentLoaded', function() {
var categoryField = document.querySelector('select#id_category'); // Category dropdown
var subcategoryField = document.querySelector('select#id_subcategory'); // Subcategory dropdown
console.log(categoryField);
// Ensure the categoryField element is selected
console.log("Category Field Element: ", categoryField);

// Function to update subcategory options when category is selected
function updateSubcategories() {
    var categoryId = categoryField.value; // Get selected category ID
    console.log("Selected Category ID: ", categoryId); // Log the selected category ID

    if (categoryId) {
        // Fetch subcategories using POST request
        fetch('/get-subcategories/', {
                method: 'POST', // Using POST request
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(), // Ensure CSRF token is sent
                },
                body: JSON.stringify({
                    'category_id': categoryId // Send the selected category ID
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Clear the subcategory dropdown
                subcategoryField.innerHTML = '';
                console.log("Fetched Subcategories Data: ", data); // Log the data returned by the server

                if (data.subcategories) {
                    // Populate the subcategory dropdown with the returned data
                    data.subcategories.forEach(function(subcategory) {
                        var option = document.createElement('option');
                        option.value = subcategory.id;
                        option.textContent = subcategory.title;
                        subcategoryField.appendChild(option);
                    });
                } else {
                    console.error('No subcategories found or invalid response');
                }
            })
            .catch(error => {
                console.error('Error fetching subcategories:', error);
            });
    } else {
        // Clear the subcategory dropdown if no category is selected
        subcategoryField.innerHTML = '';
    }
}

// Add event listener for the category dropdown change event
categoryField.addEventListener('change', function() {
    console.log("Category changed, updating subcategories...");
    updateSubcategories();
});

// Trigger change event on page load to load existing data (if a category is pre-selected)
if (categoryField.value) {
    updateSubcategories();
}
// });

// Function to get CSRF token from Django's cookies (necessary for POST requests)
function getCSRFToken() {
    let cookieValue = null;
    let name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    console.log("CSRF Token: ", cookieValue); // Log CSRF token for verification
    return cookieValue;
}