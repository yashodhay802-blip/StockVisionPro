from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import yfinance as yf

from services.market_data import (
    get_market_data,
    get_top_gainers,
    get_top_losers,
    get_chart_data,
    STOCKS
)

from services.prediction import predict_stock
from services.news import get_live_news
app = Flask(__name__)

app.secret_key = "stockvision-pro-2026-secret"


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template("home.html")


# ==================================================
# LOGIN
# ==================================================

@app.route("/login")
def login():

    return render_template("login.html")


@app.route("/register")
def register():

    return render_template("register.html")


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")


@app.route("/prediction")
def prediction():
    return render_template("prediction.html")


@app.route("/api/prediction")
def prediction_api():

    symbol = request.args.get(
        "symbol",
        "AAPL"
    ).upper().strip()

    try:

        horizon = int(
            request.args.get(
                "horizon",
                1
            )
        )

    except ValueError:

        horizon = 1

    # Allowed prediction periods
    if horizon not in [1, 7, 21]:
        horizon = 1

    try:

        result = predict_stock(
            symbol,
            horizon
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
# ==================================================
# CHARTS
# ==================================================

@app.route("/charts")
def charts():

    return render_template(
        "charts.html",
        stocks=STOCKS
    )


# ==================================================
# NEWS
# ==================================================

@app.route("/news")
def news():

    return render_template("news.html")

# ==================================================
# LIVE NEWS API
# ==================================================

@app.route("/api/news")
def news_api():

    category = request.args.get(
        "category",
        "all"
    ).lower().strip()

    try:

        news = get_live_news(
            category=category,
            limit=10
        )

        return jsonify({

            "success": True,

            "news": news

        })

    except Exception as error:

        print(
            f"News API error: {error}"
        )

        return jsonify({

            "success": False,

            "message": str(error),

            "news": []

        }), 500
# ==================================================
# WATCHLIST
# ==================================================

@app.route("/watchlist")
def watchlist():

    watchlist_symbols = session.get(
        "watchlist",
        []
    )

    market_data = get_market_data()

    watchlist_data = [

        stock

        for stock in market_data

        if stock["symbol"] in watchlist_symbols

    ]

    return render_template(

        "watchlist.html",

        watchlist=watchlist_data

    )


@app.route("/watchlist/add/<symbol>")
def add_watchlist(symbol):

    watchlist_symbols = session.get(
        "watchlist",
        []
    )

    symbol = symbol.upper()

    if symbol not in watchlist_symbols:

        watchlist_symbols.append(symbol)

    session["watchlist"] = watchlist_symbols

    return redirect(

        request.referrer

        or url_for("dashboard")

    )


@app.route("/watchlist/remove/<symbol>")
def remove_watchlist(symbol):

    watchlist_symbols = session.get(
        "watchlist",
        []
    )

    symbol = symbol.upper()

    if symbol in watchlist_symbols:

        watchlist_symbols.remove(symbol)

    session["watchlist"] = watchlist_symbols

    return redirect(

        url_for("watchlist")

    )


# ==================================================
# PORTFOLIO
# ==================================================

@app.route("/portfolio")
def portfolio():

    portfolio_data = session.get(
        "portfolio",
        []
    )

    total_value = 0

    for item in portfolio_data:

        try:

            total_value += (

                float(item["quantity"])

                * float(item["price"])

            )

        except Exception:

            pass

    return render_template(

        "portfolio.html",

        portfolio=portfolio_data,

        total_value=total_value

    )


# ==================================================
# PAPER TRADING
# ==================================================

@app.route("/paper-trading")
def paper_trading():

    cash = session.get(
        "cash",
        100000
    )

    portfolio = session.get(
        "portfolio",
        []
    )

    return render_template(

        "paper_trading.html",

        stocks=STOCKS,

        cash=cash,

        portfolio=portfolio

    )


# ==================================================
# BUY STOCK
# ==================================================

@app.route(
    "/paper-trading/buy",
    methods=["POST"]
)
def buy_stock():

    symbol = request.form.get(
        "symbol",
        ""
    ).upper()

    try:

        quantity = int(

            request.form.get(
                "quantity",
                0
            )

        )

        price = float(

            request.form.get(
                "price",
                0
            )

        )

    except ValueError:

        return redirect(

            url_for(
                "paper_trading"
            )

        )


    if quantity <= 0 or price <= 0:

        return redirect(

            url_for(
                "paper_trading"
            )

        )


    total_cost = quantity * price


    cash = session.get(
        "cash",
        100000
    )


    if total_cost > cash:

        return redirect(

            url_for(
                "paper_trading"
            )

        )


    portfolio = session.get(
        "portfolio",
        []
    )


    transactions = session.get(
        "transactions",
        []
    )


    cash -= total_cost


    found = False


    for item in portfolio:

        if item["symbol"] == symbol:

            item["quantity"] += quantity

            item["price"] = price

            found = True

            break


    if not found:

        portfolio.append({

            "symbol": symbol,

            "quantity": quantity,

            "price": price

        })


    transactions.append({

        "type": "BUY",

        "symbol": symbol,

        "quantity": quantity,

        "price": price,

        "total": total_cost

    })


    session["cash"] = cash

    session["portfolio"] = portfolio

    session["transactions"] = transactions


    return redirect(

        url_for(
            "paper_trading"
        )

    )


# ==================================================
# TRANSACTIONS
# ==================================================

@app.route("/transactions")
def transactions():

    transaction_data = session.get(
        "transactions",
        []
    )

    return render_template(

        "transactions.html",

        transactions=transaction_data

    )


# ==================================================
# API - STOCK DATA
# ==================================================

@app.route("/api/stocks")
def stocks_api():

    data = get_market_data()


    gainers = get_top_gainers(
        data
    )


    losers = get_top_losers(
        data
    )


    return jsonify({

        "stocks": data,


        "top_gainer":

            gainers[0]

            if gainers

            else None,


        "top_loser":

            losers[0]

            if losers

            else None

    })


# ==================================================
# API - CHART DATA
# ==================================================

@app.route("/api/chart-data")
def chart_data():

    symbol = request.args.get(
        "symbol",
        "AAPL"
    )


    period = request.args.get(
        "period",
        "1mo"
    )


    data = get_chart_data(

        symbol,

        period

    )


    return jsonify({

        "symbol": symbol,

        "period": period,

        "data": data

    })


# ==================================================
# API - LIVE S&P 500 MARKET PERFORMANCE
# ==================================================

@app.route("/api/market-performance")
def market_performance():

    try:

        data = yf.download(

            "^GSPC",

            period="1mo",

            interval="1d",

            progress=False,

            auto_adjust=False,

            multi_level_index=False

        )


        if data is None or data.empty:

            return jsonify({

                "dates": [],

                "prices": [],

                "error": "No market data available"

            }), 503


        # Handle MultiIndex returned by some yfinance versions

        if (

            hasattr(
                data.columns,
                "nlevels"
            )

            and data.columns.nlevels > 1

        ):

            data.columns = (

                data.columns

                .get_level_values(0)

            )


        if "Close" not in data.columns:

            return jsonify({

                "dates": [],

                "prices": [],

                "error": "Close price data not available"

            }), 503


        close_prices = (

            data["Close"]

            .dropna()

        )


        # If Close is returned as DataFrame

        if hasattr(

            close_prices,

            "columns"

        ):

            close_prices = (

                close_prices

                .iloc[:, 0]

            )


        dates = []

        prices = []


        for index, value in close_prices.items():

            dates.append(

                index.strftime(
                    "%d %b"
                )

            )


            prices.append(

                round(
                    float(value),
                    2
                )

            )


        return jsonify({

            "dates": dates,

            "prices": prices,

            "symbol": "S&P 500",

            "status": "success"

        })


    except Exception as error:


        print(

            "MARKET PERFORMANCE ERROR:",

            str(error)

        )


        return jsonify({

            "dates": [],

            "prices": [],

            "error": str(error)

        }), 500


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )