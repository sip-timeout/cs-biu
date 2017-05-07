(function () {
    "use strict";
    angular.module('selection')
        .controller('selectionController', ['selectionService', '$routeParams', '$location', '$anchorScroll', '$timeout', selectionController]);

    function selectionController(selectionService, $routeParams, $location, $anchorScroll, $timeout) {
        var vm = this;
        vm.restName = $routeParams['restName'];
        vm.selection = selectionService.getRestaurantUsers(vm.restName);
        vm.prediction = selectionService.getPrediction(vm.restName);
        vm.predictionMode = false;
        vm.predictionLabels = _.range(0.5,5.5,0.5);

        vm.selectCategory = function (category) {
            vm.selectedCategory = category;
            $timeout(function () {
                $location.hash('catAnalysis');
                $anchorScroll();
                $location.hash(null);
            }, 10);
        };

        vm.togglePrediction = function () {
            vm.predictionMode = !vm.predictionMode;
        };
    }

})();