window.addEventListener("load", () => {

    const loader =
        document.getElementById("pageLoader");

    if (loader) {

        setTimeout(() => {

            loader.classList.add("hide");

        }, 700);

    }

});


/* =====================================================
   SMOOTH CARD ANIMATION
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const cards =
            document.querySelectorAll(
                ".dash-card, .stat-card, .feature-card"
            );

        cards.forEach((card, index) => {

            card.style.opacity = "0";

            card.style.transform =
                "translateY(20px)";

            setTimeout(() => {

                card.style.transition =
                    "0.6s ease";

                card.style.opacity =
                    "1";

                card.style.transform =
                    "translateY(0)";

            }, index * 80);

        });

    }
);