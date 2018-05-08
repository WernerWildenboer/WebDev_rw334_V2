

var getTopics_array=[];

$(document).ready(function() {
	
    	function getTopics() {

		}
	
	//show dropdown on home page.
	$("#dropdownBtn").click(function() {
		 var temp = this.id;
		 if( !temp.hasClass("w3-show") ) {
			temp.addClass("w3-show").removeClass("w3-hide");
		 } else {
			temp.addClass("w3-hide").removeClass("w3-show");
		 }
	});
	
	//Home Page AJAX functions
	function replaceTopic() {
		$.get('/show_topics').done(
		function(response) {
			$("#show_topics").html(response);
		});
	}
	function replaceSuggestions() {
		$.get('/show_suggestions').done(
		function(response) {
			$("#show_suggestions").html(response);
		});
	}
	if ($("#show_topics").length) {
		replaceTopic();
	}
	if ($("#show_suggestions").length) {
		replaceSuggestions();
	}
	function dropDownTopics() {
    var x = document.getElementById("Demo");
    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
    } else { 
        x.className = x.className.replace(" w3-show", "");
    }
}
	// Home Page update questions function
	function update() {
		var frm = $("select[name=from]").val();
		var qa = $("select[name=qa]").val();
		var order = $("select[name=order]").val();
		var amount = $("select[name=amount]").val();
		var url = "/show_questions";
		if (frm = "main") {
			url += "/main"
		}
		$.get('/show_questions').done(
		function(response) {
			$("#show_questions").html(response);
		});
	}
	if ($("#update").length) {
		//update();
		$("#update").click(function() {
			update();
		});
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
