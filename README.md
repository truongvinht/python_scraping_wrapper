Scraping Wrapper Tool for getting content from website
==============
Scraping Tool written in python

# Example in main.py

```Python
from classes.contentScraper import ContentScraper

# example for Fandom
start_url = 'https://genshin-impact.fandom.com/wiki/Ganyu'

# load page configuration
scraper = ContentScraper(start_url,"./example.json")

# scrape content
content = scraper.scraping()

print(content)

# close connection
scraper.close()
```

## Result Example
Parsing for example the title and insert into result map.

```JSON
{
    "title": {
        "css_selector":"h1#firstHeading",
        "attribute":"textContent"
    }
}
```

# License
MIT License (MIT)