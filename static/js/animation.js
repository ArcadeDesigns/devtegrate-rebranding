gsap.fromTo(".startUp", {
            opacity: 1
        }, {
            opacity: 0,
            duration: 0.5,
            delay: 8
        });

        gsap.fromTo(".logoTitleContent", {
            y: 50,
            opacity: 0
        }, {
            y: 0,
            opacity: 1,
            duration: 2,
            delay: 1
        });