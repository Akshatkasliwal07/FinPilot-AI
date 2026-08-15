INDIAN_SYMBOL_MAP = {

    "Tata Motors": "TATAMOTORS.NS",

    "Reliance Industries": "RELIANCE.NS",

    "Infosys": "INFY.NS",

    "TCS": "TCS.NS",

    "HDFC Bank": "HDFCBANK.NS",

    "Apple": "AAPL",

    "Tesla": "TSLA"

}



def resolve_symbol(company: str):

    return INDIAN_SYMBOL_MAP.get(
        company,
        company
    )