# web2md.py
from adapters import browser, python, file
import datetime

try:
    result = (browser.open("https://news.ycombinator.com/")
              .wait(2)
              .extract({
                  'titles': {
                      'selector': '.titleline > a',
                      'attribute': 'innerText',
                      'multiple': True
                  },
                  'urls': {
                      'selector': '.titleline > a',
                      'attribute': 'href',
                      'multiple': True
                  },
                  'scores': {
                      'selector': '.score',
                      'multiple': True
                  }
              })
              | python.execute("""
# Process the scraped data into a structured format
import datetime

news_items = []
for i in range(min(len(data['titles']), len(data['urls']))):
    score_text = data['scores'][i] if i < len(data['scores']) else "0 points"
    score = int(score_text.replace(' points', '')) if 'points' in score_text else 0

    news_items.append({
        'title': data['titles'][i],
        'url': data['urls'][i],
        'score': score,
        'timestamp': str(datetime.datetime.now())
    })

# Create markdown content
current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
md_content = f"# HackerNews Top Stories\n\nScraped on: {current_date}\n\n"

for i, item in enumerate(news_items):
    md_content += f"## {i+1}. {item['title']}\n"
    md_content += f"- Score: {item['score']} points\n"
    md_content += f"- URL: {item['url']}\n"
    md_content += f"- Timestamp: {item['timestamp']}\n\n"

result = md_content
""")
              | file.write("hackernews.md")
              .execute())

    print(f"Scraped HackerNews stories and saved to hackernews.md")

except Exception as e:
    print(f"Error in pipeline: {e}")
    import traceback
    traceback.print_exc()