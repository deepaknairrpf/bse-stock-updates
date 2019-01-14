$(document).ready(function() {
    $('#example').DataTable( {
        "ajax": "http://localhost:8080/fetch_data",
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
            { "data": "no_of_trades"},
        ]
    } );
    $('#search').addEventListener('keypress', function (ev) {
        ev.preventDefault()
        //Extract value from input
        //Call the API

    })
} );
