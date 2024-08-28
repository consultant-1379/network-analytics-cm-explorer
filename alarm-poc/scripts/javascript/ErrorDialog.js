# ********************************************************************
# Ericsson Inc.                                                 SCRIPT
# ********************************************************************
#
#
# (c) Ericsson Inc. 2019 - All rights reserved.
#
# The copyright to the computer program(s) herein is the property
# of Ericsson Inc. The programs may be used and/or copied only with
# the written permission from Ericsson Inc. or in accordance with the
# terms and conditions stipulated in the agreement/contract under
# which the program(s) have been supplied.
#
# ********************************************************************
# Name    : ErrorDialogs.js
# Date    : 05/09/2019
# Revision: 1.0
# Purpose : Creates modal dialogs for any errors when deleting an alarm
#
# Usage   : PM Alarms
#


$("#deleteBtn").click(function() {
	AlarmState = $("#ErrorInput").first().text().trim();
	isMarked = $("#isMarked").first().text().trim();
	console.log("Wot it is homie: "+isMarked)
	console.log("Alarm state: "+AlarmState)
	if(isMarked=="True"){
		if(AlarmState=="Inactive"){
			createConfirmDeleteDialog()
		}else{
			createNotInactiveDialog()
		}
	}
	else{
		createNoMarkingsConfirmDialog()
	}
});
  
  
  
  
function createConfirmDeleteDialog(){
	$( "#dialog-confirm" ).dialog({
      resizable: false,
      height: "auto",
      width: 400,
      modal: true,
	  draggable: false,
      buttons: {
        "Delete alarm": function() {
          $( this ).dialog( "close" );
		  $("#deleteBtnInput input").val('Other').blur();
        },
        Cancel: function() {
          $( this ).dialog( "close" );
        }
      }
    });
}

function createNotInactiveDialog(){ 
   $( "#dialog-error" ).dialog({
      resizable: false,
      height: "auto",
      width: 400,
      modal: true,
	  draggable: false,
      buttons: {
        "OK": function() {
          $( this ).dialog( "close" );
        }
      }
    });
}

function createNoMarkingsConfirmDialog(){ 
   $( "#dialog-noMarkings" ).dialog({
      resizable: false,
      height: "auto",
      width: 400,
      modal: true,
	  draggable: false,
      buttons: {
        "OK": function() {
          $( this ).dialog( "close" );
        }
      }
    });
}