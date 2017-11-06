$(document).ready(function() {
	$("#refreshPageBtn").click(function(){
		location.reload();
	});
	refresh_page();
});
function refresh_page() {
	var url = "http://127.0.0.1:8080/dashboard";
	$.getJSON(url, function(data) {
		if (data['status'] == 'Error') {
			alert("Error: " + data['message']);
		} else
			for ( var tuple in data['message']) {
				create_div(data['message'][tuple]);
			}
	});
}

function create_div(tuple) {
	var attrs = ['request_id', 'customer_id', 'time_elapsed', 'status', 'driver_id'];
	var $div = $("<div>", {
		class : "dashboardLower"
	});
	
	for(val of attrs) {
		var value = tuple[val];
		if (value && val == 'time_elapsed') {
			seconds = parseInt(value);
			value = "";
			var days = Math.floor(seconds / (3600*24));
			seconds  -= days*3600*24;
			var hrs   = Math.floor(seconds / 3600);
			seconds  -= hrs*3600;
			var min = Math.floor(seconds / 60);
			seconds  -= min*60;
			if(days) { value += days + "days "; }
			if(hrs) { value += hrs + "hrs "; }
			if(min) { value += min + "min "; }
			if(seconds) { value += seconds + "sec"; }
		}
		if(!value) {
			value = 'None';
		}
		var $innerDiv = $("<div>", {
			class : "dashInner",
			html : value
		});
		//$innerDiv.append(tuple[attr]);
		$div.append($innerDiv);
	}
	$("#lowerDataDiv").append($div);
}