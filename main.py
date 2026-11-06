from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Server is running!"}

@app.get("/search")
def search_screen(model: str):
    # Запрос к сайту lcd4laptop (Shopify API)
    url = f"https://www.lcd4laptop.co.uk/search/suggest.json?q={model}&resources[type]=product"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        products = data.get('resources', {}).get('results', {}).get('products', [])
        
        results = []
        for item in products:
            results.append({
                "title": item.get('title'),
                "price": item.get('price'),
                "link": "https://www.lcd4laptop.co.uk" + item.get('url')
            })
            
        return {"query": model, "count": len(results), "results": results}
    except Exception as e:
        return {"error": str(e)}