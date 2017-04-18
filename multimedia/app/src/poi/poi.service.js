(function () {
    'use strict';

    angular.module('poi')
        .service('poiService', ['$q', '$resource', poiService]);


    function poiService($q, $resource) {
        var res = $resource('http://localhost:5000/rests', {}, {'get': {'isArray': true}});

        // Promise-based API
        return {
            loadAllPois: res.get
        };
    }

})();
