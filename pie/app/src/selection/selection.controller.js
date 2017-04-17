(function () {
    "use strict";
    angular.module('selection')
        .controller('selectionController', ['selectionService','$routeParams', selectionController]);

    function selectionController(selectionService,$routeParams) {
        var vm = this;
        vm.restName = $routeParams['restName'];
        vm.selection=  selectionService.getRestaurantUsers(vm.restName);

        vm.selectCategory = function (category) {
            vm.selectedCategory = category;
        };
    }

})();