import MySQLdb


class YelpDB:
    def __init__(self):
        self.procedures = {
            "get_rests":
                """ 
                select b.id,b.name from business b where 
                review_count > {0}
                and 'Restaurants' in ( select c.category from category c where c.business_id = b.id)
                order by review_count desc
                limit {1};
                 """
            ,
            "get_users":
                """
                select u.id as user_id,u.name,u.review_count,u.yelping_since,u.useful,u.funny,u.cool,u.fans  
                from user u  
                order by u.review_count
                limit {0}
                """
            ,
            "get_reviews":
                """
                select r.text as review_content ,r.stars as review_rating,r.date as review_date,u.id as user_id,u.name,u.review_count,u.yelping_since,u.useful,u.funny,u.cool,u.fans  
                from review r, user u  
                where business_id='{0}'
                and r.user_id=u.id
                """
            ,
            "get_user_reviews":
                """
                select r.stars as review_rating,r.business_id as rest_id
                from review r
                where 'Restaurants' in ( select c.category from category c where c.business_id = r.business_id)
                and r.user_id = {0}
                """
        }

    def __enter__(self):
        self.conn = MySQLdb.connect(user='root', db='yelp_db')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def __perform_query__(self, name, *params):
        query_str = self.procedures[name].format(*params)
        cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(query_str)
        return cur.fetchall()

    def get_rests(self,review_threshold,limit):
        return self.__perform_query__("get_rests",review_threshold,limit)

    def get_rest_reviews(self,rest_id):
        return self.__perform_query__("get_reviews",rest_id)

    def get_users(self,limit):
        return self.__perform_query__("get_users",limit)

    def get_user_reviews(self,user_id):
        return self.__perform_query__("get_user_reviews",user_id)

    def get_rest_details(self,rest_id):
