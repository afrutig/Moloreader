//this file contains all shared functions

//disables caching
$.ajaxSetup({ cache: false });

/*zeropadding recursive, pads to n digits
 *@param str 	the string to be padded
 *@param n		number of digits the string is padded to with zeros
 *@returns		the padded string
*/
function pad (str, n) {
  str = str.toString();
  return str.length < n ? pad("0" + str, n) : str;
}


/*fills a specified table with data
 *@param data 		the table will be filled with the elements of data
 *@param str		the id of the table elements to be filled. (#str00, #str01, #str02, ...)
 *@param maxelem	the maximum element number of the filled elements ( for example: str24)
*/
function filltable(data, str, maxelem){
	for(i=0; i<maxelem; i++){
		if (data[i]==undefined||data[i]==""){
			document.getElementById(str+pad(i,2)).innerHTML="-";
		}
		else{
			document.getElementById(str+pad(i,2)).innerHTML=data[i];
		}	
	}	
}

/*fills a specified form with data
 *@param data 		the form will be filled with the elements of data
 *@param str		the id of the form elements to be filled. (#str00, #str01, #str02, ...)
 *@param maxelem	the maximum number of the filled elements ( for example: str24)
*/
function fillform(data, str, maxelem){
	for(i=0; i<maxelem; i++){
		if (data[i]==undefined){	
			document.getElementById(str+pad(i,2)).value="";
		}
		else{
			document.getElementById(str+pad(i,2)).value=data[i];
		}	
	}
}


/*loads a html file from the server into the frame divison
 *@param url	the url of the html file 
*/
function loadhtml(url){
  	$.ajax({
          type: "GET",
          url: url,
          dataType: "html",
          success: function(data) {
	 	        $("#frame").html(data);
		   } 			   
	   });	
}



/*generates a table or a form with a specified number of elements a puts it into a division
 *@param n				number of rows
 *@param m				number of collumns
 *@param strID			name and id of the table/form elements (padded)
 *@param bodyID			table/form will be appended to the divison with id=bodyID
 *@param formbool		if true, a form with inputs will be generated, else just a table
 *@param tableclass		the class of the whole table
*/
function gentable(n, m, strID, bodyID, formbool, tableclass){
    var frame = document.getElementById(bodyID);
	var table = document.createElement("table");
	var tablebody = document.createElement("tbody");
	var count = 0;
	for (var i = 0; i < n; i++) {

		var row = document.createElement("tr");
 
		for (var j = 0; j < m; j++) {
			
        	var elem = document.createElement("td");
			
			if(formbool){
				table.className = tableclass;
				var inp = document.createElement("input");
				inp.name = strID+pad(count,2);
				inp.value = "";
				inp.id=strID+pad(count,2);
				inp.className = "input"
				elem.appendChild(inp);
				row.appendChild(elem);
			}
		
			else{
					table.className = "table table-bordered "+tableclass;
					elem.id=strID+pad(count,2);
					row.appendChild(elem);				
			}
			count+=1;	
		}
   		tablebody.appendChild(row);
	}
	table.appendChild(tablebody);
 	frame.appendChild(table);
}
