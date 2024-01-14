// Invoked when the page is loaded
$(document).ready(function() {
    // Listen for clicks on elements with the `order-done` CSS class
    $('.order-done').bind('click', function(){
        if (confirm('Вы уверены, что шарик доставлен?')) {
            order_id = $(this).data("order");
            if (order_id > 0) {
                var csrftoken = getCookie('csrftoken');  // Required for security reasons

                $.ajax({  // Background request
                    url: '/order-done/' + order_id,
                    method: 'POST',
                    dataType: 'html',
                    data: {'csrfmiddlewaretoken': csrftoken},
                    success: function(data){
                        location.reload();
                    }
                });
            }
        }
    });

    // Extract any owned cookie
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
