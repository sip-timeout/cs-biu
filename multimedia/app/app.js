(function () {
    angular
        .module('app', ['ngMaterial', 'puppy','ngRoute','ngResource','chart.js'])
        .config(function ($mdThemingProvider, $mdIconProvider, $routeProvider,$locationProvider) {

            $mdIconProvider
                .defaultIconSet("./assets/svg/avatars.svg", 128)
                .icon("menu", "./assets/svg/menu.svg", 24)
                .icon("logo", "./assets/svg/logo.svg")
                .icon("share", "./assets/svg/share.svg", 24);

            $mdThemingProvider.theme('default')


            $routeProvider.when("/adoption", {
                templateUrl: "src/adoption/adoption.html"
            }).when("/puppy", {
                templateUrl: "src/puppy/puppy.html",
                controller: "puppyController",
                controllerAs: "vm"
            }).when("/training", {
                templateUrl: "src/training/training.html"
            }).otherwise({
                redirectTo:'/adoption'
            });


        });


})();