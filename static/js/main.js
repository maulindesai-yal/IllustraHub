// Slideshow functionality
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    let currentSlide = 0;
    let slideInterval;

    function showSlide(index) {
        slides.forEach(slide => {
            slide.classList.remove('active');
            slide.style.opacity = '0';
            slide.style.transform = 'scale(1.1)';
        });
        
        slides[index].classList.add('active');
        slides[index].style.opacity = '1';
        slides[index].style.transform = 'scale(1)';
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    function startSlideshow() {
        showSlide(0);
        slideInterval = setInterval(nextSlide, 5000);
    }

    function stopSlideshow() {
        clearInterval(slideInterval);
    }

    // Start slideshow
    startSlideshow();

    // Pause slideshow on hover
    const slideshow = document.querySelector('.slideshow');
    slideshow.addEventListener('mouseenter', stopSlideshow);
    slideshow.addEventListener('mouseleave', startSlideshow);

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Animate elements on scroll with intersection observer
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.animate-text, .feature-card, .bidding-card, .testimonial-card').forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'all 0.6s ease-out';
        observer.observe(element);
    });

    // Add hover effect to bidding cards
    const biddingCards = document.querySelectorAll('.bidding-card');
    biddingCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // Add loading animation to buttons
    const buttons = document.querySelectorAll('.btn-cta');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!this.classList.contains('loading')) {
                e.preventDefault();
                this.classList.add('loading');
                
                // Simulate loading state
                setTimeout(() => {
                    this.classList.remove('loading');
                    // Navigate to the href after loading animation
                    const href = this.getAttribute('href');
                    if (href) {
                        window.location.href = href;
                    }
                }, 1000);
            }
        });
    });

    // Scroll progress indicator
    const scrollProgress = document.createElement('div');
    scrollProgress.className = 'scroll-progress';
    document.body.appendChild(scrollProgress);

    window.addEventListener('scroll', () => {
        const windowHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrolled = (window.scrollY / windowHeight) * 100;
        scrollProgress.style.transform = `scaleX(${scrolled / 100})`;
    });

    // Mobile menu functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const closeSidebar = document.getElementById('closeSidebar');

    function toggleSidebar() {
        sidebarOverlay.classList.toggle('active');
        document.body.style.overflow = sidebarOverlay.classList.contains('active') ? 'hidden' : '';
    }

    sidebarToggle.addEventListener('click', toggleSidebar);
    closeSidebar.addEventListener('click', toggleSidebar);
    sidebarOverlay.addEventListener('click', (e) => {
        if (e.target === sidebarOverlay) {
            toggleSidebar();
        }
    });

    // Close sidebar when clicking a link
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', () => {
            toggleSidebar();
        });
    });

    // Add parallax effect to hero section
    const heroSection = document.querySelector('.hero-section');
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        heroSection.style.backgroundPositionY = `${scrolled * 0.5}px`;
    });
});

// DOM Elements
const modal = document.querySelector('.modal');
const modalContent = document.querySelector('.modal-content');
const closeModal = document.querySelector('.close-modal');
const sidebarOverlay = document.querySelector('.sidebar-overlay');
const sidebarPopup = document.querySelector('.sidebar-popup');
const hamburger = document.querySelector('.hamburger');
const scrollProgress = document.querySelector('.scroll-progress');

// Utility Functions
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};

// Modal Functions
const openModal = (content) => {
    modalContent.innerHTML = content;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
};

const closeModalHandler = () => {
    modal.style.display = 'none';
    document.body.style.overflow = '';
};

// Sidebar Functions
const toggleSidebar = () => {
    sidebarOverlay.classList.toggle('active');
    sidebarPopup.classList.toggle('active');
};

const closeSidebar = () => {
    sidebarOverlay.classList.remove('active');
    sidebarPopup.classList.remove('active');
};

// Scroll Progress
const updateScrollProgress = () => {
    const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (window.scrollY / windowHeight) * 100;
    scrollProgress.style.transform = `scaleX(${scrolled / 100})`;
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Modal
    if (closeModal) {
        closeModal.addEventListener('click', closeModalHandler);
    }

    // Sidebar
    if (hamburger) {
        hamburger.addEventListener('click', toggleSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', (e) => {
            if (e.target === sidebarOverlay) {
                closeSidebar();
            }
        });
    }

    // Scroll Progress
    if (scrollProgress) {
        window.addEventListener('scroll', debounce(updateScrollProgress, 10));
    }

    // Form Validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Image Zoom
    const images = document.querySelectorAll('.zoomable');
    images.forEach(img => {
        img.addEventListener('click', () => {
            openModal(`<img src="${img.src}" alt="${img.alt}" style="max-width: 100%; max-height: 90vh;">`);
        });
    });

    // Bid Amount Validation
    const bidInput = document.querySelector('.bid-input');
    if (bidInput) {
        bidInput.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            const minBid = parseFloat(e.target.dataset.minBid);
            
            if (value < minBid) {
                e.target.classList.add('error');
            } else {
                e.target.classList.remove('error');
            }
        });
    }

    // Cart Functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const form = btn.closest('form');
            if (form) {
                try {
                    const response = await fetch(form.action, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });

                    if (response.ok) {
                        btn.classList.add('success');
                        setTimeout(() => {
                            btn.classList.remove('success');
                        }, 2000);
                        // Redirect to cart page or show success message
                        window.location.href = response.url;
                    } else {
                        throw new Error('Failed to add to cart');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    btn.classList.add('error');
                }
            }
        });
    });

    // Animation on Scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.animate, .animate-up');
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            
            if (elementTop < window.innerHeight && elementBottom > 0) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    window.addEventListener('scroll', debounce(animateOnScroll, 10));
    animateOnScroll();

    // Upload Form Functionality
    const uploadPopup = document.getElementById('uploadPopup');
    const openUploadBtn = document.getElementById('openUploadForm');
    const openUploadBtnEmpty = document.getElementById('openUploadFormEmpty');
    const closePopupBtn = document.getElementById('closePopup');
    const cancelUploadBtn = document.getElementById('cancelUpload');
    const uploadForm = document.querySelector('.upload-form');

    function openUploadForm() {
        uploadPopup.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeUploadForm() {
        uploadPopup.style.display = 'none';
        document.body.style.overflow = '';
    }

    if (openUploadBtn) {
        openUploadBtn.addEventListener('click', openUploadForm);
    }

    if (openUploadBtnEmpty) {
        openUploadBtnEmpty.addEventListener('click', openUploadForm);
    }

    if (closePopupBtn) {
        closePopupBtn.addEventListener('click', closeUploadForm);
    }

    if (cancelUploadBtn) {
        cancelUploadBtn.addEventListener('click', closeUploadForm);
    }

    // Close popup when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === uploadPopup) {
            closeUploadForm();
        }
    });

    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const requiredFields = uploadForm.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    }
});

// Export functions for use in other modules
export {
    openModal,
    closeModalHandler,
    toggleSidebar,
    closeSidebar,
    formatCurrency,
    debounce
}; 