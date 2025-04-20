// Utility Functions
const utils = {
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${message}
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    formatCurrency(amount) {
        return `$${parseFloat(amount).toFixed(2)}`;
    }
};

// Image Zoom Functionality
const imageZoom = {
    init() {
        const modal = document.getElementById("zoomModal");
        if (!modal) return;

        const modalImg = document.getElementById("zoomedImage");
        const closeBtn = document.getElementsByClassName("close-modal")[0];

        if (closeBtn) {
            closeBtn.onclick = () => modal.style.display = "none";
        }

        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        };
    },

    toggleZoom(imageUrl) {
        const modal = document.getElementById("zoomModal");
        const modalImg = document.getElementById("zoomedImage");
        if (modal && modalImg) {
            modal.style.display = "flex";
            modalImg.src = imageUrl;
        }
    }
};

// Bidding Timer
const biddingTimer = {
    init(endTime) {
        if (!endTime) return;
        
        function update() {
            const now = new Date().getTime();
            const distance = endTime - now;
            
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            const timerElement = document.getElementById("bidding-timer");
            if (!timerElement) return;
            
            if (distance < 0) {
                timerElement.innerHTML = "Auction Ended";
                timerElement.classList.add("ended");
                this.handleAuctionEnd();
                return;
            }
            
            let timeString = '';
            if (days > 0) timeString += `${days}d `;
            timeString += `${hours}h ${minutes}m ${seconds}s`;
            
            timerElement.textContent = timeString;
            
            if (distance < 3600000) { // less than 1 hour
                timerElement.classList.add("ending-soon");
            }
        }
        
        update();
        setInterval(update, 1000);
    },

    handleAuctionEnd() {
        const bidForm = document.getElementById("bid-form");
        if (bidForm) {
            bidForm.remove();
            const endedMessage = document.createElement('div');
            endedMessage.className = 'auction-ended-message';
            endedMessage.innerHTML = '<i class="fas fa-gavel"></i> This auction has ended';
            bidForm.parentNode.appendChild(endedMessage);
        }
    }
};

// Bidding System
const biddingSystem = {
    init(illustrationId, minBid) {
        if (!illustrationId) return;

        const socket = new WebSocket(`ws://${window.location.host}/ws/bid/${illustrationId}/`);
        const bidForm = document.getElementById("bid-form");
        
        if (!bidForm) return;

        this.setupWebSocket(socket);
        this.setupBidForm(bidForm, minBid);
    },

    setupWebSocket(socket) {
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateBidDisplay(data);
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed");
            setTimeout(() => window.location.reload(), 3000);
        };
    },

    updateBidDisplay(data) {
        const highestBidSpan = document.getElementById("highest-bid");
        const bidCountSpan = document.getElementById("bid-count");
        const highestBidderSpan = document.getElementById("highest-bidder");
        const bidHistory = document.getElementById("bid-history");
        const bidAmount = document.getElementById("bid-amount");

        if (highestBidSpan) highestBidSpan.textContent = utils.formatCurrency(data.bid_amount);
        if (bidCountSpan) bidCountSpan.textContent = data.bid_count;
        if (highestBidderSpan && data.bidder_name) highestBidderSpan.textContent = data.bidder_name;

        // Update minimum bid input
        if (bidAmount) {
            const newMinBid = parseFloat(data.bid_amount) + 1;
            bidAmount.min = newMinBid;
            const minBidNote = document.querySelector('.min-bid-note');
            if (minBidNote) minBidNote.textContent = `Minimum bid: ${utils.formatCurrency(newMinBid)}`;
        }

        // Add animation for new bids
        if (bidHistory) {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.style.opacity = '0';
            historyItem.style.transform = 'translateY(-20px)';
            historyItem.innerHTML = `
                <div class="bid-info">
                    <div class="bidder-info">
                        <img src="${data.bidder_image || '/static/images/default-avatar.png'}" alt="${data.bidder_name}">
                        <span class="bidder-name">${data.bidder_name}</span>
                    </div>
                    <span class="bid-amount">${utils.formatCurrency(data.bid_amount)}</span>
                </div>
                <span class="bid-time">just now</span>
            `;
            
            bidHistory.insertBefore(historyItem, bidHistory.firstChild);
            
            // Trigger animation
            setTimeout(() => {
                historyItem.style.transition = 'all 0.3s ease';
                historyItem.style.opacity = '1';
                historyItem.style.transform = 'translateY(0)';
            }, 10);

            // Remove no-bids message if it exists
            const noBids = bidHistory.querySelector('.no-bids');
            if (noBids) {
                noBids.style.opacity = '0';
                setTimeout(() => noBids.remove(), 300);
            }
        }
    },

    setupBidForm(bidForm, minBid) {
        const submitButton = bidForm.querySelector('button[type="submit"]');
        const errorDiv = document.getElementById('bid-error');
        const bidAmount = document.getElementById('bid-amount');

        function validateBidAmount(value) {
            const numValue = parseFloat(value);
            if (isNaN(numValue)) {
                return {
                    valid: false,
                    message: 'Please enter a valid number'
                };
            }
            if (numValue < minBid) {
                return {
                    valid: false,
                    message: `Bid must be at least ${utils.formatCurrency(minBid)}`
                };
            }
            return { valid: true, message: '' };
        }

        // Handle input validation
        bidAmount.addEventListener('input', function() {
            const validation = validateBidAmount(this.value);
            if (!validation.valid) {
                errorDiv.textContent = validation.message;
                errorDiv.style.display = 'block';
                submitButton.disabled = true;
                this.classList.add('invalid');
            } else {
                errorDiv.style.display = 'none';
                submitButton.disabled = false;
                this.classList.remove('invalid');
            }
        });

        // Handle form submission
        bidForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            const bidValue = bidAmount.value;
            const validation = validateBidAmount(bidValue);
            
            if (!validation.valid) {
                errorDiv.textContent = validation.message;
                errorDiv.style.display = 'block';
                return;
            }

            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            errorDiv.style.display = 'none';

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        bid_amount: parseFloat(bidValue)
                    })
                });

                const data = await response.json();
                
                if (response.ok && data.success) {
                    utils.showNotification('Bid placed successfully!', 'success');
                    biddingSystem.updateBidDisplay(data);
                    
                    // Clear form and reset validation
                    bidAmount.value = '';
                    bidAmount.classList.remove('invalid');
                } else {
                    throw new Error(data.error || 'Failed to place bid');
                }
            } catch (error) {
                console.error('Bid submission error:', error);
                errorDiv.textContent = error.message || 'An error occurred while placing your bid. Please try again.';
                errorDiv.style.display = 'block';
                utils.showNotification(error.message || 'Failed to place bid', 'error');
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-gavel"></i> Place Bid';
            }
        });

        // Add bid increment buttons
        const incrementButtons = document.createElement('div');
        incrementButtons.className = 'bid-increment-buttons';
        incrementButtons.innerHTML = `
            <button type="button" class="increment-btn" data-increment="1">+$1</button>
            <button type="button" class="increment-btn" data-increment="5">+$5</button>
            <button type="button" class="increment-btn" data-increment="10">+$10</button>
        `;
        bidAmount.parentNode.appendChild(incrementButtons);

        incrementButtons.addEventListener('click', (e) => {
            if (e.target.classList.contains('increment-btn')) {
                const increment = parseFloat(e.target.dataset.increment);
                const currentValue = parseFloat(bidAmount.value) || minBid;
                bidAmount.value = (currentValue + increment).toFixed(2);
                bidAmount.dispatchEvent(new Event('input'));
            }
        });
    }
};

// Portfolio Filter
const portfolioFilter = {
    init() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const portfolioItems = document.querySelectorAll('.portfolio-item');

        if (!filterButtons.length || !portfolioItems.length) return;

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                const filterValue = button.getAttribute('data-filter');

                portfolioItems.forEach(item => {
                    if (filterValue === 'all' || item.getAttribute('data-category') === filterValue) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
};

// Start Bidding Configuration
const startBiddingConfig = {
    init() {
        const durationInput = document.getElementById('duration');
        const reservePriceInput = document.getElementById('reserve_price');
        const form = document.querySelector('.config-form');

        if (durationInput) {
            durationInput.addEventListener('change', this.updateEndTime);
        }

        if (reservePriceInput) {
            reservePriceInput.addEventListener('input', this.updateReserveSummary);
        }

        if (form) {
            form.addEventListener('submit', this.validateForm);
        }

        // Initialize
        this.updateEndTime();
        this.updateReserveSummary();
    },

    updateEndTime() {
        const duration = document.getElementById('duration').value;
        const now = new Date();
        const endTime = new Date(now.getTime() + duration * 60 * 60 * 1000);
        
        const endTimeElement = document.getElementById('end-time');
        const endTimeSummary = document.getElementById('end-time-summary');
        const durationSummary = document.getElementById('duration-summary');

        if (endTimeElement) endTimeElement.textContent = endTime.toLocaleString();
        if (endTimeSummary) endTimeSummary.textContent = endTime.toLocaleString();
        if (durationSummary) durationSummary.textContent = duration + ' Hours';
    },

    updateReserveSummary() {
        const reservePrice = document.getElementById('reserve_price').value;
        const reserveSummary = document.getElementById('reserve-summary');
        if (reserveSummary) {
            reserveSummary.textContent = reservePrice ? utils.formatCurrency(reservePrice) : 'Not Set';
        }
    },

    validateForm(e) {
        const reservePrice = document.getElementById('reserve_price').value;
        const startingPrice = parseFloat(document.querySelector('.info-item .value').textContent.replace('$', ''));
        
        if (reservePrice && parseFloat(reservePrice) < startingPrice) {
            e.preventDefault();
            alert('Reserve price cannot be lower than the starting price');
        }
    }
};

// Initialize Select2 for country dropdown
const initSelect2 = () => {
    if (typeof $ !== 'undefined' && $('select[name="country"]').length) {
        $('select[name="country"]').select2({
            placeholder: "Select a country",
            allowClear: true
        });
    }
};

// Bid History Filter
const bidHistoryFilter = {
    init() {
        const filterButtons = document.querySelectorAll('.history-filters .filter-btn');
        if (!filterButtons.length) return;

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Filter bid history
                this.filterBids(button.dataset.filter);
            });
        });
    },

    filterBids(filterType) {
        const historyList = document.getElementById('bid-history');
        const historyItems = historyList.querySelectorAll('.history-item');
        const noBidsMessage = historyList.querySelector('.no-bids');

        if (!historyItems.length) return;

        let sortedItems = Array.from(historyItems);

        switch (filterType) {
            case 'recent':
                // Items are already in recent order
                break;
            case 'top':
                sortedItems.sort((a, b) => {
                    const amountA = parseFloat(a.querySelector('.bid-amount').textContent.replace('$', ''));
                    const amountB = parseFloat(b.querySelector('.bid-amount').textContent.replace('$', ''));
                    return amountB - amountA;
                });
                break;
        }

        // Clear and re-append items
        historyItems.forEach(item => item.remove());
        if (noBidsMessage) noBidsMessage.remove();

        if (sortedItems.length === 0) {
            const noBids = document.createElement('div');
            noBids.className = 'no-bids';
            noBids.innerHTML = `
                <i class="fas fa-info-circle"></i>
                <p>No bids found for this filter.</p>
            `;
            historyList.appendChild(noBids);
        } else {
            sortedItems.forEach(item => historyList.appendChild(item));
        }
    }
};

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize image zoom
    imageZoom.init();

    // Initialize bidding timer if end time is available
    const endTimeElement = document.getElementById('bidding-timer');
    if (endTimeElement) {
        const endTime = new Date(endTimeElement.dataset.endTime).getTime();
        biddingTimer.init(endTime);
    }

    // Initialize bidding system if illustration ID is available
    const illustrationId = document.querySelector('[data-illustration-id]')?.dataset.illustrationId;
    const minBid = parseFloat(document.querySelector('[data-min-bid]')?.dataset.minBid);
    if (illustrationId && minBid) {
        biddingSystem.init(illustrationId, minBid);
    }

    // Initialize portfolio filter
    portfolioFilter.init();

    // Initialize start bidding configuration
    startBiddingConfig.init();

    // Initialize Select2
    initSelect2();

    // Initialize bid history filter
    bidHistoryFilter.init();

    // Add animation to elements
    const elements = document.querySelectorAll('.illustration-details-container > div');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'all 0.5s ease-out';
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 200);
    });

    // Add smooth scroll for bid history
    const bidHistory = document.getElementById('bid-history');
    if (bidHistory) {
        bidHistory.addEventListener('scroll', () => {
            if (bidHistory.scrollTop > 0) {
                bidHistory.classList.add('scrolled');
            } else {
                bidHistory.classList.remove('scrolled');
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll(".slideshow img");
    let currentIndex = 0;

    function showNextImage() {
        images[currentIndex].style.opacity = "0";
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].style.opacity = "1";
    }

    setInterval(showNextImage, 3000); // Change every 3 seconds
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

document.getElementById("openUploadForm").addEventListener("click", function() {
    document.getElementById("uploadPopup").style.display = "block";
});
document.getElementById("closePopup").addEventListener("click", function() {
    document.getElementById("uploadPopup").style.display = "none";
});