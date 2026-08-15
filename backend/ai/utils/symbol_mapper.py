SYMBOL_MAP = {
    "tata motors": "TMCV.NS",
    "tata": "TMCV.NS",
    "reliance": "RELIANCE.NS",
    "infosys": "INFY.NS",
    "sbi": "SBIN.NS",
    "tcs": "TCS.NS",
    "hdfc bank": "HDFCBANK.NS",
}


def get_symbol(company_name):
    key = company_name.lower().strip()

    return SYMBOL_MAP.get(key)