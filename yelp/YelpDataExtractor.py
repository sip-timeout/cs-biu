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
    rest['restaurant-features'] = list()
    for name, val in rest_db_obj['attributes']:
        if isinstance(val, int) and val > 0:
            rest['restaurant-features'].append("_".join([name, val]))
        elif val.startswith('{'):
            val_as_dic = ast.literal_eval(val.replace('false','False').replace('true','True'))
            for key in val_as_dic:
                if val_as_dic[key]:
                    rest['restaurant-features'].append("_".join([name, key]))
        else:
            rest['restaurant-features'].append("_".join([name, val]))

    return rest


def main():
    args = docopt(__doc__)
    mode = args['-m']

    users = dict()
    restaurants = dict()

    with YelpDB() as db:
        if mode == 'quality':
            num_of_users = int(args['-u'])
            for user in db.get_users(num_of_users):
                user['restaurants'] = get_restaurants_dict(db.get_user_reviews(user['user_id']))
                for rest in user['restaurants']:
                    if rest not in restaurants:
                        restaurants[rest] = get_rest_details(db, rest)
                        print restaurants[rest]


if __name__ == "__main__":
    main()
