document.addEventListener(
    "DOMContentLoaded",
    async () => {


        try {


            const response =
                await fetch(
                    "/api/stocks"
                );


            const market =
                await response.json();


            const stocks =
                market.stocks || [];


            if (!stocks.length) {

                return;

            }


            /* ================= LINE ================= */

            const lineLabels =
                stocks
                    .slice(0, 10)
                    .map(
                        stock =>
                            stock.symbol
                    );


            const linePrices =
                stocks
                    .slice(0, 10)
                    .map(
                        stock =>
                            stock.price
                    );


            new Chart(
                document.getElementById(
                    "lineChart"
                ),
                {

                    type:
                        "line",

                    data: {

                        labels:
                            lineLabels,

                        datasets: [

                            {

                                label:
                                    "Stock Price",

                                data:
                                    linePrices,

                                borderWidth:
                                    3,

                                tension:
                                    0.4

                            }

                        ]

                    }

                }
            );


            /* ================= BAR ================= */

            const changes =
                stocks
                    .slice(0, 15)
                    .map(
                        stock =>
                            stock.change_percent
                    );


            new Chart(
                document.getElementById(
                    "barChart"
                ),
                {

                    type:
                        "bar",

                    data: {

                        labels:
                            stocks
                                .slice(0, 15)
                                .map(
                                    s =>
                                        s.symbol
                                ),

                        datasets: [

                            {

                                label:
                                    "% Change",

                                data:
                                    changes

                            }

                        ]

                    }

                }
            );


            /* ================= VOLUME ================= */

            new Chart(
                document.getElementById(
                    "volumeChart"
                ),
                {

                    type:
                        "bar",

                    data: {

                        labels:
                            stocks
                                .slice(0, 12)
                                .map(
                                    s =>
                                        s.symbol
                                ),

                        datasets: [

                            {

                                label:
                                    "Volume",

                                data:
                                    stocks
                                        .slice(0, 12)
                                        .map(
                                            s =>
                                                s.volume
                                        )

                            }

                        ]

                    }

                }
            );


            /* ================= SECTOR ================= */

            const sectors = {

                Technology: 12,

                Finance: 5,

                Consumer: 6,

                Entertainment: 3,

                Industrial: 4,

                Other: 3

            };


            new Chart(
                document.getElementById(
                    "sectorChart"
                ),
                {

                    type:
                        "doughnut",

                    data: {

                        labels:
                            Object.keys(
                                sectors
                            ),

                        datasets: [

                            {

                                data:
                                    Object.values(
                                        sectors
                                    )

                            }

                        ]

                    }

                }
            );


        }


        catch (error) {

            console.log(
                "Chart error:",
                error
            );

        }


    }
);