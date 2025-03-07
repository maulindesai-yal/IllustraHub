document.addEventListener("DOMContentLoaded", function () {
    let slides = document.querySelectorAll(".slide");
    let currentIndex = 0;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove("active");
            if (i === index) {
                slide.classList.add("active");
            }
        });
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        showSlide(currentIndex);
    }

    document.querySelector(".next").addEventListener("click", nextSlide);
    document.querySelector(".prev").addEventListener("click", prevSlide);

    setInterval(nextSlide, 4000); // Auto-slide every 4 seconds
});

// Dynamic Header
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.background = 'var(--primary-dark)';
        header.style.boxShadow = '0 4px 20px rgba(15,23,42,0.2)';
    } else {
        header.style.background = 'var(--primary-dark)';
        header.style.boxShadow = '0 4px 20px rgba(15,23,42,0.15)';
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebarOverlay = document.getElementById("sidebarOverlay");
    const closeSidebar = document.getElementById("closeSidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebarOverlay.classList.add("active");
        document.querySelector(".sidebar-popup").classList.add("active");
    });

    closeSidebar.addEventListener("click", function () {
        sidebarOverlay.classList.remove("active");
        document.querySelector(".sidebar-popup").classList.remove("active");
    });

    // Close sidebar if clicked outside
    sidebarOverlay.addEventListener("click", function (event) {
        if (event.target === sidebarOverlay) {
            sidebarOverlay.classList.remove("active");
            document.querySelector(".sidebar-popup").classList.remove("active");
        }
    });
});

// Advanced Form Validation
document.querySelector('form').addEventListener('submit', function(e) {
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error-message').forEach(el => {
        el.style.display = 'none';
        el.parentElement.classList.remove('has-error');
    });

    // Required fields
    document.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            showError(field.id, 'This field is required');
        }
    });

    // Price validation
    const priceInput = document.getElementById('price');
    if (priceInput.value && (priceInput.value < 50 || isNaN(priceInput.value))) {
        isValid = false;
        showError('price', 'Minimum price is $50');
    }

    if (!isValid) e.preventDefault();
});

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorElement = field.parentNode.querySelector('.error-message');
    field.parentNode.classList.add('has-error');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

// Auto-slider
let currentSlide = 0;
const slides = document.querySelectorAll('.slider img');

function nextSlide() {
    slides[currentSlide].classList.remove('active');
    currentSlide = (currentSlide + 1) % slides.length;
    slides[currentSlide].classList.add('active');
}

if (slides.length > 0) {
    slides[0].classList.add('active');
    setInterval(nextSlide, 5000);
}


document.getElementById("openUploadForm").addEventListener("click", function() {
    document.getElementById("uploadPopup").style.display = "block";
});
document.getElementById("closePopup").addEventListener("click", function() {
    document.getElementById("uploadPopup").style.display = "none";
});