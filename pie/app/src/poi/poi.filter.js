(function () {
    "use strict";
    angular.module('poi')
        .filter('poi', poiFilter);

    function poiFilter() {
        return function (pois, query) {
            if (query) {
                return _.filter(pois, function (poi) {
                    var search_obj = {name:poi.name,cui:poi.cuisines}
                    return JSON.stringify(search_obj).toLowerCase().includes(query.toLowerCase());
                });
            }
            else {
                return pois;
            }

        }

    }

})();