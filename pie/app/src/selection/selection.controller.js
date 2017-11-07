(function () {
    "use strict";
    angular.module('selection')
        .controller('selectionController', ['selectionService', '$scope', '$filter', '$routeParams', '$location', '$anchorScroll', '$timeout', selectionController]);

    function selectionController(selectionService, $scope, $filter, $routeParams, $location, $anchorScroll, $timeout) {
        var vm = this;
        vm.restName = $routeParams['restName'];
        vm.selectionCriteria = [];
        vm.selection = {'users': []};
        // vm.selection = selectionService.getRestaurantUsers(vm.restName, vm.selectionCriteria);
        // vm.prediction = selectionService.getPrediction(vm.restName, vm.selectionCriteria);
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
            var oldSelection = vm.selection.users.slice().map(function (user) {
                return user.user;
            });
            vm.selection = selectionService.getRestaurantUsers(vm.restName, vm.selectionCriteria);
            vm.selection.$promise.then(function (selection) {
                if (oldSelection.length > 0) {
                    _.forEach(vm.selection.users, function (user) {
                        if (_.findIndex(oldSelection, {'name': user.user.name}) < 0) {
                            user.new = true;
                        }
                    });
                }

                vm.autoItems = _.map(selection.rest_categories, function (cat) {
                    return {originalCat: cat, display: $filter('category')(cat)};
                });
            });

            vm.prediction = selectionService.getPrediction(vm.restName, vm.selectionCriteria);
        };

        vm.search = function (query) {
            return _.filter(vm.autoItems, function (cat) {
                var substrIndex = cat.display.includes(":") ? cat.length : cat.display.search(',');
                return cat.display.toLowerCase().substring(0, substrIndex).includes(query.toLowerCase());
            });
        };

        $scope.$watchCollection('ctrl.selectionCriteria', function (newVal) {
            if (newVal && newVal.length === 0) {
                vm.refine();
            }
        });
    }

})();