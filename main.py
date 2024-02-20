import browser

file_name = "config/config_file.ini"
insta_link = "https://www.instagram.com"

webScraper = browser.Driver(insta_link, file_name)
webScraper.run()
webScraper.close()

