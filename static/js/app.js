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