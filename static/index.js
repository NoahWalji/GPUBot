$(document).ready(function() {
    if ($(".p-name").length) {
        console.log("Running")
        if ($(".p-name").text().length > 100) {
            console.log($(".p-name").html())
            shortened = $('.p-name').html().substr(0,100);
            $('.p-name').text(shortened + "...");
        }
    }

});