$(document).ready(function(){
    $('input').each(function(i, el) {
        $(this).prop("disabled", true);
    })
    $(':checkbox').each(function(i, el) {
        $(this).prop("disabled", false);
    })
     $("#srch-term").prop("disabled", false);

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

    //var rangeSlider = document.getElementById('slider-range');

    function createSlider(element) {
        var slider = noUiSlider.create(element, {
            start: 0.50,
            range: {
                'min': 0,
                'max': 1
            }
        });

       slider.on('slide', function( values, handle ) {
            // on change of the slider, find the next element and set its value
            console.log(event.target);
            $(event.target).closest('.slider').next().text(values[handle]);
            $(event.target).closest('.slider').next().next().val(values[handle]);
        });

    }

    $(".slider").each(function(index, element) {
        createSlider(element);
    })


    $(':checkbox').change(function() {
        var input = $(this).closest('.row').find('input');
        if($(this).is(":checked")) {
            input.prop("disabled", false);
        }
        else {
            input.prop("disabled", true);
        }
        $(this).prop("disabled", false); // jeez

    }); 

    $('#searchForm').on('submit', function() {

        console.log($("#date_input").val());
         if ($("#srch-term").val() == "") 
            return false;
        if ( $("#checkbox-date").is(":checked") &&  $("#date_input").val() == "")
            return false;
        if ( $("#checkbox-views").is(":checked") &&  $("#views").val() == "")
            return false;
        if ( $("#checkbox-duration").is(":checked") &&  $("#duration").val() == "")
            return false;
     });

});