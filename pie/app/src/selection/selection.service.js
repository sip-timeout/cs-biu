(function () {
    'use strict';

    angular.module('selection')
        .service('selectionService', ['$q', '$resource', selectionService]);


    function selectionService($q, $resource) {
        var selectionRes = $resource('http://localhost:5000/selection/:restName');
        var categoryRes = $resource('http://localhost:5000/selection/:restName/category_analysis/:categoryName');

        // Promise-based API
        return {
            getRestaurantUsers:function (restName) {
                return selectionRes.get({restName:restName});
            },
            getCategoryAnalysis:function (restName,categoryName) {
                return categoryRes.get({restName:restName,categoryName:categoryName});
            }
        };
    }

})();
