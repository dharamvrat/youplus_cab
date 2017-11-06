var driver_id = ""
$(document).ready(function() {
		var url_string = window.location.href;
		var url = new URL(url_string);
		driver_id = url.searchParams.get("id");
		if (driver_id && parseInt(driver_id) <= 5 && parseInt(driver_id) >= 1) {
			$('#driverPageHead').html("Driver App - driver id : " + driver_id);
			refresh_page();
		} else {
			alert("Please select a valid driver id");
			$("#mainDiv").hide();
		}
		$("#refreshPageBtn").click(function(){
			location.reload();
		});
});


function refresh_page(){
	var url = "http://127.0.0.1:8080/driver/" + driver_id;
	$.getJSON(url, function(data) {
		if (data['status'] == 'Error') {
			alert("Error: " + data['message']);
		} else
			create_div(data['message']);
	});
}

function create_div(tuple) {
	var disable_booking = false;
	for (var on of tuple['ongoing']) {
		disable_booking = true;
		var htmlTxt = "";
		htmlTxt += "Req. Id: " + on['request_id'];
		htmlTxt += "<br>Cust. Id: " + on['customer_id'];
		htmlTxt += "<br>Request: " + on['requested_min'] + " min ago";
		htmlTxt += "<br>Picked Up: " + on['pickup_min'] + " min ago";
		var $div = $("<div>", {
			class : "bubble",
			html : htmlTxt
		});
		$("#divOngoing").append($div)
	}
	for (var comp of tuple['completed']) {
		var htmlTxt = "";
		htmlTxt += "Req. Id: " + comp['request_id'];
		htmlTxt += "<br>Cust. Id: " + comp['customer_id'];
		htmlTxt += "<br>Request: " + comp['requested_min'] + " min ago";
		htmlTxt += "<br>Picked Up: " + comp['pickup_min'] + " min ago";
		htmlTxt += "<br>Completed: " + comp['completed_min'] + " min ago";
		var $div = $("<div>", {
			class : "bubble",
			html : htmlTxt
		});
		$("#divCompleted").append($div)
	}
	for (var wait of tuple['waiting']) {
		var htmlTxt = "";
		htmlTxt += "Req. Id: " + wait['request_id'];
		htmlTxt += "<br>Cust. Id: " + wait['customer_id'];
		htmlTxt += "<br>Request: " + wait['requested_min'] + " min ago";
		var $button = $("<button>",{
			text: "Select",
			id: wait['request_id'],
			class: 'bookRequestBtn button',
			disabled: disable_booking,
			click: book_request
		});
		var $btnDiv = $("<div>", {
			class : "requestBtnDiv"
		});
		$btnDiv.append($button);
		var $div = $("<div>", {
			class : "bubble",
			html : htmlTxt
		});
		$div.append($btnDiv);
		$("#divWaiting").append($div)
	}
}

function book_request() {
	var booking_id = $(this).attr('id');
	var url = "http://127.0.0.1:8080/driver/" + driver_id + "/" + booking_id;
	$.getJSON(url, function(data) {
		alert(data['status'] + ": " + data['message']);
	});
	location.reload();
}