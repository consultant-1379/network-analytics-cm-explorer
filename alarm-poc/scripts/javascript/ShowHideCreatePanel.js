$( "#createBtn" ).click(function() {
  $( "#accordion" ).accordion({
		active: 0
	}
)
  $( "#saveAfterCreateBtn" ).css("display", "");
  $( "#saveAfterEditBtn" ).css("display", "none");
});

$( "#editBtn" ).click(function() {
  $( "#accordion" ).accordion({
		active: 0
	}
)
  $( "#saveAfterEditBtn" ).css("display", "");
  $( "#saveAfterCreateBtn" ).css("display", "none");
});

$("#cancelBtn").click(function() {
  $( "#accordion" ).accordion({
		active: 1
	}
)
});