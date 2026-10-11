console.log("PREDICTION JS LOADED");

/* =========================================================
   STOCKVISION PRO - PREDICTION JAVASCRIPT
   ========================================================= */

/* ================= PAGE LOAD ================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("Prediction page loaded");

    const input = document.getElementById("stockSymbol");

    if (input && input.value.trim()) {
        runPrediction();
    }

});


/* ================= SELECT STOCK ================= */

function selectStock(symbol) {

    const input = document.getElementById("stockSymbol");

    if (!input) {
        console.error("stockSymbol input not found");
        return;
    }

    if (input.disabled) {
        return;
    }

    input.value = symbol;

    runPrediction();
}


/* ================= RUN PREDICTION ================= */

async function runPrediction() {

    const input = document.getElementById("stockSymbol");

    if (!input) {
        console.error("stockSymbol element not found");
        showError("Stock symbol input not found.");
        return;
    }

    const symbol = input.value.trim().toUpperCase();
    const horizon = document.getElementById("predictionHorizon").value;

    if (!symbol) {
        showError("Please enter a valid stock symbol.");
        return;
    }

    console.log("Starting prediction for:", symbol);

    showLoading(true);
    hideError();

    try {

        const response = await fetch(
          `/api/prediction?symbol=${encodeURIComponent(symbol)}&horizon=${horizon}`   
        );

        console.log("API status:", response.status);

        if (!response.ok) {
            throw new Error(
                `Prediction API returned status ${response.status}`
            );
        }

        const data = await response.json();

        console.log("Prediction API Response:", data);

        if (!data || data.success !== true) {

            showError(
                data && data.message
                    ? data.message
                    : "Unable to generate prediction."
            );

            return;
        }

        console.log("DISPLAYING PREDICTION DATA");

        displayPrediction(data);

    } catch (error) {

        console.error("Prediction error:", error);

        showError(
            error.message ||
            "Unable to connect to the prediction service."
        );

    } finally {

        showLoading(false);

    }
}


/* ================= DISPLAY RESULT ================= */

function displayPrediction(data) {

    console.log("1. displayPrediction started");

    const currentPrice =
        document.getElementById("currentPrice");

    if (currentPrice) {
        currentPrice.textContent =
            formatPrice(data.current_price);
    }


    const predictedPrice =
        document.getElementById("predictedPrice");

    if (predictedPrice) {
        predictedPrice.textContent =
            formatPrice(data.predicted_price);
    }

    const predictionPeriod =
    document.getElementById("predictionPeriod");

if (predictionPeriod) {
    predictionPeriod.textContent =
        data.horizon_label || "Next Trading Day";
}


    const changeElement =
        document.getElementById("expectedChange");

    const change =
        Number(data.expected_change);

    if (changeElement) {

        changeElement.textContent =
            `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`;

    }


    const confidence =
        document.getElementById("confidence");

    if (confidence) {

        confidence.textContent =
            `${Number(data.confidence).toFixed(1)}%`;

    }


    const trend =
        document.getElementById("trend");

    if (trend) {
        trend.textContent =
            data.trend || "--";
    }


    const signal =
        document.getElementById("signal");

    if (signal) {
        signal.textContent =
            data.signal || "--";
    }


    const risk =
        document.getElementById("risk");

    if (risk) {
        risk.textContent =
            data.risk || "--";
    }


    const rsi =
        document.getElementById("rsi");

    if (rsi) {
        rsi.textContent =
            Number(data.rsi).toFixed(2);
    }


    const macd =
        document.getElementById("macd");

    if (macd) {
        macd.textContent =
            Number(data.macd).toFixed(4);
    }


    const predictionSymbol =
        document.getElementById("predictionSymbol");

    if (predictionSymbol) {
        predictionSymbol.textContent =
            data.symbol || "--";
    }


    console.log("5. all values done");

    updateColors(data);

    console.log("6. colors done");

    drawPredictionChart(data);

    console.log("7. chart done");
}


/* ================= FORMAT PRICE ================= */

function formatPrice(value) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return "$" + number.toLocaleString(
        "en-US",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    );
}


/* ================= COLORS ================= */

function updateColors(data) {

    const changeElement =
        document.getElementById("expectedChange");

    const trendElement =
        document.getElementById("trend");

    const signalElement =
        document.getElementById("signal");

    const riskElement =
        document.getElementById("risk");


    if (changeElement) {

        changeElement.style.color =
            Number(data.expected_change) >= 0
                ? "#22c55e"
                : "#ef4444";
    }


    if (trendElement) {

        if (data.trend === "BULLISH") {
            trendElement.style.color = "#22c55e";
        } else if (data.trend === "BEARISH") {
            trendElement.style.color = "#ef4444";
        } else {
            trendElement.style.color = "#facc15";
        }
    }


    if (signalElement) {

        if (data.signal === "BUY") {
            signalElement.style.color = "#22c55e";
        } else if (data.signal === "SELL") {
            signalElement.style.color = "#ef4444";
        } else {
            signalElement.style.color = "#facc15";
        }
    }


    if (riskElement) {

        if (data.risk === "LOW") {
            riskElement.style.color = "#22c55e";
        } else if (data.risk === "HIGH") {
            riskElement.style.color = "#ef4444";
        } else {
            riskElement.style.color = "#facc15";
        }
    }
}


/* ================= PREDICTION CHART ================= */

function drawPredictionChart(data) {

    const chart =
        document.getElementById("predictionChart");

    if (!chart) {
        console.error("predictionChart element not found");
        return;
    }

    if (typeof Plotly === "undefined") {

        console.error("Plotly library is not loaded.");

        showError(
            "Chart library could not be loaded."
        );

        return;
    }


    const historicalDates =
        Array.isArray(data.historical_dates)
            ? data.historical_dates
            : [];

    const historicalPrices =
        Array.isArray(data.historical_prices)
            ? data.historical_prices
            : [];

    const predictionDates =
        Array.isArray(data.prediction_dates)
            ? data.prediction_dates
            : [];

    const predictionPrices =
        Array.isArray(data.prediction_prices)
            ? data.prediction_prices
            : [];


    if (
        historicalDates.length === 0 ||
        historicalPrices.length === 0
    ) {

        console.error(
            "Historical chart data is missing."
        );

        return;
    }


    const historicalTrace = {

        x: historicalDates,
        y: historicalPrices,

        type: "scatter",
        mode: "lines",

        name: `${data.symbol} Historical`,

        line: {
            width: 2
        }
    };


    const predictionTrace = {

        x: predictionDates,
        y: predictionPrices,

        type: "scatter",
        mode: "lines+markers",

        name: "AI Prediction",

        line: {
            width: 3,
            dash: "dot"
        },

        marker: {
            size: 8
        }
    };


    const layout = {

        paper_bgcolor: "rgba(0,0,0,0)",

        plot_bgcolor: "rgba(0,0,0,0)",

        margin: {
            l: 55,
            r: 20,
            t: 35,
            b: 45
        },

        font: {
            color: "#a7a7b5"
        },

        xaxis: {
            gridcolor: "rgba(255,255,255,0.06)",
            zeroline: false,
            showline: false
        },

        yaxis: {
            gridcolor: "rgba(255,255,255,0.06)",
            zeroline: false,
            showline: false,
            tickprefix: "$"
        },

        legend: {
            orientation: "h",
            y: 1.08,
            x: 0
        },

        hovermode: "x unified"
    };


    const config = {

        responsive: true,

        displaylogo: false,

        modeBarButtonsToRemove: [
            "lasso2d",
            "select2d"
        ]
    };


    try {

        Plotly.newPlot(
            "predictionChart",
            [
                historicalTrace,
                predictionTrace
            ],
            layout,
            config
        );

    } catch (error) {

        console.error(
            "Prediction chart error:",
            error
        );
    }
}


/* ================= LOADING ================= */

function showLoading(show) {

    const loading =
        document.getElementById("predictionLoading");

    const results =
        document.getElementById("predictionResults");

    const predictButton =
        document.querySelector(".predict-btn");

    const stockInput =
        document.getElementById("stockSymbol");

    const stockControls =
        document.querySelectorAll(
            ".stock-option, .stock-btn, .stock-card"
        );


    if (show) {

        if (loading) {
            loading.style.display = "block";
        }

        if (results) {
            results.style.opacity = "0.35";
        }

        if (stockInput) {
            stockInput.disabled = true;
        }

        if (predictButton) {

            predictButton.disabled = true;

            predictButton.setAttribute(
                "aria-disabled",
                "true"
            );

            predictButton.style.opacity = "0.6";

            predictButton.style.cursor =
                "not-allowed";
        }

        stockControls.forEach(function (control) {

            control.disabled = true;

            control.setAttribute(
                "aria-disabled",
                "true"
            );

            control.style.pointerEvents = "none";

            control.style.opacity = "0.6";
        });

    } else {

        if (loading) {
            loading.style.display = "none";
        }

        if (results) {
            results.style.opacity = "1";
        }

        if (stockInput) {
            stockInput.disabled = false;
        }

        if (predictButton) {

            predictButton.disabled = false;

            predictButton.setAttribute(
                "aria-disabled",
                "false"
            );

            predictButton.style.opacity = "1";

            predictButton.style.cursor = "pointer";
        }

        stockControls.forEach(function (control) {

            control.disabled = false;

            control.setAttribute(
                "aria-disabled",
                "false"
            );

            control.style.pointerEvents = "";

            control.style.opacity = "1";
        });
    }
}


/* ================= ERROR ================= */

function showError(message) {

    const errorBox =
        document.getElementById("predictionError");

    const errorMessage =
        document.getElementById("errorMessage");


    if (errorMessage) {
        errorMessage.textContent = message;
    }

    if (errorBox) {
        errorBox.style.display = "flex";
    }

    console.error(
        "Prediction UI Error:",
        message
    );
}


/* ================= HIDE ERROR ================= */

function hideError() {

    const errorBox =
        document.getElementById("predictionError");

    if (errorBox) {
        errorBox.style.display = "none";
    }
}


/* ================= ENTER KEY ================= */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            document.activeElement &&
            document.activeElement.id === "stockSymbol"
        ) {

            event.preventDefault();

            const input =
                document.getElementById("stockSymbol");

            if (
                input &&
                !input.disabled
            ) {

                runPrediction();
            }
        }
    }
);