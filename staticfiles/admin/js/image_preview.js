// This will handle showing image preview after selecting a file
document.addEventListener("DOMContentLoaded", function () {
    // Image preview logic for main image
    const imageInput = document.querySelector("#id_image");
    const imagePreview = document.querySelector("#image-preview");

    if (imageInput) {
        imageInput.addEventListener("change", function (event) {
            const [file] = imageInput.files;
            if (file) {
                imagePreview.src = URL.createObjectURL(file);
                imagePreview.style.display = "block"; // Show the preview
            } else {
                imagePreview.style.display = "none"; // Hide the preview if no file is selected
            }
        });
    }

    // Image preview logic for hover image
    const hoverImageInput = document.querySelector("#id_hover_img");
    const hoverImagePreview = document.querySelector("#hover-image-preview");

    if (hoverImageInput) {
        hoverImageInput.addEventListener("change", function (event) {
            const [file] = hoverImageInput.files;
            if (file) {
                hoverImagePreview.src = URL.createObjectURL(file);
                hoverImagePreview.style.display = "block"; // Show the preview
            } else {
                hoverImagePreview.style.display = "none"; // Hide the preview if no file is selected
            }
        });
    }
});
