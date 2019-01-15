var datatable = $('#stock-data-tb').DataTable( {
        "ajax": "http://localhost:8080/fetch_data?page_start=" + 0 + "&page_end=" + 9,
        "order": [[ 9, "desc" ]],
        "bPaginate": false,
        "bLengthChange": false,
        "bFilter": true,
        "bInfo": false,
        "bAutoWidth": false,
        "columns": [
            { "data": "code" },
            { "data": "name" },
            { "data": "group" },
            { "data": "type" },
            { "data": "open" },
            { "data": "high" },
            { "data": "low" },
            { "data": "close" },
            { "data": "last" },
            { "data": "no_of_trades" },
            { "data": "no_of_shares" },
        ]
    } );

$(document).ready(function() {
   datatable.draw();
} );

$('#pagination-here').bootpag({
    total: 10,
    page: 1,
    maxVisible: 5,
    leaps: true,
    href: "#result-page-{{number}}",
});

$('#pagination-here').on("page", function(event, num){
    datatable.clear().draw();
    $.ajax({"url": "http://localhost:8080/fetch_data?page_start=" + (num - 1) * 10 + "&page_end=" + ((num - 1) * 10 + 9) + "&_=124", "success": function (response) {
            var data_obj = JSON.parse(response);
            console.log(num);
            console.log(data_obj.data);
            datatable.rows.add(data_obj.data);
            datatable.columns.adjust().draw();
        }, "error": function (err) {
            console.log(this.url);
            console.log(err)
        }});


});

$(document).ready(function() {
    $("#stock-search-btn").click(function(){
        var search_query = $('#stock-search').val();
        $.ajax({"url": "http://localhost:8080/search?title=" + search_query, "success": function (response) {
            var data_obj = JSON.parse(response);
            console.log(data_obj.code);
            if(data_obj.code !== undefined) {
                datatable.clear().draw();
                datatable.row.add(data_obj);
                datatable.columns.adjust().draw();
            }
            else {
                alert("No stock info was found for " + search_query);
            }
            }, "error": function (err) {
            console.log(err)
            }})
    });
});

