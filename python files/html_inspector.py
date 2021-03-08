from bs4 import BeautifulSoup
import requests

#url = "https://www.google.com/search?q=temperature+in+" + input().strip()
url = "https://www.google.com/search?q=temperature+in+toronto"

page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")


with open('test_html_raw.html', 'w') as f:
    f.writelines(soup.prettify())
