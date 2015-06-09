    var rowNum = 0;
    var maxRowCount = 11;
    function removeRow(temp) {
        $('#rowNum'+temp).remove();
        rowNum --;
        grRemoveRow(grRowNum);
    };

     function addRow() {
        rowNum ++;
        if(rowNum <maxRowCount)
        {
           var row = '<div class="control-group">' +
            '<p id="rowNum' + rowNum +'">' +
            'Name' + rowNum.toString() + ': <select id="sname'+rowNum+'" name="sname'+rowNum+'">' +
            '<option value="percCPULoad">CPULoad</option>' +
            '<option value="bwd_status">bandwidthStatus</option>' +
            '<option value="percRAMUsed">RAMUsed</option>' +
            '<option value="percDiskUsed">DiskUsed</option>' +
            /*'<option value="SWAPfree">SWAPfree</option>' +
            '<option value="NrProcs">NrProcs</option>' +
            '<option value="NrZOMBIEprocs">NrZOMBIEprocs</option>' +*/
            '</select>' +
            '<input id="rowBtn'+rowNum+'" onclick="removeRow('+rowNum+');" type="button" value="Remove" class="btn">' +
            '</p>' +
            '</div>';

         $('#metrics div:last').before(row);
        }
         grAddRow();
     }


    var grRowNum = 0;
    var maxGrRowCount = 11;
    function grRemoveRow(temp) {
        $('#grRowNum'+temp).remove();
        grRowNum --;
    };

     function grAddRow() {
        grRowNum ++;
        if(grRowNum <maxGrRowCount)
        {
           var row = '<p id="grRowNum' + grRowNum +'">' +
            'G.Name' + grRowNum + ':' +
            '<select  id="gname'+grRowNum+'" name="gname'+grRowNum+'">' +
            '<option value="GT_percCPULoad">CPULoad</option>' +
            '<option value="GT_bwd_status">bandwidthStatus</option>' +
            '<option value="GT_percRAMUsed">RAMUsed</option>' +
            '<option value="GT_percDiskUsed">DiskUsed</option>' +
            /*'<option value="GT_SWAPfree">SWAPfree</option>' +
            '<option value="GT_NrProcs">NrProcs</option>' +
            '<option value="GT_NrZOMBIEprocs">NrZOMBIEprocs</option>' +*/
            '</select>' +
            'Constraints:' +
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
            '<input  type="text" class="form-control" id="consval'+grRowNum+'" name="consval'+grRowNum+'" >' +
            '</p>';

         $('#guarantees div:last').before(row);
        }
     }

     function agrGrAddRow(key, value, name, kpiName, t_name, t_time, service, provider) {
        grRowNum ++;
        rowNum++;
        if(grRowNum <maxGrRowCount)
        {
           var row = '<p id="grRowNum' + grRowNum +'">' +
            '<span class="label label-info" style="width: 75px">G.name:</span>' +
            '<input type="text" id="gname'+grRowNum+'" name="gname'+grRowNum+'" value="' + kpiName+ '" readonly class="form-control" style="margin-left: 20px; width: 100px"/>' +
            '<span class="label label-info" style="width: 75px; margin-left: 20px">Constraint:</span>' +
             '<input type="text" id="cons'+grRowNum+'" name="cons'+grRowNum+'" value="' + key +'" readonly class="form-control" style="margin-left: 20px; width: 100px"/>' +
             '<span class="label label-info" style="width: 75px;margin-left: 20px">Value:</span>' +
             '<input type="text" id="consval'+grRowNum+'" name="consval'+grRowNum+'" value="' + value +'" readonly class="form-control" style="margin-left: 20px; width: 100px"/>' +
            '</p>';
             if(rowNum <maxRowCount)
             {
                 if(rowNum == 1){
                    var row2 = '<p>' +
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

                var row3 = '<p id="rowNum' + rowNum +'">' +
                '<span class="label label-info" style="width: 150px">Service property:</span>' +
                '<input type="text"  id="sname'+rowNum+'" name="sname'+rowNum+'" value="' + name + '" readonly class="form-control" style="margin-left: 20px; width: 100ppx"/>' +
                '</p>';
                 $('#metric-list').append(row3);
             }



         $('#metric-list').append(row);
        }
     }
