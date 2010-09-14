/*	
 *  Check the value of all the fields on the page, 
 *  if a value is changed launch an event that will check all the values again and update 
 *  the currently used rule for hiding and displaying fields.
 */

var inputs;

jQuery(document).ready(function($) {
	// Add a change handler to each input field
	inputs = $("[@name*='field']");
	inputs.change(function() {
		ajax();
	});
	ajax();
});

function ajax() {
	$.ajax({
		type: "GET",
		url: getTracURL(),
		data: getValues(),
		cache: false,
		dataType: 'xml',
		success: function(data) {
			showFields(data);
		}
	});
}

function getValues() {
	// Build the query string
	var values = "";
	inputs.each(function() {
		// The this.value property doesn't seem to work in IE for <select/> objects
		if ($.browser.msie) {
			var id = "field-" + this.name.substr(6);
			var fname = $("select#" + id + "").attr("name");

			if (this.name == fname) {
				var field = document.getElementById(id); 
				var val = field.options[field.selectedIndex].text;
				values += this.name.substr(6) + "=" + escape(val) + "&";
			} else {
				values += this.name.substr(6) + "=" + escape(this.value) + "&";
			}
		} else {
			values += this.name.substr(6) + "=" + this.value + "&";
		}
	});
	// Minus the last '&'
	return values.slice(0, -1);
}

function showFields(xml)
{	
	// Shows all the fields
	$("[@for*='field-']").parent().show();
	$("[@name*='field_']").parent().show();
	
	// Stores the values from xml doc to an array
	var arr = new Array();
	var i = 0;
	while (i < xml.getElementsByTagName("field").length)
		{
			value = xml.getElementsByTagName("field")[i].childNodes[0].nodeValue;
			arr[i] = value;
			i++;
		}

	// Hiding of the selected fields
	var i = 0;
	while (i<arr.length)
	{
		$("[@for*='" + arr[i] + "']").parent().hide();
		
		arr[i] = arr[i].substr(6);
		var temp = new String;
		temp = 'field_' + arr[i];
		arr[i] = temp;

		$("[@name*=" + arr[i] + "]").parent().hide();
		i++;
	}
}
