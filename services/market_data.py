import yfinance as yf


STOCKS = {

    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NVDA": "NVIDIA",

    "META": "Meta Platforms",
    "NFLX": "Netflix",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel",

    "IBM": "IBM",
    "ORCL": "Oracle",
    "CRM": "Salesforce",
    "ADBE": "Adobe",

    "QCOM": "Qualcomm",
    "CSCO": "Cisco",

    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",

    "V": "Visa",
    "MA": "Mastercard",

    "WMT": "Walmart",
    "COST": "Costco",

    "KO": "Coca-Cola",
    "PEP": "PepsiCo",

    "MCD": "McDonald's",
    "NKE": "Nike",

    "DIS": "Walt Disney",

    "UBER": "Uber",
    "PYPL": "PayPal",

    "BA": "Boeing",
    "GE": "GE Aerospace",

    "AVGO": "Broadcom"
}


def get_market_data():

    symbols = list(
        STOCKS.keys()
    )

    results = []

    try:

        data = yf.download(

            symbols,

            period="5d",

            interval="1d",

            group_by="ticker",

            progress=False,

            auto_adjust=False,

            threads=True
        )

        for symbol in symbols:

            try:

                stock = data[
                    symbol
                ].dropna()

                if stock.empty:
                    continue

                latest = stock.iloc[-1]

                price = float(
                    latest["Close"]
                )

                high = float(
                    latest["High"]
                )

                low = float(
                    latest["Low"]
                )

                volume = int(
                    latest["Volume"]
                )

                if len(stock) > 1:

                    previous = float(
                        stock.iloc[-2]["Close"]
                    )

                else:

                    previous = price

                change = (
                    price
                    - previous
                )

                if previous:

                    change_percent = (
                        change
                        / previous
                    ) * 100

                else:

                    change_percent = 0

                results.append({

                    "symbol":
                        symbol,

                    "name":
                        STOCKS[symbol],

                    "price":
                        round(price, 2),

                    "change":
                        round(change, 2),

                    "change_percent":
                        round(
                            change_percent,
                            2
                        ),

                    "high":
                        round(high, 2),

                    "low":
                        round(low, 2),

                    "volume":
                        volume
                })

            except Exception as error:

                print(
                    "Stock error:",
                    symbol,
                    error
                )

        return results

    except Exception as error:

        print(
            "Market error:",
            error
        )

        return []


def get_top_gainers(stocks):

    return sorted(

        stocks,

        key=lambda x:
            x["change_percent"],

        reverse=True
    )


def get_top_losers(stocks):

    return sorted(

        stocks,

        key=lambda x:
            x["change_percent"]
    )


def get_chart_data(

    symbol,

    period="1mo"
):

    try:

        data = yf.download(

            symbol,

            period=period,

            interval="1d",

            progress=False,

            auto_adjust=False
        )

        if data.empty:

            return []

        if (
            hasattr(
                data.columns,
                "nlevels"
            )

            and

            data.columns.nlevels > 1
        ):

            data.columns = (
                data.columns
                .get_level_values(0)
            )

        result = []

        for index, row in data.iterrows():

            result.append({

                "date":
                    str(index.date()),

                "open":
                    round(
                        float(
                            row["Open"]
                        ),
                        2
                    ),

                "high":
                    round(
                        float(
                            row["High"]
                        ),
                        2
                    ),

                "low":
                    round(
                        float(
                            row["Low"]
                        ),
                        2
                    ),

                "close":
                    round(
                        float(
                            row["Close"]
                        ),
                        2
                    ),

                "volume":
                    int(
                        row["Volume"]
                    )
            })

        return result

    except Exception as error:

        print(
            "Chart error:",
            error
        )

        return []
