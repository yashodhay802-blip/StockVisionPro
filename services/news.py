import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime


# ==========================================================
# LIVE NEWS RSS SOURCES
# ==========================================================

NEWS_FEEDS = {
    "markets": [
        "https://news.google.com/rss/search?q=stock+market+finance+when:1d&hl=en-US&gl=US&ceid=US:en"
    ],

    "stocks": [
        "https://news.google.com/rss/search?q=stocks+shares+Wall+Street+when:1d&hl=en-US&gl=US&ceid=US:en"
    ],

    "technology": [
        "https://news.google.com/rss/search?q=technology+AI+stocks+when:1d&hl=en-US&gl=US&ceid=US:en"
    ],

    "investing": [
        "https://news.google.com/rss/search?q=investing+finance+when:1d&hl=en-US&gl=US&ceid=US:en"
    ],

    "economy": [
        "https://news.google.com/rss/search?q=economy+inflation+interest+rates+when:1d&hl=en-US&gl=US&ceid=US:en"
    ]
}


# ==========================================================
# GET PUBLISHED DATETIME
# ==========================================================

def get_published_datetime(entry):

    try:

        published = entry.get("published")

        if published:

            return parsedate_to_datetime(
                published
            )

    except Exception:
        pass

    return None


# ==========================================================
# FORMAT TIME
# ==========================================================

def format_time(entry):

    try:

        dt = get_published_datetime(entry)

        if dt:

            now = datetime.now(dt.tzinfo)

            minutes = int(
                (now - dt).total_seconds() / 60
            )

            if minutes < 1:
                return "Just now"

            if minutes < 60:
                return f"{minutes} min ago"

            hours = minutes // 60

            if hours < 24:
                return f"{hours} hr ago"

            days = hours // 24

            if days == 1:
                return "Yesterday"

            return f"{days} days ago"

    except Exception:
        pass

    return "Latest"


# ==========================================================
# CLEAN TITLE
# ==========================================================

def clean_title(title):

    if not title:
        return "Latest Market News"

    return title.strip()


# ==========================================================
# GET SOURCE NAME
# ==========================================================

def get_source(entry):

    try:

        if hasattr(entry, "source"):

            source = entry.source

            if isinstance(source, dict):

                return source.get(
                    "title",
                    "News Source"
                )

    except Exception:
        pass

    return "News Source"


# ==========================================================
# FETCH ONE CATEGORY
# ==========================================================

def fetch_category(category):

    articles = []

    feeds = NEWS_FEEDS.get(
        category,
        []
    )

    for feed_url in feeds:

        try:

            feed = feedparser.parse(
                feed_url
            )

            for entry in feed.entries:

                title = clean_title(
                    entry.get(
                        "title",
                        ""
                    )
                )

                link = entry.get(
                    "link",
                    "#"
                )

                summary = entry.get(
                    "summary",
                    ""
                )

                published_dt = (
                    get_published_datetime(
                        entry
                    )
                )

                articles.append({

                    "title": title,

                    "link": link,

                    "summary": summary,

                    "category": category.upper(),

                    "source": get_source(
                        entry
                    ),

                    "published": format_time(
                        entry
                    ),

                    "published_timestamp":
                        published_dt.timestamp()
                        if published_dt
                        else 0

                })

        except Exception as error:

            print(
                f"{category} feed error: {error}"
            )

    return articles


# ==========================================================
# GET LIVE NEWS
# ==========================================================

def get_live_news(
    category="all",
    limit=10
):

    # ------------------------------------------------------
    # SINGLE CATEGORY
    # ------------------------------------------------------

    if category != "all":

        articles = fetch_category(
            category
        )

        articles.sort(
            key=lambda x:
                x.get(
                    "published_timestamp",
                    0
                ),
            reverse=True
        )

        return articles[:limit]


    # ------------------------------------------------------
    # ALL CATEGORIES
    # ------------------------------------------------------

    category_names = [
        "markets",
        "stocks",
        "technology",
        "investing",
        "economy"
    ]

    category_articles = {}

    for name in category_names:

        category_articles[name] = (
            fetch_category(name)
        )

        category_articles[name].sort(
            key=lambda x:
                x.get(
                    "published_timestamp",
                    0
                ),
            reverse=True
        )


    # ------------------------------------------------------
    # REMOVE DUPLICATES
    # ------------------------------------------------------

    for name in category_names:

        unique = []

        seen = set()

        for article in category_articles[name]:

            key = article["title"].lower()

            if key not in seen:

                seen.add(key)

                unique.append(article)

        category_articles[name] = unique


    # ------------------------------------------------------
    # MIX CATEGORIES
    # ------------------------------------------------------

    mixed = []

    max_items = max(
        len(category_articles[name])
        for name in category_names
    )

    for index in range(max_items):

        for name in category_names:

            items = category_articles[name]

            if index < len(items):

                mixed.append(
                    items[index]
                )


    # ------------------------------------------------------
    # SORT BY ACTUAL PUBLISHED TIME
    # ------------------------------------------------------

    mixed.sort(
        key=lambda x:
            x.get(
                "published_timestamp",
                0
            ),
        reverse=True
    )


    # ------------------------------------------------------
    # FINAL UNIQUE LIST
    # ------------------------------------------------------

    final_articles = []

    seen_titles = set()

    for article in mixed:

        key = article["title"].lower()

        if key not in seen_titles:

            seen_titles.add(key)

            final_articles.append(
                article
            )

        if len(final_articles) >= limit:

            break


    return final_articles
