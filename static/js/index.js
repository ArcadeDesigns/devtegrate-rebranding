function ResponsiveMenuNavigation() {
    const menuToggle = document.querySelector(".responsive-navbar-header .menu");
    const responsiveMenu = document.querySelector(".responsive-menu");
    const closeMenuToggle = document.querySelector(".responsive-menu .menu");
    const dropDowns = document.querySelectorAll(".responsive-drop-down");

    // Toggle responsive menu
    menuToggle.addEventListener("click", function() {
        responsiveMenu.classList.add("active")
    });

    closeMenuToggle.addEventListener("click", function() {
        responsiveMenu.classList.remove("active")
    });

    // Toggle dropdown menus
    dropDowns.forEach(dropDown => {
        dropDown.addEventListener("click", function() {
            const responsiveList = this.querySelector(".responsive-list");
            responsiveList.classList.toggle("active");
        });
    });
};

function AutomatedSlider() {
    const images = document.querySelectorAll('.slider-img');
    const contents = document.querySelectorAll('.header-content-container');
    const nextPageBtn = document.querySelector('.header-nav span:first-child');

    let currentIndex = 0;

    const slideToNext = () => {
        images[currentIndex].classList.remove('active');
        contents[currentIndex].classList.remove('active');

        currentIndex = (currentIndex + 1) % images.length;

        images[currentIndex].classList.add('active');
        contents[currentIndex].classList.add('active');
    };

    nextPageBtn.addEventListener('click', slideToNext);

    setInterval(slideToNext, 10000);
};
