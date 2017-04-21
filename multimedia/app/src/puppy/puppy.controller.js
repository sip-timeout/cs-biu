(function () {
    "use strict";
    angular.module('puppy')
        .controller('puppyController', PuppyController);
    function PuppyController() {
        var vm = this;


        vm.opts = {
            index: 0,
            history:false
        };

        vm.slides = [{
            src: 'src/puppy/assets/p1.jpg',
            w: 500, h: 500
        }, {
            src: 'src/puppy/assets/p2.jpg',
            w: 500, h: 500
        }, {
            src: 'src/puppy/assets/p3.jpg',
            w: 500, h: 500
        }, {
            src: 'src/puppy/assets/p4.jpg',
            w: 500, h: 500
        }, {
            src: 'src/puppy/assets/p5.jpg',
            w: 500, h: 500
        }, {
            src: 'src/puppy/assets/p6.jpg',
            w: 500, h: 500
        }, {
            src: 'src/puppy/assets/p7.jpg',
            w: 500, h: 500
        }, {
            src: 'src/puppy/assets/p8.jpg',
            w: 500, h: 500
        }];

        vm.showGallery = function (i) {
            if(angular.isDefined(i)) {
                vm.opts.index = i;
            }
            vm.open = true;
        };

        vm.closeGallery = function () {
            vm.open = false;
        };

    }

})();