$(document).ready(function(){
	
	//smooth transitions
	$('#frame').fadeIn('slow');
	
	//enables onscreen keyboard
	$(function(){
		$('.ui-keyboard-input').keyboard();
	});
	
	//enables tabs
    $(function() {
      $( "#tabs" ).tabs();
    });

	//generate forms to put in calibration data and categories
	gentable(5,5,"spot","calibrationForm",1,"calibrationtable");
	gentable(5,5,"cat","categoryForm",1,"categorytable");
	
	for(var i=0;i<25;i+=1){
		$('#spot'+pad(i,2)).attr('class',"ui-keyboard-input ui-widget-content ui-corner-all");
		$('#spot'+pad(i,2)).attr('aria-haspopup',"true");
		$('#spot'+pad(i,2)).attr('role',"textbox");
	}
	
	//fill the forms
	fillform(ipGet('experiment.calibration'),"spot",25)	
	fillform(ipGet('experiment.categoryMap'),'cat', 25)
	// load camera values
	$("#shutterspeed").val(ipGet('camera.shutter_speed'));
	$("#iso").val(ipGet('camera.iso'));
	
	//adding delete element to be able to efficiently delete categories 
	x = $("<td>Delete</td>");
	x.data("value", "");
	$("#availableCategories").append(x);
	

	/*adds a additional category to the available categories element
	 *@param val	the value and name of the appended category
	*/
	function addCategory(val) {
		x = $("<td>"+val+"</td>");
		x.data("value", val);
		$("#availableCategories").append(x);
		
	};	

	/*used to efficiently fill in categories into the form:
	 *a selected element will copy its value into the clicked input field
	*/
	function inpclick() {
		var x;
		
		$("#availableCategories .ui-selected").each(function(){
			x=$(this).data("value");
		})
		
		this.value=x;
	};
	
	//if a selectable element is selected, the input fields change value to the value of the selected element by clicking on the input fields
	$(function() {
		$( "#availableCategories" ).selectable({
			stop: function(){
				var elements = $("#categoryForm .input");
				$.each(elements, function(i, val){
					val.onfocus = inpclick;
				});
			}			 
		});
    });	
	
	//calls addcategory fucntion when button is clicked
	$("#categorybutton").click(function() {

		addCategory($('#categoryinput').val());
	});

	$("#clearcat").click(function() {
		for(var i=0; i<25; i+=1){
			$('#cat'+pad(i,2)).val("");
		}
	});
	
	$("#clearcal").click(function() {
		for(var i=0; i<25; i+=1){
			$('#spot'+pad(i,2)).val("");
		}
	});
});

function save(){
	var data = $('#calibrationForm').serializeArray();
	//send POST to server. data: the new calibration settings
 	ipSet('calibrate', data);
	
	var data = $('#categoryForm').serializeArray();
	//send POST to server. data: the new category settings
 	ipSet('categories', data);
	
	var data = $('#iso').val();
	//send POST to server. data: the new camera settings
 	ipSet('camera.iso',data);
	
	var data = $('#shutterspeed').val();
	//send POST to server. data: the new camera settings
 	ipSet('camera.shutter_speed',data);
	
	var data = document.getElementById("timeId").value;
	//send POST to server. data: the new time and date settings
 	ipSet('time', data);
}

