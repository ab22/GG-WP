var app = angular.module('yrylDashboard', []);

app.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.controller('DashboardCtrl', ['$scope', '$http', function($scope, $http){
    $scope.champions = [];
    $scope.summonerSpells = [];
    $scope.summonerSpells = [];
    $scope.menuOptions = [
        'Main',
        'Champions',
        'SummonerSpells'
    ];
    $scope.selectedOption = $scope.menuOptions[0];
    $scope.orderChampionsBy = 'name';
    $scope.orderSpellsBy = 'name';
    $scope.loadingChampions = false;
    $scope.loadingSpells = false;


    $scope.isActive = function(option){
        return option == $scope.selectedOption ? 'active' : '';
    };

    $scope.changeMenuOption = function(option){
        $scope.selectedOption = option;
    };

    $scope.getChampions = function(){
        $scope.loadingChampions = true;
        $http.get('/champions').success(function(champions){
            $scope.champions = champions;
            $scope.loadingChampions = false;
        });
    };

    $scope.getSummonerSpells = function(){
        $scope.loadingSpells = true;
        $http.get('/summoner_spells').success(function(summonerSpells){
            $scope.summonerSpells = summonerSpells;
            $scope.loadingSpells = false;
        });
    }
}]);
