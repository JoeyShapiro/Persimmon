import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import math
import numpy as np
import networkx as nx

# could use `anime` as base, but confusing (/anime(list)/)
BASE_URL = "https://myanimelist.net" # always end with no slash, looks nicer
# URL = "https://myanimelist.net/anime/29803/Overlord/userrecs"
# page = requests.get(URL)

# print(len(page.content))

# ai score = sum(k_score * k_recommenders) k = current anime

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def softmax_animes(animes, field):
    """Modifies the given list by adding a softmaxed, of the given field. The softmax will be in f'{field}_soft'"""
    bottom = np.exp([rec[field] for rec in animes]).sum()

    for anime in animes:
        anime[f'{field}_soft'] = np.exp(anime[field]) / bottom

def soft_items(items, field):
    """Modifies the given list by adding a \"soft\" to the dict. This is field / max. Stored in f'{field}_soft'"""
    m = max([item[field] for item in items])

    for item in items:
        item[f'{field}_soft'] = item[field] / m

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
user = 'yoeyshapiro'

watched, bytes_user = get_watched(user)
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

# remove already watched ones (i feel like i already do this)
for anime in watched: # smart to use watched
    for rec in recommendations:
        if f"{BASE_URL}{anime['anime_url']}" == rec['link']:
            recommendations.remove(rec)

# convert the recs to a tree list
pbar = tqdm(recommendations, total=len(recommendations))
for anime in pbar:
    pbar.set_description(f'Mapping recommendations')
    # should remake to have 'if' be 'isNew'
    if anime['link'] in uniques: # if its a repeat
        mapped_recs[anime['link']]['times_recommended'].append(
            {
                "recommender": anime['recommender'],
                "amount": anime['amount']
            })
    else: # if it hasnt been seen before
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
            'ai_score': 0
        }
        mapped_recs[anime['link']] = rec # can i use this to search

recs_as_list = [ pair[1] for pair in list(mapped_recs.items())]

# all i really need
watched_scores = {}
for anime in watched:
    watched_scores[anime['anime_url']] = anime['score']

# get ai score (better version of 'sum amounts')
print('Getting softmaxed, \"AI\" scores...')
for anime in recs_as_list:
    for recommender in anime['times_recommended']:
        # sum(rec_score * rec_amount)
        anime['ai_score'] += watched_scores[recommender['recommender']] * recommender['amount']
        # print(anime['ai_score'], '+=', watched_scores[recommender['recommender']], '*', recommender['amount'], recommender['recommender'])

# softmax_animes(recs_as_list, 'ai_score')
soft_items(recs_as_list, 'ai_score')

sorted_recs = sorted(recs_as_list, key=lambda x: x['ai_score_soft'], reverse=True)


# print(f'Showing recommendations for \"{user}\"')
# print('This list is sorted by the amount of times an anime is recommended by another anime')
# # now deal with the pairs and how; and show bytes downloaded; also what if i already watched it (GNN)
# for anime in sorted_recs:
#     if anime['ai_score_soft'] > 0.1:
#         print(anime['name'], "############", anime['ai_score_soft'])

# print(f'Total bytes downloadled {convert_size(bytesDownloaded)}')

with open('recommendations.html', 'w') as f:
    f.write(f'<h1>Username: {user}</h1>\n')
    f.write(f'<h3>Bytes Downloaded: {convert_size(bytesDownloaded)}</h3>\n')
    f.write(f'<h3>{user} has watched {len(watched)} anime, and was recommended {len(sorted_recs)}.</h3>\n')
    f.write('<table>\n')
    f.write('\t<tr>\n')
    f.write('\t\t<th>Name</th>\n')
    f.write('\t\t<th>Soft Score</th>\n')
    f.write('\t\t<th>Amount</th>\n')
    f.write('\t\t<th>Score</th>\n')
    f.write('\t</tr>\n')
    for anime in sorted_recs:
        f.write('\t<tr>\n')
        f.write(f'\t\t<td><a href="{anime["link"]}">{anime["name"]}</a></td>\n')
        f.write(f'\t\t<td>{anime["ai_score_soft"]}</td>\n')
        f.write(f'\t\t<td>{len(anime["times_recommended"])}</td>\n')
        f.write(f'\t\t<td>{anime["ai_score"]}</td>\n')
        f.write('\t</tr>\n')

    f.write('</table>\n')

# graph time
G = nx.Graph()
for anime in sorted_recs:
    if anime['ai_score_soft'] >= 0.1:
        for rec in anime['times_recommended']:
            G.add_edge(anime['link'], rec['recommender'])

import matplotlib.pyplot as plt

nx.draw(G, with_labels=True)

plt.show()
