function convertTableToExcel(tableId, table_data) {
    var table = $('#' + tableId);
    var filename = table_data;
    var excelHtml = table.clone().appendTo('body');
    excelHtml.find('button, input, textarea').remove();
    var excelFile = excelHtml.html();
    excelHtml.remove();
    var uri = 'data:application/vnd.ms-excel;charset=utf-8,' + encodeURIComponent(excelFile);
    var link = document.createElement('a');
    link.href = uri;
    link.download = filename + '.xls';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }