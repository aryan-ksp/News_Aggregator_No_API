from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

NEWS_SOURCES = {
    "general": "https://news.yahoo.com/",
    "technology": "https://www.yahoo.com/tech/",
    "sports": "https://sports.yahoo.com/",
    "business": "https://news.yahoo.com/business/",
}

def scrape_news(category, page=1):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = NEWS_SOURCES.get(category, NEWS_SOURCES["general"])
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []

        for item in soup.select("li.js-stream-content"):
            title_element = item.select_one("h3 a")
            img_element = item.select_one("img")

            if title_element and img_element:
                title = title_element.text.strip()
                link = title_element["href"]
                if not link.startswith("http"):
                    link = "https://news.yahoo.com" + link  # Fix relative links

                image = img_element["src"] if img_element else "https://via.placeholder.com/150"

                articles.append({"title": title, "url": link, "image": image})

        # Pagination: Return articles based on page number
        start = (page - 1) * 10
        end = start + 10
        return articles[start:end]  

    except Exception as e:
        print("Error scraping news:", e)
        return []

@app.route('/')
def home():
    category = request.args.get("category", "general")
    news = scrape_news(category, page=1)  # Load first 10 news
    return render_template("index.html", news=news, category=category)

@app.route('/load_more')
def load_more():
    category = request.args.get("category", "general")
    page = int(request.args.get("page", 1))
    news = scrape_news(category, page)
    return jsonify(news)

if __name__ == "__main__":
    app.run(debug=True)
