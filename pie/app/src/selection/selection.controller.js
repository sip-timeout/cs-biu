(function () {
    "use strict";
    angular.module('selection')
        .controller('selectionController', ['selectionService','$routeParams', selectionController]);

    function selectionController(selectionService,$routeParams) {
        var vm = this;
        vm.selection=  selectionService.getRestaurantUsers($routeParams['restName']);

    }

})();