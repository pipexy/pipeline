# softreck2md.py
from adapters import browser, python, file

try:
    result = (browser.open("https://softreck.com")
              .wait(2)
              .extract({
                  'title': {
                      'selector': 'title',
                      'multiple': False
                  },
                  'headings': {
                      'selector': 'h1, h2, h3',
                      'multiple': True
                  },
                  'links': {
                      'selector': 'a',
                      'attribute': 'href',
                      'multiple': True
                  }
              })
              | python.execute("""
# Format scraped data as markdown
import datetime

current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
md_content = f"# Softreck Website Analysis\\n\\n"
md_content += f"Scraped on: {current_date}\\n\\n"

# Add page title
md_content += f"## Page Title\\n{data['title']}\\n\\n"

# Add headings found on the page
md_content += "## Headings\\n"
for i, heading in enumerate(data['headings']):
    md_content += f"{i+1}. {heading}\\n"
md_content += "\\n"

# Add links
md_content += "## Links\\n"
unique_links = set()
for link in data['links']:
    if link and not link.startswith('#') and not link == '/':
        unique_links.add(link)

for i, link in enumerate(sorted(unique_links)):
    md_content += f"{i+1}. [{link}]({link})\\n"

result = md_content
""")
              | file.write("softreck.md")
              .execute())

    print(f"Scraped Softreck website and saved to softreck.md")

except Exception as e:
    print(f"Error in pipeline: {e}")
    import traceback
    traceback.print_exc()