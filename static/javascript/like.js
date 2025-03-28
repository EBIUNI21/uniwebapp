$(document).ready(function() {
    $('.like-btn').on('click', function() {
        var postId = $(this).data('post-id');
        var button = $(this);

        $.ajax({
            url: likeUrl,
            type: 'POST',
            data: {
                'post_id': postId,
                'csrfmiddlewaretoken': csrfToken,
            },
            success: function(response) {
                if (response.is_liked) {
                    button.text('Unlike');
                } else {
                    button.text('Like');
                }
                button.siblings('.like-count').text(response.like_count);
            }
        })
    })
})