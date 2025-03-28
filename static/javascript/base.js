$(document).ready(function () {
    $('.like-btn').on('click', function () {
        const postId = $(this).data('post-id');
        const button = $(this);

        $.ajax({
            url: likeUrl,
            type: 'POST',
            data: {
                'post_id': postId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (response) {
                button.text(response.is_liked ? 'Unlike' : 'Like');
                button.siblings('.like-count').text(response.like_count);
            }
        });
    });

    $('form#new-comment-form').on('submit', function (e) {
        e.preventDefault();
        const textarea = $(this).find('textarea[name="content"]');
        const content = textarea.val();

        $.ajax({
            url: window.location.href,
            method: "POST",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'content': content
            },
            success: function (data) {
                if (data.success) {
                    const commentHTML = `
                        <li class="list-group-item">
                            <strong>${data.username}</strong>: ${data.content}
                            <small class="text-muted d-block">${data.timestamp}</small>
                            <a href="#" class="btn btn-sm btn-link reply-toggle" data-id="${data.replyee_id || ''}">Reply</a>
                            <div class="reply-form-container mt-2" style="display:none;">
                                <form class="ajax-reply-form">
                                    <input type="hidden" name="replyee_id" value="${data.replyee_id || ''}">
                                    <textarea name="content" class="form-control" rows="2" placeholder="Write your reply..."></textarea>
                                    <button type="submit" class="btn btn-success btn-sm mt-1">Reply</button>
                                </form>
                            </div>
                        </li>`;
                    $('.list-group').prepend(commentHTML);
                    textarea.val("");
                }
            }
        });
    });

    $(document).on('click', '.reply-toggle', function (e) {
        e.preventDefault();
        $(this).siblings('.reply-form-container').toggle();
    });

    $(document).on('submit', '.ajax-reply-form', function (e) {
        e.preventDefault();
        const form = $(this);
        const replyeeId = form.find('input[name="replyee_id"]').val();
        const content = form.find('textarea[name="content"]').val();

        $.ajax({
            url: window.location.href,
            method: "POST",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'content': content,
                'replyee_id': replyeeId
            },
            success: function (data) {
                if (data.success) {
                    const replyHTML = `
                        <ul class="list-group mt-2 ms-4">
                            <li class="list-group-item">
                                <strong>${data.username}</strong>: ${data.content}
                                <small class="text-muted d-block">${data.timestamp}</small>
                            </li>
                        </ul>`;
                    form.closest('.list-group-item').append(replyHTML);
                    form.closest('.reply-form-container').hide();
                    form.find('textarea[name="content"]').val('');
                }
            }
        });
    });
});

