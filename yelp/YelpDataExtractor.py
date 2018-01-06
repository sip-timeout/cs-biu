"""Generate.

Usage:
  YelpDataExtractor.py -m <mode> [-u <num_of_users>] [-r <num_of_rests>] [-t <threshold>]

Options:
  -h --help     Show this screen.
  -m <mode>  Available modes: quality,prediction
  -u <num_of_users> number of users for quality tests
  -r <num_of_rests> number of rests for prediction tests
  -t <threshold> review threshold
"""

import itertools
import ast
import json
import time
from docopt import docopt
from YelpDB import YelpDB
from TripAdvisorScraper import TripAdvisorScraper


class YelpDataExtractor:
    def __init__(self):
        self.scraper = TripAdvisorScraper()
        self.users = dict()
        self.restaurants = dict()

    def __enter__(self):
        self.db = YelpDB()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __get_restaurants_dict__(self, user_reviews):
        rest_dic = dict()
        for review in user_reviews:
            rest_dic[review['rest_id']] = {'rating': review['review_rating']}
        return rest_dic

    def __get_rest_details__(self, rest_id, extract_topics=False):
        rest_db_obj = self.db.get_rest_details(rest_id)
        rest = dict(rest_db_obj['info'][0])
        rest['cuisine'] = list(itertools.chain.from_iterable(rest_db_obj['category']))
        rest['cuisine'].remove('Restaurants')
        rest['cuisine'] = ','.join(rest['cuisine'])
        if extract_topics:
            if not rest['topics']:
                rest['topics'] = self.scraper.get_restaurant_topics(rest['name'], rest['city'], rest['postal_code'])
                self.db.update_restaurant_topics(rest_id, rest['topics'])

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

    def __process_user__(self, user):
        user['restaurants'] = self.__get_restaurants_dict__(self.db.get_user_reviews(user['user_id']))
        for rest in user['restaurants']:
            if rest not in self.restaurants:
                self.restaurants[rest] = self.__get_rest_details__(rest)
        self.users[user['user_id']] = user

    def quality(self, num_of_users):
        i = 0
        for user in self.db.get_users(num_of_users):
            i += 1
            self.__process_user__(user)
            print i

    def prediction(self, num_of_rests, review_threshold):
        i = 0
        for rest in self.db.get_rests(review_threshold, num_of_rests):
            i += 1
            self.restaurants[rest] = self.__get_rest_details__(rest, True)
            for user in self.db.get_rest_reviews(rest):
                if user['user_id'] in self.users:
                    self.users[user['user_id']]['reviews'].append(user['reviews'][0])
                else:
                    self.__process_user__(user)
            print i


def main():
    args = docopt(__doc__)
    mode = args['-m']

    with YelpDataExtractor() as extractor:
        if mode == 'quality':
            extractor.quality(args['-u'])
        elif mode == 'prediction':
            extractor.prediction(args['-r'], args['-t'])

    with open('users_' + args['-m'] + '.json', 'w') as users_file:
        json.dump(extractor.users, users_file, encoding='latin1')

    with open('rests_' + args['-m'] + '.json', 'w') as rests_file:
        json.dump(extractor.restaurants, rests_file, encoding='latin1')

    print str(len(extractor.users)) + ' ' + str(len(extractor.restaurants))


if __name__ == "__main__":
    main()
