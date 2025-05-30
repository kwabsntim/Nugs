
document.getElementById("hamburger").addEventListener("click", function() {
    this.classList.toggle("active");
});
function animateCounter(id, finalNumber, speed) {
    let count = 0;
    const counterElement = document.getElementById(id);
    const increment = Math.ceil(finalNumber / 100);
    
    function updateCounter() {
        if (count < finalNumber) {
            count += increment;
            if (count > finalNumber) count = finalNumber;
            counterElement.textContent = count;
            setTimeout(updateCounter, speed);
        }
    }
    updateCounter();
}

function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}
function revealCards() {
    const cards = document.querySelectorAll('.testimonial-card');
    const triggerBottom = window.innerHeight * 0.85;

    cards.forEach(card => {
        const cardTop = card.getBoundingClientRect().top;
        if (cardTop < triggerBottom) {
            card.classList.add('visible');
        }
    });
}

window.addEventListener('scroll', revealCards);
window.addEventListener('load', revealCards);

let selectedCourse = "";

function selectCourse(course) {
    selectedCourse = course;
    document.getElementById("popupTitle").innerText = `Select Level for ${course}`;
    // Show the popup by changing its display style
    document.getElementById("levelPopup").style.display = "flex";
}

function closePopup() {
    // Hide the popup
    document.getElementById("levelPopup").style.display = "none";
}

function goToLevel(level) {
    const courseEncoded = encodeURIComponent(selectedCourse);
    // Navigate to the selected course and level
    window.location.href = `/files/${courseEncoded}/${level}`;
}
