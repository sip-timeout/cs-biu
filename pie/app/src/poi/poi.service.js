(function () {
    'use strict';

    angular.module('poi')
        .service('poiService', ['$q', '$resource', poiService]);


    function poiService($q, $resource) {
        var res = $resource('assets/pois.json', {}, {'get': {'isArray': true}});

        // Promise-based API
        return {
            loadAllPois: function () {
                return res.get();
            }
        };
    }

})();
