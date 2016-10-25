$(document).ready(function(){

	var locationPicker = $('#map').locationpicker({
        location: {
            latitude: 50.0755381,
            longitude: 14.4378005
        },
        radius: 0,
        zoom: 4,
        inputBinding: {
            latitudeInput: $('#lat'),
            longitudeInput: $('#lon'),
            locationNameInput: $('#address')
        }
    }).map;

    $('.link-advanced-filters').click(function(e) {
    	$(".advanced-filters").toggle();
		//locationPicker.autosize();
		//var map = $("#map")[0];
		var currentCenter = map.getCenter();
        google.maps.event.trigger(map, "resize");
       // map.setCenter(currentCenter); 
		e.preventDefault();
    // Do stuff
	});

});