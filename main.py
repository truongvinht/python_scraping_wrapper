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