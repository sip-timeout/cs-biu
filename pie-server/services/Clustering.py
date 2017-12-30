import numpy
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans


class KMeansCluster:
    def get_representatives(self, users, num_of_clusters):
        user_list = users.values()
        user_features = list()
        for user in user_list:
            features = dict()
            for feature_type in user['rest_features']:
                features.update(
                    {'_'.join([feature_type, key]): value for (key, value) in
                     user['rest_features'][feature_type].iteritems()})
            user_features.append(features)
        v = DictVectorizer(sparse=False)
        feature_matrix = v.fit_transform(user_features)
        kmeans = KMeans(n_clusters=num_of_clusters).fit_transform(feature_matrix)
        rep_indices = numpy.argmin(kmeans, axis=0)
        return [user_list[idx] for idx in rep_indices]
