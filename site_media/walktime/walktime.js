// Calculates distance and approximate walking time between any two points on campus.

/////////////////////////////
// Configuration variables //
/////////////////////////////
var $mainContainer = $("#walktime_main");
var $resultsDisplayContainer = $("#response");
var $startPoint = $("#StartPoint");
var $endPoint = $("#EndPoint");

// Default position is Doe Library
var defaultCoords = [37.87243,-122.25955,37.87243,-122.25955]; 

///////////////////////
// Utility functions //
///////////////////////

// If all four coords are available, calculate distance
var findDistance = function(coords) {
    
    if (coords && coords.length == 4) {
        // Get vals out of coords array and cast strings to floats
        lat1 = parseFloat(coords[0]);
        lon1 = parseFloat(coords[1]);
        lat2 = parseFloat(coords[2]);
        lon2 = parseFloat(coords[3]);

        var R = 6371; // Radius of the earth in km
        var dLat = (lat2-lat1).toRad();  // Javascript functions in radians
        var dLon = (lon2-lon1).toRad();
        var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1.toRad()) * Math.cos(lat2.toRad()) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        var d = R * c * 1000; // Distance in meters
        var distance = Math.round(d);

        return distance;
    };
};


var metersToMinutes = function(meters) {
    // Assuming avg walking speed of 5 foot/second = 91 meter/minute.
    // But you can never get there as the crow flies, so add 20% padding.

    meters = meters * 1.2;
    var minutes = Math.round(parseInt(meters)/91);
    return minutes;
};

var setToRad = function() {
    // Convert numeric degrees to radians 
    // (for older browsers lacking toRad() function in the Number lib)
    if (typeof(Number.prototype.toRad) === "undefined") {
        Number.prototype.toRad = function() {
            return this * Math.PI / 180;
        }
    };            
};


/////////////////////////
// Main View functions //
/////////////////////////

var showMainView = function() {
    $mainContainer.show();
};

// Convert all currently selected coords into a single array
var getStartEndPoints = function() {

    var latLong = $startPoint.val();
    var startPoint = latLong.split(',');
    latLong = $endPoint.val();
    var endPoint = latLong.split(',');            

    return [startPoint[0],startPoint[1],endPoint[0],endPoint[1]];
};

// Update all display text by obtaining coords and calculating distance.
var updateDisplayStrings = function(startfinish) {

    var coords = getStartEndPoints();
    var distance = findDistance(coords);

    if (startfinish == "start") {
        var selectlist = $startPoint;
    } else {
        var selectlist = $endPoint;
    };

    // First use regex to add commas to long numeric strings
    var distanceString = distance.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    $("#distance_text").text(distanceString);
    $("#minutes_text").text(metersToMinutes(distance));

    // Only show the response text if we have an actual distance
    if(isNaN(distance)){
      $resultsDisplayContainer.hide();
    } else {
      $resultsDisplayContainer.show();
    };
};

// Determine optimum zoom level for a distance between two points,
// so we can always show start and end points simultaneously on large map.
var getZoom = function(coords) {
    var distance = findDistance(coords);
    var zoom;

    if (distance >= 1000) {
        zoom = 16;
    } else if (distance > 500 && distance < 1000 ) {
        zoom = 17;
    } else {
        zoom = 18;
    };
    return zoom;
};

////////////////////
// Event Handlers //
////////////////////

// Update displayed strings when start or end selections change
var startUpdate = function(startend) {
    var coords = getStartEndPoints();
    var zoom = getZoom(coords);

    // Don't fire the map update if we don't have an end point (else we end up in the ocean!)
    if (coords[3] != undefined) {
        updateDisplayStrings(startend);
        updateLargeMapLink(coords,zoom);
    }
};

$startPoint.on("change", {startend: 'start'}, startUpdate);
$endPoint.on("change", {startend: 'end'}, startUpdate);        


// Update linked map image and footer URL on load or when coords change
// function updateLargeMapLink(newLat,newLong) {
var updateLargeMapLink = function(coords,zoom) {            
    var goToURL = 'http://maps.google.com/maps?saddr='+coords[0]+','+coords[1]+'&daddr='+coords[2]+','+coords[3]+'&l=en&dirflg=w&t=m&z='+zoom;
    $(".walktime_item_link").attr({href : goToURL});

    // Using the static maps image generator in the Google Maps API instead of iframe
    var imgURL = 'http://maps.googleapis.com/maps/api/staticmap?center='+coords[2]+','+coords[3]+'&zoom=16&size=200x200&maptype=roadmap&markers=color:blue%7C'+coords[2]+','+coords[3]+'&sensor=false';
    $("#walktime_googleimg").attr({src : imgURL});
};

/////////////////////////////
// Initialization function //
/////////////////////////////

/**
 * Initialization function DOCUMENTATION
 */
var doInit = function () {

    // Make sure all browsers have access to the ToRad() func
    setToRad();
    
    // Initally hide the response text (until we have an actual distance to work with)
    $("#distance_text").text(0);
    $("#minutes_text").text(0);

    updateLargeMapLink(defaultCoords);

    // Read XML and draw select lists
    var select_string = '';
    $.ajax({
         type: "GET",
         url: "/static/walktime/map_coordinates.xml",
         dataType: "xml",
         success: function(xml) {
            $(xml).find('Locations').find('Location').each(function(){
                var Name = $(this).find('Name').text();
                var LatLong = $(this).find('Lat').text() + "," + $(this).find('Lon').text();
                var newOpt = '<option value="'+ LatLong +'">'+ Name +'</option>\n';
                select_string = select_string.concat(newOpt);
            });

            // Modify DOM selects just once for each list
            $startPoint.append(select_string);
            $endPoint.append(select_string);
        }
    });
    showMainView();
};

// run the initialization function when the widget object loads
doInit();
