(function () {
    "use strict";
    angular.module('selection')
        .controller('selectionController', ['selectionService', '$scope', '$routeParams', '$location', '$anchorScroll', '$timeout', selectionController]);

    function selectionController(selectionService, $scope, $routeParams, $location, $anchorScroll, $timeout) {
        var vm = this;
        vm.restName = $routeParams['restName'];
        vm.selectionCriteria = [];
        vm.selection = selectionService.getRestaurantUsers(vm.restName, vm.selectionCriteria);
        vm.prediction = selectionService.getPrediction(vm.restName, vm.selectionCriteria);
        vm.predictionMode = false;
        vm.predictionLabels = _.range(0.5, 5.5, 0.5);


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

        vm.addCriterion = function (category, type) {
            if (!_.find(vm.selectionCriteria, function (o) {
                    return o[0] === category[0];
                })) {
                var criteria = category.concat([type]);
                vm.selectionCriteria.push(criteria);
            }
        };

        vm.refine = function () {
            vm.selection = selectionService.getRestaurantUsers(vm.restName, vm.selectionCriteria);
            vm.prediction = selectionService.getPrediction(vm.restName, vm.selectionCriteria);
        };

        $scope.$watchCollection('ctrl.selectionCriteria', function (newVal) {
            if (newVal && newVal.length === 0) {
               vm.refine();
            }
        });
    }

})();