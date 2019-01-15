$(document).ready(function() {
    $('#stock-data-tb').DataTable( {
        "ajax": "http://localhost:8080/fetch_data?page_start=" + 0 + "&page_end=" + 9,
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
} );

$('#pagination-here').bootpag({
    total: 10,
    page: 1,
    maxVisible: 5,
    leaps: true,
    href: "#result-page-{{number}}",
})

//page click action
$('#pagination-here').on("page", function(event, num){
    //show / hide content or pull via ajax etc

});