(function () {
    "use strict";
    angular.module('poi')
        .controller('poiController', ['poiService', PoiController]);
    function PoiController(poiService) {
        var vm = this;
        vm.pois = poiService.loadAllPois();

    }

})();