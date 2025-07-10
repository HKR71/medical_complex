// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Animation on scroll with debouncing
    let scrollTimeout;
    function animateOnScroll() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        elements.forEach(element => {
            const position = element.getBoundingClientRect();
            if (position.top < window.innerHeight - 100 && !element.classList.contains('animate__animated')) {
                element.classList.add('animate__animated', 'animate__fadeInUp');
            }
        });
    }

    // Initial check
    animateOnScroll();

    // Efficient scroll handling
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(animateOnScroll, 100);
    });

    // Form input animations
    document.querySelectorAll('.form-control').forEach(input => {
        // Initialize focused state for pre-filled fields
        if (input.value) input.parentElement.classList.add('focused');

        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            if (!this.value) this.parentElement.classList.remove('focused');
        });
    });

    // Doctor selection in booking form
    const doctorSelect = document.querySelector('select[name="doctor"]');
    if (doctorSelect) {
        doctorSelect.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            const doctorDisplay = document.querySelector('.doctor-selection');
            if (selectedOption && doctorDisplay) {
                doctorDisplay.textContent = selectedOption.textContent;
            }
        });
    }

    // Appointment date validation (timezone-safe)
    const dateInput = document.querySelector('input[name="date"]');
    if (dateInput) {
        dateInput.addEventListener('change', function () {
            const selectedDate = new Date(this.value);
            const today = new Date();

            // Normalize dates to local time
            const selectedDateLocal = new Date(
                selectedDate.getFullYear(),
                selectedDate.getMonth(),
                selectedDate.getDate()
            );

            const todayLocal = new Date(
                today.getFullYear(),
                today.getMonth(),
                today.getDate()
            );

            if (selectedDateLocal < todayLocal) {
                alert('Please select a future date');
                this.value = '';
            }
        });
    }

    // Initialize count-up statistics
    const counters = document.querySelectorAll('.counter');

    counters.forEach(counter => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                const target = +counter.getAttribute('data-target');
                const duration = 2000; // 2 seconds
                const startTime = performance.now();

                const updateCount = (timestamp) => {
                    const elapsed = timestamp - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const current = Math.floor(progress * target);

                    counter.textContent = current.toLocaleString();

                    if (progress < 1) {
                        requestAnimationFrame(updateCount);
                    } else {
                        counter.textContent = target.toLocaleString();
                    }
                };

                requestAnimationFrame(updateCount);
                observer.disconnect();
            }
        }, { threshold: 0.5 });

        observer.observe(counter);
    });
});