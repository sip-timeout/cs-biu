(function () {
    "use strict";
    angular.module('poi')
        .controller('poiController', ['poiService','$location','$rootScope', PoiController]);
    function PoiController(poiService,$location,$rootScope) {
        var vm = this;
        vm.pois = poiService.loadAllPois();

        vm.gotoPoi = function (poi) {
            $location.path("/"+poi.name+"/selection");
            $rootScope.selectedPOI = poi;
        };

    }

})();