import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor


# =========================================================
# TECHNICAL INDICATORS
# =========================================================

def calculate_indicators(df):

    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = df["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    df["MACD"] = ema12 - ema26

    df["Volume_MA20"] = df["Volume"].rolling(
        window=20
    ).mean()

    return df


# =========================================================
# GET HISTORICAL DATA
# =========================================================

def get_prediction_data(symbol):

    symbol = symbol.upper().strip()

    try:

        ticker = yf.Ticker(symbol)

        df = ticker.history(
            period="2y",
            interval="1d",
            auto_adjust=True
        )

        if df.empty:
            return None

        df = df.reset_index()

        df = calculate_indicators(df)

        return df

    except Exception as e:

        print("Prediction data error:", e)

        return None


# =========================================================
# TRAIN RANDOM FOREST MODEL
# =========================================================

def train_prediction_model(df, horizon=1):

    features = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "MA20",
        "MA50",
        "RSI",
        "MACD",
        "Volume_MA20"
    ]

    data = df.copy()

    # -----------------------------------------------------
    # FUTURE TARGET
    # horizon = 1  -> next trading day
    # horizon = 7  -> 7 trading days
    # horizon = 21 -> approximately 1 month
    # -----------------------------------------------------

    data["Target"] = data["Close"].shift(-horizon)

    data = data.dropna()

    if len(data) < 100:

        return None, None

    X = data[features]
    y = data["Target"]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=12,
        min_samples_split=5,
        n_jobs=-1
    )

    model.fit(X, y)

    return model, features


# =========================================================
# HORIZON LABEL
# =========================================================

def get_horizon_label(horizon):

    if horizon == 1:
        return "Next Trading Day"

    elif horizon == 7:
        return "7 Trading Days"

    elif horizon == 21:
        return "1 Month"

    else:
        return f"{horizon} Trading Days"


# =========================================================
# STOCK PREDICTION
# =========================================================

def predict_stock(symbol, horizon=1):

    # Safety check
    try:
        horizon = int(horizon)
    except:
        horizon = 1

    # Allowed prediction periods
    allowed_horizons = [1, 7, 21]

    if horizon not in allowed_horizons:
        horizon = 1

    df = get_prediction_data(symbol)

    if df is None or df.empty:

        return {
            "success": False,
            "message": "Unable to fetch market data."
        }

    try:

        model, features = train_prediction_model(
            df,
            horizon
        )

        if model is None:

            return {
                "success": False,
                "message": "Not enough historical data."
            }

        latest = df.iloc[-1]

        latest_features = pd.DataFrame(
            [[
                latest["Open"],
                latest["High"],
                latest["Low"],
                latest["Close"],
                latest["Volume"],
                latest["MA20"],
                latest["MA50"],
                latest["RSI"],
                latest["MACD"],
                latest["Volume_MA20"]
            ]],
            columns=features
        )

        # -------------------------------------------------
        # PREDICT FUTURE PRICE
        # -------------------------------------------------

        predicted_price = float(
            model.predict(latest_features)[0]
        )

        current_price = float(
            latest["Close"]
        )

        # -------------------------------------------------
        # EXPECTED CHANGE
        # -------------------------------------------------

        expected_change = (
            (predicted_price - current_price)
            / current_price
        ) * 100

        # -------------------------------------------------
        # TREND + SIGNAL
        # -------------------------------------------------

        if expected_change >= 1.5:

            trend = "BULLISH"
            signal = "BUY"

        elif expected_change <= -1.5:

            trend = "BEARISH"
            signal = "SELL"

        else:

            trend = "NEUTRAL"
            signal = "HOLD"

        # -------------------------------------------------
        # RISK
        # -------------------------------------------------

        returns = df["Close"].pct_change()

        volatility = returns.std() * 100

        if volatility < 1.5:

            risk = "LOW"

        elif volatility < 3:

            risk = "MEDIUM"

        else:

            risk = "HIGH"

        # -------------------------------------------------
        # MODEL CONFIDENCE
        # -------------------------------------------------

        latest_values = latest_features.values

        predictions = np.array([
            estimator.predict(latest_values)[0]
            for estimator in model.estimators_
        ])

        prediction_std = np.std(
            predictions
        )

        confidence = max(
            0,
            min(
                100,
                100 - (
                    prediction_std
                    / current_price
                    * 100
                )
            )
        )

        # -------------------------------------------------
        # RSI / MACD
        # -------------------------------------------------

        rsi = float(
            latest["RSI"]
        )

        macd = float(
            latest["MACD"]
        )

        # -------------------------------------------------
        # HISTORICAL CHART DATA
        # -------------------------------------------------

        historical_dates = [
            date.strftime("%Y-%m-%d")
            for date in df["Date"].tail(90)
        ]

        historical_prices = [
            round(float(price), 2)
            for price in df["Close"].tail(90)
        ]

        # -------------------------------------------------
        # FUTURE DATE
        # -------------------------------------------------

        last_date = df["Date"].iloc[-1]

        future_date = (
            last_date
            + pd.tseries.offsets.BDay(horizon)
        )

        prediction_dates = [
            last_date.strftime("%Y-%m-%d"),
            future_date.strftime("%Y-%m-%d")
        ]

        prediction_prices = [
            round(current_price, 2),
            round(predicted_price, 2)
        ]

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        return {

            "success": True,

            "symbol": symbol,

            "horizon": horizon,

            "horizon_label": get_horizon_label(
                horizon
            ),

            "current_price": round(
                current_price,
                2
            ),

            "predicted_price": round(
                predicted_price,
                2
            ),

            "expected_change": round(
                expected_change,
                2
            ),

            "trend": trend,

            "signal": signal,

            "risk": risk,

            "confidence": round(
                confidence,
                2
            ),

            "rsi": round(
                rsi,
                2
            ),

            "macd": round(
                macd,
                2
            ),

            "historical_dates":
                historical_dates,

            "historical_prices":
                historical_prices,

            "prediction_dates":
                prediction_dates,

            "prediction_prices":
                prediction_prices
        }

    except Exception as e:

        print(
            "Prediction error:",
            e
        )

        return {

            "success": False,

            "message": str(e)
        }
