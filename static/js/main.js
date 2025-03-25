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