(function () {
    'use strict';

    angular.module('selection')
        .service('selectionService', ['$q', '$resource', selectionService]);


    function selectionService($q, $resource) {
        var res = $resource('http://localhost:5000/selection/:restName');

        // Promise-based API
        return {
            getRestaurantUsers:function (restName) {
                return res.get({restName:restName});
            }
        };
    }

})();
