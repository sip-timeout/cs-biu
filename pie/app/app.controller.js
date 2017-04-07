(function () {

    angular
        .module('app')
        .controller('AppController', [
            '$location', '$mdSidenav', '$mdBottomSheet', '$timeout', '$log',
            AppController
        ]);


    function AppController($location, $mdSidenav, $mdBottomSheet, $timeout, $log) {
        var vm = this;


        vm.stages = [
            {
                displayName: "Pick A Restaurant",
                route: "/restaurant"
            }
        ];
        vm.selected = vm.stages[0];
        vm.toggleMenu = toggleMenu;
        vm.selectStage = selectStage;
        vm.menuOpen = true;

        function toggleMenu() {
            vm.menuOpen = !vm.menuOpen;
        }

        /**
         * Select the current avatars
         * @param menuId
         */
        function selectStage(stage) {
            vm.selected = stage
            $location.path(stage.route);
        }


    }

})();
