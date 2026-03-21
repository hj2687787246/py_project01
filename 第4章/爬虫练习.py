#
import requests
from lxml import html

target_url = 'https://www.tiobe.com/tiobe-index/'

response = requests.get(target_url)

html.fromstring(response.text)

print(response.text)