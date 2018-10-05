import json

with open('pois-cikm.json', 'r') as pois_file:
    pois = json.load(pois_file)
    new_pois = []
    for poi in pois[:50]:
        new_poi = {}
        new_poi['cuisine'] = ",".join(poi['cuisines'])
        # new_poi['city']  = poi['city']
        # new_poi['country'] = poi['country']
        new_poi['name'] = poi['name']
        new_poi['id'] = poi['name']
        new_poi['topics'] = ";".join(poi['topics'])
        new_pois.append(new_poi)
with open('pois-transformed.json','w') as new_pois_file:
    json.dump(new_pois,new_pois_file)

