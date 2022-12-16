import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import math

# could use `anime` as base, but confusing (/anime(list)/)
BASE_URL = "https://myanimelist.net" # always end with no slash, looks nicer
# URL = "https://myanimelist.net/anime/29803/Overlord/userrecs"
# page = requests.get(URL)

# print(len(page.content))

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def get_recomendations(id):
    url = f"{BASE_URL}/{id}/userrecs" #f"{BASE_URL}/anime/{id}/userrecs"
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
            # this should not have dupes
            if inner_text.isnumeric():
                recommendations[-1]['amount'] = int(inner_text)
            else: # this is if only one person recommended it (they dont print a 1)
                recommendations.append({
                    'name': inner_text,
                    'link': tag.parent['href'],
                    'amount': 1,
                    'recommender': id # need better name
                })
        # break

    return recommendations, len(page.content)

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

    return animes_watched, len(page.content)


# ACTUAL CODE
threshold = 1
bytesDownloaded = 0

watched, bytes_user = get_watched('yoeyshapiro')
bytesDownloaded += bytes_user

recommendations = []
pbar = tqdm(watched, total=len(watched))
for anime in pbar:
    pbar.set_description(f'Getting Recs of \"{anime["name"]}\"')
    # this returns a list
    recs_found, bytes_anime = get_recomendations(anime['anime_url']) # this adds anime to the title
    # add the values
    recommendations += recs_found
    bytesDownloaded += bytes_anime
    # break

mapped_recs = {} # best way?
uniques = []

pbar = tqdm(recommendations, total=len(recommendations))
for anime in pbar:
    pbar.set_description(f'Mapping recommendations')
    if anime['link'] in uniques:
        mapped_recs[anime['link']]['times_recommended'].append(
            {
                "recommender": anime['recommender'],
                "amount": anime['amount']
            })
    else:
        uniques.append(anime['link'])
        rec = {
            'name': anime['name'],
            'link': anime['link'],
            'times_recommended': [ # list of each recommendations amount (times people recommend it); maybe add anime its from
                {
                    "recommender": anime['recommender'], # this way is easier to manage, but looks worse
                    "amount": anime['amount']
                }
            ],
        }
        mapped_recs[anime['link']] = rec # can i use this to search

print(len(mapped_recs))
final = [ pair[1] for pair in list(mapped_recs.items())]
sorted_recs = sorted(final, key=lambda x: len(x['times_recommended']), reverse=True)

# now deal with the pairs and how; and show bytes downloaded; also what if i already watched it (GNN)
for anime in sorted_recs:
    if len(anime['times_recommended']) > 1:
        print(anime['name'], "############", sum(recommender['amount'] for recommender in anime['times_recommended']))

print(f'Total bytes downloadled {convert_size(bytesDownloaded)}')