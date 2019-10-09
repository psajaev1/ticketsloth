$(document).ready(function() {
    $('.add-to-wishlist').on('click', function() {
       var eventID = $(this).data('event');
       $.ajax({
            type: 'POST',
            url: '/wishlist/',
            data: JSON.stringify({'event_id': eventID}),
            contentType: "application/json",
            dataType: 'json'
       }).then(function(data) {
           alert('Added to wishlist.');
       }).catch(function(error) {
          window.location = '/accounts/login/';
       });
    });
});