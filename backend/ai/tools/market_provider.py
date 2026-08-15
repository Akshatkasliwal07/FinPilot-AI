import yfinance as yf


def get_market_data(symbol):

    try:

        ticker = yf.Ticker(symbol)

        data = ticker.history(
            period="5d"
        )


        if data.empty:

            return {

                "success":False,
                "message":
                f"No data for {symbol}"

            }


        return {

            "success":True,

            "data":{

                "price":
                float(
                    data["Close"].iloc[-1]
                ),

                "high":
                float(
                    data["High"].iloc[-1]
                ),

                "low":
                float(
                    data["Low"].iloc[-1]
                )

            }

        }


    except Exception as e:


        return {

            "success":False,
            "message":str(e)

        }