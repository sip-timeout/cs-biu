"""Generate.

Usage:
  YelpDataExtractor.py -m <mode> [-u <num_of_users>]

Options:
  -h --help     Show this screen.
  -m <mode>  Available modes: quality,prediction
  -u <num_of_users> number of users for quality tests

"""

from docopt import docopt
from YelpDB import YelpDB


def get_restaurants_dict(user_reviews):
    rest_dic = dict()
    for review in user_reviews:
        rest_dic[review['rest_id']] = {'rating': review['review_rating']}
    return rest_dic


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
                        restaurants[rest] =



if __name__ == "__main__":
    main()
