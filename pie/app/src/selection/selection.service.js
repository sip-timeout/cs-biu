(function () {
    'use strict';

    angular.module('selection')
        .service('selectionService', ['$q', '$resource', selectionService]);


    function selectionService($q, $resource) {
        var selectionRes = $resource('http://localhost:5000/selection/:restName', {}, {post: {method: 'POST'}});
        var predictionRes = $resource('http://localhost:5000/selection/:restName/prediction', {}, {post: {method: 'POST'}});
        var categoryRes = $resource('http://localhost:5000/selection/:restName/category_analysis/:categoryName', {}, {post: {method: 'POST'}});

        function createSearchCriteriaObject(searchCrit) {
            var searchObj = {'forbidden_cats': [], 'dislike_cats': [], 'required_cats': [], 'like_cats': []};
            searchCrit.forEach(function (category) {
                searchObj[category[2] + '_cats'].push(category[0]);
            });
            return searchObj;
        }

        // Promise-based API
        return {
            getRestaurantUsers: function (restName, searchCrit) {
                return selectionRes.post({restName: restName}, createSearchCriteriaObject(searchCrit));
            },
            getPrediction: function (restName, searchCrit) {
                return predictionRes.post({restName: restName}, createSearchCriteriaObject(searchCrit));
            },
            getCategoryAnalysis: function (restName, categoryName, searchCrit) {
                return categoryRes.post({
                    restName: restName,
                    categoryName: categoryName
                }, createSearchCriteriaObject(searchCrit));
            }
        };
    }

})();
