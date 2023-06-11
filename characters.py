import json
import requests
from bs4 import BeautifulSoup

# get characters/actors of show
# get list of watched shows
# get actors in watched shows
# find known actors in show
# add to list of all known shows
# too heavy

# get actors of show
# get list of watched shows
# get list of shows actor in
# compare list to find actor shows
# add to list of all known shows'
# lighter

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

def parse_picSurround(tag):
    atag = tag.find('a')
    img = tag.find('img')
    
    return atag['href'], img['alt']

# makes more sense, even though im getting character
# merge/join on actors, want to have this work on all
# neeeds to mbe chars. only get chars, then do lookup
# not getting all chars of all shows
def get_actors(anime_id: str):
    anime_url = get_char_page(anime_id)
    print(anime_url)
    page = requests.get(anime_url)

    soup = BeautifulSoup(page.content, "html.parser")
    actors = {}

    character = soup.find("div", class_="anime-character-container js-anime-character-container")
    for tag in character.find_all('table', class_='js-anime-character-table'):
        name, link = get_jp_actor(tag, 'Japanese')
        char_link, char_name = parse_picSurround(tag.find('div', class_='picSurround'))
        actors[name] = {
            'link': link,
            'character': char_name
        }

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

def get_characters(actor):
    characters = []
    page = requests.get(actor['link'])
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find('table', class_='js-table-people-character table-people-character')
    animes = table.find('a', class_='js-people-title')
    for anime in animes:
        characters.append({
            'show_link': anime['href'],
            'show_name': anime.getText()
        })

# watched, bytes_user = get_watched(user)
# bytesDownloaded += bytes_user
actors = get_actors('https://myanimelist.net/anime/36038')
for actor in actors:
    characters = get_characters(actor)
    # known_chars = get_known_chars(watched, characters)
    actor['chars'] = characters
    # actor['known'] = known_chars

print(actors)