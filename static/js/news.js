// ==========================================================
// STOCKVISION PRO - LIVE NEWS
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {

    loadNews("all");

    setupCategoryButtons();

    // Refresh live news every 5 minutes
    setInterval(function () {

        const activeButton =
            document.querySelector(
                ".sv-news-category.active"
            );

        const category =
            activeButton
                ? activeButton.getAttribute("data-category")
                : "all";

        loadNews(category);

    }, 5 * 60 * 1000);

});


// ==========================================================
// CATEGORY BUTTONS
// ==========================================================

function setupCategoryButtons() {

    const buttons =
        document.querySelectorAll(
            ".sv-news-category"
        );

    buttons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                buttons.forEach(
                    function (btn) {

                        btn.classList.remove(
                            "active"
                        );

                    }
                );

                button.classList.add(
                    "active"
                );

                const category =
                    button.getAttribute(
                        "data-category"
                    );

                loadNews(category);

            }
        );

    });

}


// ==========================================================
// LOAD LIVE NEWS
// ==========================================================

async function loadNews(category = "all") {

    try {

        const response = await fetch(
            `/api/news?category=${encodeURIComponent(category)}`,
            {
                cache: "no-store"
            }
        );

        const data =
            await response.json();

        if (!data.success) {

            console.error(
                "News API error:",
                data.message
            );

            return;
        }

        renderNews(data.news);

    }

    catch (error) {

        console.error(
            "LIVE NEWS ERROR:",
            error
        );

    }

}


// ==========================================================
// RENDER NEWS
// ==========================================================

function renderNews(news) {

    const stories =
        document.querySelectorAll(
            ".sv-side-story"
        );

    news.slice(0, 4).forEach(
        function (article, index) {

            if (!stories[index]) {
                return;
            }

            const story =
                stories[index];

            const title =
                story.querySelector("h3");

            const description =
                story.querySelector("p");

            const category =
                story.querySelector(
                    ".sv-news-meta span"
                );

            const time =
                story.querySelector(
                    ".sv-news-meta small"
                );

            const link =
                story.querySelector(
                    ".sv-story-bottom span"
                );

            if (title) {

                title.textContent =
                    article.title;

            }

            if (description) {

                description.textContent =
                    cleanText(
                        article.summary ||
                        "Latest financial market news and updates."
                    );

            }

            if (category) {

                category.textContent =
                    article.category;

            }

            if (time) {

                time.textContent =
                    article.published ||
                    "Latest";

            }

            if (link) {

                link.textContent =
                    "Read story";

            }

            story.style.display = "";

            story.onclick =
                function () {

                    if (
                        article.link &&
                        article.link !== "#"
                    ) {

                        window.open(
                            article.link,
                            "_blank"
                        );

                    }

                };

        }
    );

}


// ==========================================================
// CLEAN HTML
// ==========================================================

function cleanText(text) {

    const temp =
        document.createElement(
            "div"
        );

    temp.innerHTML = text;

    return (
        temp.textContent ||
        temp.innerText ||
        ""
    );

}