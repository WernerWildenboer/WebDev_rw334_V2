$(document).ready(function() {
	
	//show dropdown on home page.
	$("#dropdownBtn").click(function() {
		 var temp = $("#navDropdown");
		 if( !temp.hasClass("w3-show") ) {
			temp.addClass("w3-show").removeClass("w3-hide");
		 } else {
			temp.addClass("w3-hide").removeClass("w3-show");
		 }
	});

});
