$(document).ready(function() {
	$("#rideNowBtn").click(function() {
		var customer_id = $("#CustomerId").val();
		if (customer_id) {
			var url = "http://127.0.0.1:8080/customer/" + customer_id;
			$.getJSON(url, function(data) {
				alert(data['status'] + " : " + data['message'])
			});
			$("#CustomerId").val('');
		} else {
			alert("Please enter a value for customer id");
		}
	});
});