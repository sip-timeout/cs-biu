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
                displayName: "אימוץ",
                route: "/adoption"
            },
            {
                displayName: "גורות",
                route: "/puppy"
            },
            {
                displayName: "אילוף",
                route: "/training"
            },
            {
                displayName: "קריירת שירה",
                route: "/singing"
            },
            {
                displayName: "משחק בריחה",
                route: "/escape"
            }
        ];
        vm.selected = vm.stages[0];
        vm.toggleMenu = toggleMenu;
        vm.selectStage = selectStage;
        vm.isSelected = isSelected;
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

        function isSelected(stage){
            return $location.path() === stage.route;
        }


    }

})();
