$(document).ready(function () {
    // Обработка отправки комментариев
    $('#commentForm').submit(function (event) {
        event.preventDefault();
        const formData = $(this).serialize();
        $.post($(this).attr('action'), formData, function (response) {
            $('#commentsList').prepend(response);
            $('#commentForm')[0].reset();
        });
    });

    // Обработка редактирования комментариев
    $('.edit-comment').click(function () {
        const commentId = $(this).data('comment-id');
        const newContent = prompt("Edit your comment:");
        if (newContent) {
            $.ajax({
                url: `/comment/${commentId}/edit`,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ content: newContent }),
                success: function (response) {
                    $(`#comment-${commentId}`).text(newContent);
                }
            });
        }
    });

    $('#ratingForm').submit(function (event) {
    event.preventDefault();
    const rating = $('#rating').val();
    const url = '/<movie_id>/rate';  // Замените на динамическое movie_id
    $.ajax({
        url: url,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ rating: parseInt(rating) }),
        success: function (response) {
            alert('Rating submitted! Average: ' + response.average_rating);
        },
        error: function (xhr) {
            alert('Error: ' + xhr.responseJSON.error);
        }
    });
});


