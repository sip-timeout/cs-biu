(function () {
    "use strict";
    angular.module('selection')
        .filter('category', categoryFilter);

    function categoryFilter() {
        return function (category) {
            return category[0];
        };

    }

})();