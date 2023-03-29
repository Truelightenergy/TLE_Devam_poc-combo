$(document).ready(function(){
    $('#upload_form').on('submit', function(event){
        if($('#upload_file').val()){
            event.preventDefault();
            $('#save').attr('disabled', 'disabled');
            $('#process').css('display', 'block');

            $(this).ajaxSubmit({
                target: '#process',
                beforeSubmit:function(){
                    $('.progress-bar').width('50%');
                },
                uploadProgress: function(event, position, total, percentageComplete)
                {
                    $('.progress-bar').animate({
                        width: percentageComplete + '%'
                    }, {
                        duration: 1000
                    });
                },
                success:function(data){
                
                    $('#process').append(data.htmlresponse);
                },
                resetForm: true
                
            });
            // location.reload();
        }
        return false;
    });
    $('#process').css('display', 'none');
    $('.progress-bar').css('width', '0%');
    $('#save').attr('disabled', false);
    
});
