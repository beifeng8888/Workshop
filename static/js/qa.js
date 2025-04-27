$(document).ready(function(){
    $('#ask-form').submit(function(e){
        e.preventDefault();
        const question = $('question-input').val();

        $.ajax({
            url:'/api/ai-answer/',
            method:'POST',
            headers:{"X-CSRFToken":$("[name=csrfmiddlewaretoken]").val()},
            data:{question:question},
            success:function(data){
                $('#answer-container').html(`
                    <div class="ai-answer">
                        <h4>回复:</h4>
                        <small>响应时间：$(data.response_time)s</small>
                    </div>
                `);

                $('#qa-history').prepend(
                    <div class="qa-item">
                        <h5>${data.question}</h5>
                        <p>${data.answer}</p>
                    </div>
                );
            },
            error:function(xhr){
                alert('请求失败'+xhr.responceJSON.error);
            }
        });
    });
});