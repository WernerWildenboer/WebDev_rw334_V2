$(document).ready(function() {
	
	//https://youtu.be/IZWtHsM3Y5A - AJAX using jQuery w.r.t python flask
	
	//$('form').on('submit', function(event) {
	//
	//	$.ajax({
	//		data : {
	//			name : $('#nameInput').val(),
	//			email : $('#emailInput').val()
	//		},
	//		type : 'POST',
	//		url : '/process'  //hier kom die .py file, miskien kan mens net 'n funksie hier probeer call
	//	})
	//	
	//	//.done is wanneer die ajax call complete is. 
	//	.done(function(data) {
	//
	//		if (data.error) {
	//			$('#errorAlert').text(data.error).show();
	//			$('#successAlert').hide();
	//		}
	//		else {
	//			$('#successAlert').text(data.name).show();
	//			$('#errorAlert').hide();
	//		}
	//
	//	});
	//
	//	event.preventDefault(); //prevent HTML from submitting the data and force it to use jQuery as defined here
	//
	//});

function answers() {
    var x = document.getElementById("answer_area");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

// //show dropdown jQuery equivalent.
// $("#dropdownBtn").click(function() {
// 	if($("#navDropdown").attr('class')) {

// 	}
// });

});

//show dropdown menu from index.html
function showDropdown() {
    var x = document.getElementById("navDropdown");
    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
    } else { 
        x.className = x.className.replace(" w3-show", "");
    }
}

