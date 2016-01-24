$(document).ready(function(){
	
	//smooth transitions
	$('#frame').fadeIn('slow');
	
	//generate tables for overview on home screen
	gentable(5,5,"spot","calstatus",0,"hometable");
	gentable(5,5,"catspot","catspots",0,"hometable");
	
	//fill the tables and the camera status
	filltable(ipGet('experiment.calibration'),"spot",25);
	filltable(ipGet('experiment.categoryMap'),"catspot", 25);
	document.getElementById("camera").innerHTML="Shutterspeed: "+ipGet('camera.shutter_speed')+"<br>Iso: "+ipGet('camera.iso');	
	
	//start time in upper right corner
	function update() {
		var dat = new Date();
        var str = pad(dat.getHours(),2) + ":" + pad(dat.getMinutes(),2) + ":" + pad(dat.getSeconds(),2);
		var date = pad(dat.getDate(),2) + "-" + pad((dat.getMonth() + 1),2) + "-" + dat.getFullYear();
		document.getElementById("date").innerHTML=date;
		document.getElementById("time").innerHTML=str; 
        window.setTimeout(update, 1000);
	}
	update();
	
	//load the corresponding html document into the #frame <div> to avoid page reloading, save calibration if coming from calibration page
	$("#home").click(function(){
		if(typeof(save)=="function"){
			save();
		}
		$('#frame').hide();
	});
	  
	$("#calibratenav").click(function(){
		if(typeof(save)=="function"){
			save();
		}
		$('#frame').hide();
		loadhtml("static/html/calibration.html");
	});
	  
	$("#experinav").click(function(){
		if(typeof(save)=="function"){
			save();
		}
		$('#frame').hide();
		loadhtml("static/html/experiment.html");
	});
	
	$("#focusnav").click(function(){
		if(typeof(save)=="function"){
			save();
		}
		ipSet('camera.livestream', 0);	
	});
	
	$("#previewnav").click(function(){
		if(typeof(save)=="function"){
			save();
		}
		$('#frame').hide();
		loadhtml("static/html/preview.html");
	});
	
	$("#reset").click(function(){
		ipGet('reset');
		window.location.reload();
	});
	
		  	  
});