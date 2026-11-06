import re
import urllib.parse
from fastapi import FastAPI, Query
import requests

app = FastAPI()

# Кэш для курса валют, чтобы не делать лишних запросов
exchange_rate_cache = {"rate": 1.18}


def get_gbp_to_eur_rate():
    try:
        url = "https://open.er-api.com/v6/latest/GBP"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data.get("rates", {}).get("EUR")
            if rate:
                exchange_rate_cache["rate"] = float(rate)
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")

    return exchange_rate_cache["rate"]


@app.get("/")
def home():
    return {"status": "Server is running!"}


@app.get("/search")
def search_screen(model: str = Query(..., description="Laptop model or part number")):
    url = f"https://www.lcd4laptop.co.uk/search/suggest.json?q={urllib.parse.quote(model)}&resources[type]=product"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    eur_rate = get_gbp_to_eur_rate()

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        products = data.get("resources", {}).get("results", {}).get("products", [])

        results = []
        for item in products:
            raw_price = item.get("price", "")
            price_eur_str = ""

            clean_price = re.sub(r"[^\d.]", "", str(raw_price))
            if clean_price:
                try:
                    price_gbp = float(clean_price)
                    price_eur = round(price_gbp * eur_rate, 2)
                    price_eur_str = f"{price_eur:.2f}"
                except ValueError:
                    price_eur_str = str(raw_price)

            results.append(
                {
                    "title": item.get("title"),
                    "price": price_eur_str,
                    "link": "https://www.lcd4laptop.co.uk" + item.get("url"),
                }
            )

        return {"query": model, "count": len(results), "results": results}
    except Exception as e:
        return {"query": model, "count": 0, "results": [], "error": str(e)}
