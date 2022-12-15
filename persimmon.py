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

# this gives wierd data. like checks and stuff
# get user data
url = f"{BASE_URL}/animelist/yoeyshapiro?status=2"
print(url)
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
print(soup.contents)
# write to file <---------
with open('test.html', 'w') as f:
    f.write(str(soup.contents))

found_recs = soup.find_all("tr", class_="list-table-data") # list-table-data
for r in found_recs:
    # print(r)
    break

# for r in get_recomendations('29803/Overlord'):
#     print(r)