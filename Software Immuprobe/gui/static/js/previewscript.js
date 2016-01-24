$(document).ready(function(){
	
	//smooth transitions
	$('#frame').fadeIn('slow');
	
	//enables onscreen keyboard
	$(function(){
		$('.ui-keyboard-input').keyboard();
	});
	
	
	$('#shutter_speed').val(ipGet("camera.shutter_speed"));
	
	reload_preview();
	
	$('#reload').click(function(){
		reload_preview();
	});
	
});

//overrides save function from caliscript
function save(){}


//reloads preview according to the settings
function reload_preview() {
	time = (new Date().getTime())
	shutter_speed = $('#shutter_speed').val();
	resolution = $('#resolution').val();
	light_color = $('#light_color').val();
	auto_exposure = $('#auto_exposure').is(':checked');
	preview_url = './camera/preview?time='+time+'&shutter_speed='+shutter_speed+'&resolution='+resolution+'&light_color='+light_color+'&auto_exposure='+auto_exposure;
	$('#preview #preview_image').attr('src', preview_url);
}