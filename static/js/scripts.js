$(document).ready(function() {
	
	//show dropdown on home page.
	$("#dropdownBtn").click(function() {
		 var temp = this.id;
		 if( !temp.hasClass("w3-show") ) {
			temp.addClass("w3-show").removeClass("w3-hide");
		 } else {
			temp.addClass("w3-hide").removeClass("w3-show");
		 }
	});
	function replaceTopic() {
		$.get('/show_topics').done(
		function(response) {
			$("#show_topics").html(response);
		});
	}
	if ($("#show_topics").length) {
		replaceTopic();
	}
});

function myProfileFunction(id) {
	var x = document.getElementById(id);
	if (x.className.indexOf("w3-show") == -1) {
		x.className += " w3-show";
		x.previousElementSibling.className += " w3-theme-d1";
	} else {
		x.className = x.className.replace("w3-show", "");
		x.previousElementSibling.className =
			x.previousElementSibling.className.replace(" w3-theme-d1", "");
	}
}
