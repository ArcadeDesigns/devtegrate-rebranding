function SwiperSliderDef() {
    const swiperWrapper = document.querySelector('.swiper-wrapper');
    const slides = document.querySelectorAll('.ctn-section-two-cn-ctn-box');
    const nextButton = document.querySelector('.next');
    const prevButton = document.querySelector('.prev');

    let currentIndex = 0;

    function updateSlidePosition() {
        swiperWrapper.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    nextButton.addEventListener('click', () => {
        if (currentIndex < slides.length - 1) {
            currentIndex++;
            updateSlidePosition();
        }
    });

    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateSlidePosition();
        }
    });
};

function SwiperSliderDefTwo() {
    const SwiperWrapperTwo = document.querySelector('.additional-swiper-wrapper');
    const slideTwos = document.querySelectorAll('.additional-ctn-section-two-cn-ctn-box');
    const nextButtonTwo = document.querySelector('.additional-next');
    const prevButtonTwo = document.querySelector('.additional-prev');

    let currentIndex = 0;

    function updateslideTwoPosition() {
        SwiperWrapperTwo.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    nextButtonTwo.addEventListener('click', () => {
        if (currentIndex < slideTwos.length - 1) {
            currentIndex++;
            updateslideTwoPosition();
        }
    });

    prevButtonTwo.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateslideTwoPosition();
        }
    });
};

function toggleOtherIndustry() {
    var industry = document.getElementById("industry").value;
    var otherIndustry = document.getElementById("other-industry");
    if (industry === "Other") {
        otherIndustry.style.display = "block";
    } else {
        otherIndustry.style.display = "none";
    }
}

function toggleOtherHelp() {
    var helpWith = document.getElementById("help-with").value;
    var otherHelp = document.getElementById("other-help");
    if (helpWith === "Other") {
        otherHelp.style.display = "block";
    } else {
        otherHelp.style.display = "none";
    }
}

function redirectToCloudService() {
    if (document.getElementById('cloud-checkbox').checked) {
        window.location.href = "/cloud-services";
    }
}

function ApplicationDropDown() {
    const advanceDropDowns = document.querySelectorAll('.advanceDropDown');

    advanceDropDowns.forEach(advanceDropDown => {
        const select = advanceDropDown.querySelector('.select');
        const caret = advanceDropDown.querySelector('.caret');
        const menu = advanceDropDown.querySelector('.advanceDropDwonmenu');
        const options = advanceDropDown.querySelectorAll('.menuScroll li');
        const input = select.querySelector('input');

        select.addEventListener('click', () => {
            select.classList.toggle('select-clicked');
            caret.classList.toggle('caret-rotate');
            menu.classList.toggle('menu-open');
        });

        options.forEach(option => {
            option.addEventListener('click', () => {
                input.value = option.innerText;
                select.classList.remove('select-clicked');
                caret.classList.remove('caret-rotate');
                menu.classList.remove('menu-open');
                options.forEach(option => {
                    option.classList.remove('active');
                });
                option.classList.add('active');
            });
        });
    });
}
