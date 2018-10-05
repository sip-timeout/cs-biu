import json

with open('users-cikm.json', 'r') as users_file:
    users = json.load(users_file)
    for user in users.values():
        if 'review_content' in user:
            review = {"content": user['review_content'], "rating": int(float(user['review_rating'])), "id": user['restName']}
            user['reviews'] = {user['restName']:review}
            user['review_count'] = len(user['restaurants'].keys())
            for rest in user['restaurants'].values():
                rest['rating'] = int(float(rest['rating']))
        else:
            users.pop(user['user_id'])

            # new_poi['city']  = poi['city']
        # new_poi['country'] = poi['country']

with open('users-transformed.json','w') as new_users_file:
    json.dump(users, new_users_file)

