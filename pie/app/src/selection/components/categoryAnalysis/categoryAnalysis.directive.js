(function () {

    var app = angular.module('selection');

    app.directive('categoryAnalysis', ['selectionService', function () {

        var controller = function ($scope, selectionService) {

            var vm = this;

            vm.series = ['Selection Users','All Users'];

            $scope.$watch('vm.category', function (newVal) {
                if (newVal) {
                    var analysis = selectionService.getCategoryAnalysis(vm.poi, vm.category,vm.criteria);
                    analysis.$promise.then(function (analysis) {
                        vm.data = [analysis.selection_dist, analysis.total_dist];
                        vm.labels=['Low Score','Medium Score','High Score']
                    });
                }
            });

        };

        return {
            restrict: 'E', //Default for 1.3+
            scope: {
                category: '=',
                poi: '=',
                criteria:'='
            },
            controller: controller,
            controllerAs: 'vm',
            bindToController: true, //required in 1.3+ with controllerAs
            templateUrl: 'src/selection/components/categoryAnalysis/categoryAnalysis.html'
        };
    }]);

}());