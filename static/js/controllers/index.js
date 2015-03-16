var app = angular.module('yrylApp', []);

app.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.controller('IndexCtrl', function($scope){
    $scope.selectedRegion = '';
    $scope.summonerName = '';
    var regionKey = 'na';
    var self = this;

    $scope.changeRegion = function(newRegion){
        $scope.selectedRegion = $scope.regions[newRegion];
        regionKey = newRegion;
    };

    $scope.search = function(){
        if($scope.summonerName === ''){
            return;
        }
        window.location = '/match/' + regionKey + '/' + $scope.summonerName;
    };

    $scope.$watch('regions', function(){
        $scope.selectedRegion = $scope.regions.na;
    });

});
