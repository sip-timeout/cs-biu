(function () {
    angular.module('selection')
        .directive('coverageChip', function () {
            return {
                restrict: 'A',
                link: function (scope, elem, attrs) {
                    var chipInSelection = scope.$chip[1];
                    var mdChip = elem.parent().parent();
                    mdChip.addClass(chipInSelection ? 'in-selection' : 'not-in-selection');
                }
            };
        });
})();