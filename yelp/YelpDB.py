import MySQLdb
from MySQLdb.cursors import DictCursor
from MySQLdb.cursors import Cursor


class YelpDB:
    def __init__(self):
        self.procedures = {
            "get_rests":
                """ 
                select b.id from restaurant b where 
                review_count > {0}
                order by review_count desc
                limit {1};
                 """
            ,
            "get_rest_users":
                """
                    select u.id as user_id,u.name,DATE_FORMAT(u.yelping_since,'%d-%m-%Y') as yelping_since,u.useful,u.funny,u.cool,u.fans,
                     urc.review_count
                    from user u, user_review_count urc, 
                      where u.id = urc.id
                    
                """
            ,
            "get_users":
                """
                    select u.id as user_id,u.name,DATE_FORMAT(u.yelping_since,'%d-%m-%Y') as yelping_since,u.useful,u.funny,u.cool,u.fans,
                     urc.review_count
                    from user u, user_review_count urc
                      where u.id = urc.id
                    order by review_count desc
                    limit {0}
                """
            ,
            "get_reviews":
                """
                select r.text as review_content ,r.stars as review_rating,DATE_FORMAT(r.date,'%d-%m-%Y') as review_date,u.id as user_id,
                       u.name,DATE_FORMAT(u.yelping_since,'%d-%m-%Y') as yelping_since,urc.review_count,u.useful,
                       u.funny,u.cool,u.fans  
                from review r, user u  , user_review_count urc
                where business_id='{0}'
                and r.user_id=u.id
                and r.user_id = urc.id
                """
            ,
            "get_user_reviews":
                """
                select r.stars as review_rating,r.business_id as rest_id
                from review r, restaurant rest
                where r.business_id = rest.id
                and r.user_id = '{0}'
                """
            ,
            "get_rest_info":
                """
                select id,name,city,state as country,postal_code,topics from restaurant where id  = '{0}'
                """
            ,
            "get_rest_categories":
                """
                select category from category where business_id = '{0}'
                """
            ,
            "set_rest_topics":
                """
                update restaurant set topics = '{1}' where id = '{0}'
                """
            ,
            "get_rest_attributes":
                """
                select name,value from attribute
                    where business_id= '{0}'  
                    and name in (
                    'RestaurantsPriceRange2',
                    'GoodForMeal',
                    'RestaurantsGoodForGroups',
                    'NoiseLevel',
                    'RestaurantsAttire',
                    'OutdoorSeating',
                    'Ambience',
                    'GoodForKids',
                    'RestaurantsTableService',
                    'Music',
                    'HappyHour',
                    'GoodForDancing',
                    'RestaurantsCounterService',
                    'DietaryRestrictions'
                    )
                """
        }
        self.conn = MySQLdb.connect(user='root', db='yelp_db')

    def close(self):
        self.conn.close()

    def __perform_query__(self, name, cur_type, *params):
        query_str = self.procedures[name].format(*params)
        cur = self.conn.cursor(cur_type)
        cur.execute(query_str)
        return cur.fetchall()

    def update_restaurant_topics(self, rest_id, topics):
        self.__perform_query__('set_rest_topics', DictCursor, rest_id, topics)
        self.conn.commit()

    def get_rests(self, review_threshold, limit):
        return [rest[0] for rest in self.__perform_query__("get_rests", Cursor, review_threshold, limit)]

    def get_rest_reviews(self, rest_id):
        reviewing_users = self.__perform_query__("get_reviews", DictCursor, rest_id)
        for user in reviewing_users:
            user['reviews'] = dict()
            review = dict()
            review['id'] = rest_id
            review['rating'] = user.pop('review_rating')
            review['content'] = user.pop('review_content')
            review['date'] = user.pop('review_date')
            user['reviews'][rest_id] = review
        return reviewing_users

    def get_users(self, limit):
        return self.__perform_query__("get_users", DictCursor, limit)

    def get_user_reviews(self, user_id):
        return self.__perform_query__("get_user_reviews", DictCursor, user_id)

    def get_rest_details(self, rest_id):
        return {
            'info': self.__perform_query__('get_rest_info', DictCursor, rest_id),
            'category': self.__perform_query__('get_rest_categories', Cursor, rest_id),
            # 'attributes': self.__perform_query__('get_rest_attributes', Cursor, rest_id)
        }
