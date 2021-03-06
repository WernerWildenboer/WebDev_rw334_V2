

var getTopics_array=[];

$(document).ready(function() {
	
    	function getTopics() {

		}

	
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
    
	function replaceBookmarked() {
        
		$.get('/show_bookmarked').done(
		function(response) {
			$("#show_bookmarked").html(response);
            
		});
	}
	if ($("#show_topics").length) {
		replaceTopic();
	}
	if ($("#show_suggestions").length) {
		replaceSuggestions();
	}
    if ($("#show_bookmarked").length) {
       
		replaceBookmarked();
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
	function update(first) {
		var url = "/show_questions";
		if (first) {
			var loggedin = $('#loggedin').val();
			if (loggedin) {
				url += "/mainSignedInTime/10/qa";
			} else {
				url += "/mainSignedOutTime/10/qa";
			}
		} else {
			var order = $("select[name=order]").val();
			var amount = $("select[name=amount]").val();
			var loggedin = $('#loggedin').val();
			
			if (loggedin) {
				var frm = $("select[name=from]").val();
				var qa = $("select[name=qa]").val();
				if (frm = "main") {
					url += "/mainSignedIn" + order + "/" + amount + "/" + qa;
				} else {
					url += "/" + frm + order + "/" + amount + "/" + qa;
				}
			} else {
				url += "/mainSignedOut" + order + "/" + amount + "/qa";
			}
		}
		$.get(url).done(
		function(response) {
			$("#show_questions").html(response);
		});
	}
	if ($("#update").length) {
		update(true);
		$("#update").click(function() {
			update(false);
		});
	}
	
	if ($("#show_questions_profile").length) {
		var username = $("#show_questions_profile").html();
		$.get('/show_questions/userTime/1000/qa/'+ username).done(
		function(response) {
			$("#show_questions_profile").html(response);
		});
	}
	
	if ($("#show_questions_topic").length) {
		var username = $("#show_questions_topic").html();
		$.get('/show_questions/topicTime/1000/qa/'+ username).done(
		function(response) {
			$("#show_questions_topic").html(response);
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


function follow(username) {
	console.log(username);
   var url = "/search";
    url += username;
    
    
}
