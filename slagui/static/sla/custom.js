	var rowNum = 0;
	var maxRowCount = 11;
	function removeRow (temp) {
		$('#rowNum'+temp).remove();
		$('#controlRowNum'+temp).remove();
		rowNum--;
		grRemoveRow(temp);
	};

	function addRow() {
		rowNum ++;
		
		$.get('monitoring_metrics?service=' + $("#tsid").val(),
			function (measurements) {
				
				if (measurements.length > 0) {
					if(rowNum < maxRowCount) {
						var row =
							'<div id="controlRowNum' + rowNum +'" class="control-group sla-hform">'
							
						row +=	'<div id="rowNum' + rowNum +'"sla class="sla-row" >' +
									'<div class="sla-label">' +
										'<label for ="sname'+rowNum+'">Name' + rowNum.toString() + ':</label>' +
									'</div>' + 
									'<select id="sname'+rowNum+'" name="sname'+rowNum+'">';
					
						for	(i = 0; i < measurements.length; i++) {
							row += 		'<option value="' + measurements[i][0] + '">' + measurements[i][1] + '</option>';
						}
						
						row +=
										'</select>' +
									'<input id="rowBtn'+rowNum+'" onclick="removeRow('+rowNum+');" type="button" value="Remove" class="btn">' +
								'</div>' +
							'</div>';
						$('#metrics div:last').before(row);
					}
					grAddRow(measurements);
				} else {
					if (rowNum == 1) {
						row =	
							'<div id="rowNum' + rowNum +'"sla class="sla-row" >' +
								'<p>No monitoring metrics available for ' + $("#tsid").val() + '<p>'
							'</div>';
						$('#metrics div:last').before(row);
					}
				}
			}
		)
		.fail(
			function() {
				alert( "error" );
			}
		);
	}


	var grRowNum = 0;
	var maxGrRowCount = 11;
	function grRemoveRow(temp) {
		$('#grRowNum'+temp).remove();
		grRowNum --;
	};

	function grAddRow(measurements) {
		grRowNum ++;
		if(grRowNum <maxGrRowCount) {
			var row =
				'<div id="grRowNum' + grRowNum +'" >' +
					'<div class="sla-hform">' +
						'<div class="sla-row">' +
							'<div class="sla-label">' +
								'<label class="col-sm-2 control-label" for="gname'+grRowNum+'" >G.Name' + grRowNum + ':</label>' +
							'</div>' + 
							'<div class="col-sm-10">' +
								'<select class="form-control-static" id="gname'+grRowNum+'" name="gname'+grRowNum+'">';
			
			for	(i = 0; i < measurements.length; i++) {
				row += 				'<option value="' + measurements[i][0] + '">' + measurements[i][1] + '</option>';
			}
			
			row +=
								'</select>' +
							'</div>' +
						'</div>' +
					'</div>' +
					'<div class="sla-hform">' +
						'<div class="sla-row">' +
							'<div class="sla-label">' +
								'<label class="col-sm-2 control-label" style="display: inline" for="cons'+grRowNum+'">Constraints:</label>' +
							'</div>' + 
							'<div class="col-sm-10">' +
								'<select id="cons'+grRowNum+'" name="cons'+grRowNum+'">' +
									'<option value="GT">GT</option>' +
									'<option value="GE">GE</option>' +
									'<option value="EQ">EQ</option>' +
									'<option value="LT">LT</option>' +
									'<option value="LE">LE</option>' +
									'<option value="NE">NE</option>' +
									'<option value="BETWEEN">BETWEEN</option>' +
									'<option value="IN">IN</option>' +
								'</select>' +
							'</div>' +
							'<div class="col-sm-10">' +
								'<input  type="text" class="form-control" id="consval'+grRowNum+'" name="consval'+grRowNum+'" >' +
							'</div>' +
							'<div class="sla-label">' +
								'<label style="display: inline" sífor="polval'+grRowNum+'">Interval:</label>' +
							'</div>' + 
							'<div class="col-sm-10">' +
								'<select id="polval'+grRowNum+'" name="polval'+grRowNum+'">' +
									'<option value="-1">Real time</option>' +
									'<option value="6">Over 6 hours</option>' +
									'<option value="12">Over 12 hours</option>' +
									'<option value="24">Over 24 hours</option>' +
								'</select>' +
							'</div>' +
						'</div>' +
					'</div>' +
				'</div>';

			$('#guarantees div:last').before(row);
		}
	}
	
	function removeAllRows () {
		while (rowNum > 0) {
			removeRow (rowNum);
		}
	}

	function agrGrAddRow (key, value, name, kpiName, policy, t_name, t_time, service, provider) {
		grRowNum ++;
		rowNum++;

		if (grRowNum <maxGrRowCount) {
			var row =
				'<p id="grRowNum' + grRowNum +'">' +
					'<span class="label label-info" style="width: 75px">G.name:</span>' +
					'<input type="text" id="gname'+grRowNum+'" name="gname'+grRowNum+'" value="' + kpiName+ '" readonly class="form-control" style="margin-left: 20px; width: 100px"/>' +
					'<span class="label label-info" style="width: 75px; margin-left: 20px">Constraint:</span>' +
					'<input type="text" id="cons'+grRowNum+'" name="cons'+grRowNum+'" value="' + key +'" readonly class="form-control" style="margin-left: 20px; width: 100px"/>' +
					'<span class="label label-info" style="width: 75px;margin-left: 20px">Value:</span>' +
					'<input type="text" id="consval'+grRowNum+'" name="consval'+grRowNum+'" value="' + value +'" readonly class="form-control" style="margin-left: 20px; width: 100px"/>' +
					'<span class="label label-info" style="width: 75px;margin-left: 20px">Interval:</span>';

			if (policy === "") {
				row +=
						'<input type="text" id="polval'+grRowNum+'" name="polval'+grRowNum+'" value="Real time" readonly class="form-control" style="margin-left: 20px; width: 100px"/>';
					'</p>';
			} else {
				row +=
						'<input type="text" id="polval'+grRowNum+'" name="polval'+grRowNum+'" value="Over ' + policy +' hours" readonly class="form-control" style="margin-left: 20px; width: 100px"/>';
					'</p>';
			}

			if (rowNum <maxRowCount) {
				if (rowNum == 1) {
					var row2 =
						'<p>' +
							'<span class="label label-info" style="width: 150px">Template name:</span>' +
							'<input type="text"  id="t_name'+rowNum+'" name="t_name'+rowNum+'" value="' + t_name + '" readonly class="form-control" style="margin-left: 20px; width: 100ppx"/>' +
							'<span class="label label-info" style="width: 150px">Time:</span>' +
							'<input type="text"  id="t_time'+rowNum+'" name="t_time'+rowNum+'" value="' + t_time + '" readonly class="form-control" style="margin-left: 20px; width: 100ppx"/>' +
							'<span class="label label-info" style="width: 150px">Service:</span>' +
							'<input type="text"  id="service'+rowNum+'" name="service'+rowNum+'" value="' + service + '" readonly class="form-control" style="margin-left: 20px; width: 100ppx"/>' +
							'<span class="label label-info" style="width: 150px">Provider:</span>' +
							'<input type="text"  id="provider'+rowNum+'" name="provider'+rowNum+'" value="' + provider + '" readonly class="form-control" style="margin-left: 20px; width: 100ppx"/>' +
						'</p>';
					$('#metric-list').append(row2);
				}

				var row3 =
					'<p id="rowNum' + rowNum +'">' +
						'<span class="label label-info" style="width: 150px">Service property:</span>' +
						'<input type="text"  id="sname'+rowNum+'" name="sname'+rowNum+'" value="' + name + '" readonly class="form-control" style="margin-left: 20px; width: 100ppx"/>' +
					'</p>';
				$('#metric-list').append(row3);
			}

			$('#metric-list').append(row);
		}
	}
