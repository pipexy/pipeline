# flask_scraper.py
from flask import Flask, jsonify, render_template_string, send_file
import requests
from bs4 import BeautifulSoup
import datetime
import io

app = Flask(__name__)


def scrape_softreck():
    try:
        response = requests.get('https://softreck.com', timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract data
        data = {
            'title': soup.title.text if soup.title else 'No title found',
            'headings': [h.text.strip() for h in soup.select('h1, h2, h3')],
            'links': [a.get('href') for a in soup.find_all('a') if a.get('href')]
        }

        return data, None
    except Exception as e:
        return None, str(e)


@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Softreck Scraper</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .button { 
                padding: 10px 15px; 
                background: #4CAF50; 
                color: white; 
                text-decoration: none; 
                margin: 10px 5px;
                display: inline-block;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>Softreck Web Scraper</h1>
        <p>This service scrapes data from softreck.com using requests and BeautifulSoup.</p>
        <a href="/scrape/json" class="button">View as JSON</a>
        <a href="/scrape/markdown" class="button">Download as Markdown</a>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/scrape/json')
def scrape_json():
    data, error = scrape_softreck()
    if error:
        return jsonify({'error': error}), 500
    return jsonify(data)


@app.route('/scrape/markdown')
def scrape_markdown():
    data, error = scrape_softreck()
    if error:
        return f"Error: {error}", 500

    # Format as markdown
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    md_content = f"# Softreck Website Analysis\n\n"
    md_content += f"Scraped on: {current_date}\n\n"

    # Add page title
    md_content += f"## Page Title\n{data['title']}\n\n"

    # Add headings found on the page
    md_content += "## Headings\n"
    for i, heading in enumerate(data['headings']):
        md_content += f"{i + 1}. {heading}\n"
    md_content += "\n"

    # Add links
    md_content += "## Links\n"
    unique_links = set()
    for link in data['links']:
        if link and not link.startswith('#') and not link == '/':
            unique_links.add(link)

    for i, link in enumerate(sorted(unique_links)):
        md_content += f"{i + 1}. [{link}]({link})\n"

    # Create a file-like object from the markdown content
    buffer = io.BytesIO(md_content.encode('utf-8'))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='softreck.md',
        mimetype='text/markdown'
    )


if __name__ == '__main__':
    print("Server starting at http://127.0.0.1:5000")
    app.run(debug=True)