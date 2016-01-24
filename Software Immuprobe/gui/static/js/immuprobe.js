// JS interface to immuprobe server

/**
 * Send a key-value pair to the immuprobe server.
 * Calls ipSet() in the back-end.
 * 
 * @param name	The name of the attribute.
 * @param data	The value to be sent to the server.
 * 
 * @returns	Returns true on success, an error message on failure.
 */
function ipSet(name, value) {
	data = {'name': name, 'value': value};
	data = JSON.stringify(data);
	var resp = null;
	$.ajax({
       	 	type: "POST",
			url: "/ipSet",
           	dataType: "JSON",
			contentType: "application/json",
			data: data,
			async: false,
			success: function(response) {
				resp = response;
				return response;
			},
			error: function(response) {
				alert('error: ipSet('+name+')');
				return false;
			}
		});
		
		return resp;
}

/**
 * Get a named value from the server.
 * Calls ipGet() in the back-end.
 * 
 * @params name	The name of the desired value.
 */
function ipGet(name) {
		data = {'name': name};
		data = JSON.stringify(data);
		var value = null;
		$.ajax({
       	 	type: "POST",
			url: "/ipGet",
           	dataType: "JSON",
			contentType: "application/json",
			data: data,
			async: false,
			success: function(response) {
				value = response;
				return response;
			},
			error: function(response) {
				alert('error: ipGet('+name+')');
				return false;
			}
		});
		
		return value;
}
