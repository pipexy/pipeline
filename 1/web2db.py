from adapters import browser, database, python

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

result = news_items
""")
              | database.connect("hackernews.db")
              .insert("stories")
              .execute())

    print(f"Scraped and inserted {result.get('inserted', 0)} HackerNews stories")

except Exception as e:
    print(f"Error in pipeline: {e}")
    import traceback

    traceback.print_exc()