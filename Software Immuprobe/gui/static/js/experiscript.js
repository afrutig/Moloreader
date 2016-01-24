$(document).ready(function(){
	
	//smooth transitions
	$('#frame').fadeIn('slow');	
	
	//enables tabs
	$(function() {
		$( "#tabs" ).tabs();
	});
	
	//enable dropdown
    $('.dropdown-toggle').dropdown();
	
	
	//disables downloads
	$("#tab4 .btn").addClass("disabled");
	
	//generate table to display measurement results
	gentable(5,5,"spot","tablediv",0,"resulttable");
	
	//if and experiment is already done, display it
	if(!ipGet("data.isnone")){
		display_results();		
	}
	
	
	$("#start_button").click(function(){
		progress(10);
		
		$("#outcome").html("Status: Measuring...");
		
		//upload existing ----
		if($("#radio_upload").is(':checked')){
			var formData = new FormData($('#file_upload_form')[0]);
			
			if ($("#file").value==""){
				$("#outcome").html("Status: no file selected");
				return false;
			}
			
			$("#outcome").html("Status: uploading...");
			
			//uploading experiment to server
			$.ajax({
				url: "/upload",
				type: 'POST',
				data: formData,
				success: function (response) {
					if(ipGet('experiment.iscalibrated')){
						$('#outcome').html('Status: '+response);
					}
					else{
						$('#outcome').html('Status: '+response+" , run with not enough calibration info");
					}
					display_results();
					progress(100);
				
					return true;
				},
				error: function (response) {
					
					progress(90);
					
					if(ipGet('experiment.iscalibrated')){
						$('#outcome').html('Status: '+response);
					}
					else{
						$('#outcome').html('Status: '+response+" , run with not enough calibration info");
					}
					return false;
				},
				cache: false,
				contentType: false,
				processData: false
			});
			return true;
			
		//make new experiment ----
		} else if($("#radio_capture").is(':checked')){
			if(ipGet('experiment.iscalibrated')){
				$('#outcome').html('Status: '+ipGet('measure.please'));
			}
			else{
				$('#outcome').html('Status: '+ipGet('measure.please')+" , run with not enough calibration info");
			}
			progress(100);
			display_results();
					
		} else {
			$("#outcome").html("Status: Please choose an option");
			return false;
		
		}	
	    return false;
	});

});

/*helper function to format the result
 *@param data	the list of data to be formated
 *@returns		the list of data formated to 3 digits after comma
*/
function datahelp(data){
	for(var i=0;i<25;i++){
		data[i]=data[i].toFixed(3);
	}
	return data;
}

/*updates the progress bar with the id progr to a new percentage
 *@param percentage		the percentage the progress bar is updated to
 *
*/
function progress(percentage){
	$("#progr").attr("aria-valuenow", percentage);
	$("#progr").html(percentage+"%");
	$("#progr").width(percentage+"%");
}

//overrides save function from caliscript
function save(){}

/*displays the results once the experiment is completed.
 *This includes:
 *filling the table with the numeric values
 *setting the sources of the images for the plots
 *enabling the downloads for the plots etc. 
*/
function display_results() {  
	if(ipGet('experiment.iscalibrated')){
		$("#tab4 .btn").removeClass("disabled");
		
		$("#plot_standard_curve").attr("src", "/results/plot?type=standard_curve&time="+(new Date().getTime()));
	}
	else{
		$("#tab4 .btn").removeClass("disabled");
		$("#standard_link").addClass("disabled");
	}
	
	$("#plot_overview").attr("src", "/results/plot?type=overview&time="+(new Date().getTime()));
	$("#plot_intensity").attr("src", "/results/plot?type=intensity&time="+(new Date().getTime()));
	$("#plot_categorized").attr("src", "/results/plot?type=categorized&time="+(new Date().getTime()));
	$("#plot_signal_to_noise").attr("src", "/results/plot?type=signal_to_noise&time="+(new Date().getTime()));
	
	filltable(datahelp(ipGet('data.results')),"spot",25,false);
}
