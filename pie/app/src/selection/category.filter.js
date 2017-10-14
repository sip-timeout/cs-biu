(function () {
    "use strict";
    angular.module('selection')
        .filter('category', categoryFilter);

    var catTypesFullName = {
        "avg": "Average Rating",
        "liked": "Liked",
        "visit": "Visited"
    };

    var bucketName = {
        "1": "Low",
        "2": "Medium",
        "3": "High",
        "4":"Very High"
    };
    var cuisineFullName = {
        "md": "Mediterranean",
        "eur": "European",
        "glut": "Gluten Free",
        "me": "Middle Eastern",
        "veg": "Vegetarian",
        "na": "North American",
        "it": "Italian",
        "sf": "Seafood",
        "bar": "Bar",
        "as": "Asian",
        "fr": "French",
        "cafe": "Cafe",
        "int": "International",
        "soup": "Soup",
        "pizz": "Pizza",
        "ff": "Fast Food",
        "lat": "Latin",
        "kosh": "Kosher",
        "fus": "Fusion",
        "cont": "Contemporary",
        "car": "Caribbean",
        "del": "Delicatessen",
        "af": "African",
        "ocn": "Oceania",
        "gr": "Grill"

    };

    function categoryFilter() {
        return function (category) {
            var catParts = category[0].split("_");

            switch (catParts.length){
                case 2:
                    return category[0].replace("_",": ").replace(/\b\w/g, function(l){ return l.toUpperCase();});
                case 4:
                    var catName = catParts[1] === "cuisine" && cuisineFullName[catParts[0]] ? cuisineFullName[catParts[0]] : catParts[0];
                    return catName + ", " + catTypesFullName[catParts[2]] + " (" + bucketName[catParts[3]] + " Score)";
            }
        };

    }

})();