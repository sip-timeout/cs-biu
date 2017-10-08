(function () {
    angular
        .module('app', ['ngMaterial', 'poi','selection','ngRoute','ngResource','chart.js'])
        .config(function ($mdThemingProvider, $mdIconProvider, $routeProvider) {

            $mdIconProvider
                .defaultIconSet("./assets/svg/avatars.svg", 128)
                .icon("menu", "./assets/svg/menu.svg", 24)
                .icon("required", "./assets/svg/required.svg", 16)
                .icon("forbidden", "./assets/svg/forbidden.svg", 16)
                .icon("like", "./assets/svg/like.svg", 16)
                .icon("dislike", "./assets/svg/dislike.svg", 16)
                .icon("logo", "./assets/svg/logo.svg")
                .icon("share", "./assets/svg/share.svg", 24)
                .icon("google_plus", "./assets/svg/google_plus.svg", 512)
                .icon("hangouts", "./assets/svg/hangouts.svg", 512)
                .icon("twitter", "./assets/svg/twitter.svg", 512)
                .icon("phone", "./assets/svg/phone.svg", 512);

            $mdThemingProvider.theme('default')

            $routeProvider.when("/restaurant", {
                templateUrl: "src/poi/poi.html",
                controller: "poiController",
                controllerAs: "ctrl"
            }).when("/:restName/selection", {
                templateUrl: "src/selection/selection.html",
                controller: "selectionController",
                controllerAs: "ctrl"
            }).otherwise({
                redirectTo: "/restaurant"
            });


        });
})();