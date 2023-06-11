import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://myanimelist.net"
bytesDownloaded = 0
user = 'yoeyshapiro'#'Flare_Eyes'
anime_url = ''

def get_char_page(url_id: str) -> str:
    page = requests.get(url_id)
    soup = BeautifulSoup(page.content, "html.parser")

    links = soup.find_all('a')
    for link in links:
        if link.getText() == 'Characters & Staff':
            return link['href']

def get_jp_actor(tag, language):
    actors = tag.find_all('tr', class_='js-anime-character-va-lang')
    for actor in actors:
        lang = actor.find('div', class_='spaceit_pad js-anime-character-language')
        if language in lang.getText():
            atag = actor.find('div', class_='spaceit_pad').find('a')
            return atag.getText(), atag['href']

def get_characters(anime_id: str):
    anime_url = get_char_page(anime_id)
    print(anime_url)
    page = requests.get(anime_url)

    soup = BeautifulSoup(page.content, "html.parser")
    actors = {}

    character = soup.find("div", class_="anime-character-container js-anime-character-container")
    for tag in character.find_all('table', class_='js-anime-character-table'):
        print(get_jp_actor(tag, 'Japanese'))

        break

    return actors, len(page.content)

def get_watched(user):
    url = f"{BASE_URL}/animelist/{user}?status=2"
    # print(url)
    animes_watched = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    # with open('test2.html', 'w') as f:
    #     f.write(str(page.content))

    found_recs = soup.find_all("table", class_="list-table") # list-table-data
    if len(found_recs) > 1:
        print('more than one')
    found_recs = found_recs[0]
    data = json.loads(found_recs['data-items']) #data-broadcasts
    for anime in data:
        watched = {
            "name": anime['anime_title'],
            "anime_url": anime['anime_url'],
            "score": anime['score']
        }
        animes_watched.append(watched)

    return animes_watched, len(page.content)

# watched, bytes_user = get_watched(user)
# bytesDownloaded += bytes_user
get_characters('https://myanimelist.net/anime/36038')