var app = angular.module('yrylApp', []);

app.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.controller('IndexCtrl', function($scope){
    $scope.selectedRegion = 'NA';
    $scope.summonerName = '';
    var regionKey = 'na';

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

});
