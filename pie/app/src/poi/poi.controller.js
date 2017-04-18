(function () {
    "use strict";
    angular.module('poi')
        .controller('poiController', ['poiService','$location', PoiController]);
    function PoiController(poiService,$location) {
        var vm = this;
        vm.pois = poiService.loadAllPois();

        vm.gotoPoi = function (poiName) {
            $location.path("/"+poiName+"/selection");
        };

    }

})();