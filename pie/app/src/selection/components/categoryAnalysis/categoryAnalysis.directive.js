(function () {

    var app = angular.module('selection');

    app.directive('categoryAnalysis', ['selectionService', function () {

        var controller = function ($scope, selectionService) {

            var vm = this;

            vm.series = ['Selection Users','All Users'];

            $scope.$watch('vm.category', function (newVal) {
                if (newVal) {
                    var analysis = selectionService.getCategoryAnalysis(vm.poi, vm.category);
                    analysis.$promise.then(function (analysis) {
                        vm.data = [analysis.selection_dist, analysis.total_dist];
                        vm.labels=_.range(1,analysis.selection_dist.length+1);
                    });
                }
            });

        };

        return {
            restrict: 'E', //Default for 1.3+
            scope: {
                category: '=',
                poi: '='
            },
            controller: controller,
            controllerAs: 'vm',
            bindToController: true, //required in 1.3+ with controllerAs
            templateUrl: 'src/selection/components/categoryAnalysis/categoryAnalysis.html'
        };
    }]);

}());