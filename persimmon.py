import json
import requests
from bs4 import BeautifulSoup

# could use `anime` as base, but confusing (/anime(list)/)
BASE_URL = "https://myanimelist.net" # always end with no slash, looks nicer
# URL = "https://myanimelist.net/anime/29803/Overlord/userrecs"
# page = requests.get(URL)

# print(len(page.content))

def get_recomendations(id):
    url = f"{BASE_URL}/anime/{id}/userrecs"
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    recommendations = []

    found_recs = soup.find_all("div", class_="borderClass")
    for rec in found_recs:
        # print(rec, end="\n"*2)
        for tag in rec.find_all("strong"):
            # print(tag.getText(), tag.parent['href'])
            inner_text = tag.getText()

            # this assumes that the amount of recommendations is right after the value in the list
            if inner_text.isnumeric():
                recommendations[-1]['amount'] = int(inner_text)
            else:
                recommendations.append({
                    'name': inner_text,
                    'link': tag.parent['href'],
                    'amount': 1
                })
        # break

    return recommendations

def get_watched(user):
    url = f"{BASE_URL}/animelist/{user}?status=2"
    # print(url)
    animes_watched = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

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

    return animes_watched

print(get_watched('yoeyshapiro'))
# for r in get_recomendations('29803/Overlord'):
#     print(r)