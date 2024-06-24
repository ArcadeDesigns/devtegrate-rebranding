function ResponsiveMenuNavigation() {
    const menuToggle = document.querySelector(".responsive-navbar-header .menu");
    const responsiveMenu = document.querySelector(".responsive-menu");
    const closeMenuToggle = document.querySelector(".responsive-menu .menu");
    const dropDowns = document.querySelectorAll(".responsive-drop-down");

    // Toggle responsive menu
    menuToggle.addEventListener("click", function() {
        responsiveMenu.style.display = "flex";
    });

    closeMenuToggle.addEventListener("click", function() {
        responsiveMenu.style.display = "none";
    });

    // Toggle dropdown menus
    dropDowns.forEach(dropDown => {
        dropDown.addEventListener("click", function() {
            const responsiveList = this.querySelector(".responsive-list");
            responsiveList.classList.toggle("active");
        });
    });
};
