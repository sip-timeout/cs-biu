"""Generate.

Usage:
  YelpDataExtractor.py -m <mode> [-u <num_of_users>]

Options:
  -h --help     Show this screen.
  -m <mode>  Available modes: quality,prediction
  -u <num_of_users> number of users for quality tests

"""

import itertools
import ast
import json
import time
from docopt import docopt
from YelpDB import YelpDB


def get_restaurants_dict(user_reviews):
    rest_dic = dict()
    for review in user_reviews:
        rest_dic[review['rest_id']] = {'rating': review['review_rating']}
    return rest_dic


def get_rest_details(db, rest_id):
    rest_db_obj = db.get_rest_details(rest_id)
    rest = dict(rest_db_obj['info'][0])
    rest['cuisine'] = list(itertools.chain.from_iterable(rest_db_obj['category']))
    rest['cuisine'].remove('Restaurants')
    rest['cuisine'] = ','.join(rest['cuisine'])
    # rest['restaurant-features'] = list()
    # for name, val in rest_db_obj['attributes']:
    #     if val.startswith('{'):
    #         val_as_dic = ast.literal_eval(val.replace('false', 'False').replace('true', 'True'))
    #         for key in val_as_dic:
    #             if val_as_dic[key]:
    #                 rest['restaurant-features'].append("_".join([name, key]))
    #     elif val != '0':
    #         rest['restaurant-features'].append("_".join([name, val]))
    # rest['restaurant-features'] = ','.join(rest['restaurant-features'])

    return rest


def main():
    args = docopt(__doc__)
    mode = args['-m']

    users = dict()
    restaurants = dict()

    with YelpDB() as db:
        if mode == 'quality':
            num_of_users = int(args['-u'])
            i=0
            for user in db.get_users(num_of_users):
                i+=1

                user['restaurants'] = get_restaurants_dict(db.get_user_reviews(user['user_id']))
                for rest in user['restaurants']:
                    if rest not in restaurants:
                        restaurants[rest] = get_rest_details(db, rest)
                users[user['user_id']] = user
                print 'user',i

    with open('users_' + mode + '.json', 'w') as users_file:
        json.dump(users, users_file, encoding='latin1')

    with open('rests_' + mode + '.json', 'w') as rests_file:
        json.dump(restaurants, rests_file, encoding='latin1')

    print str(len(users)) + ' ' + str(len(restaurants))


if __name__ == "__main__":
    main()
