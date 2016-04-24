host  = window.location.host;
$("#loading").hide();

function getData(){
    var station = $("#station").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();
    $("#loading").show();

    $.ajax("http://" + host + "/avg/" + station + "/" + start_time + "/" + end_time, {
        success : function(data){
            var path = data;
            console.log(data);

            $('#image').remove()
            $('#img').prepend($('<img>',{id:'image',src:data, width:"70%"}))
            $("#loading").hide();

        },
        error: function(){
            console.log("Äh!");
        }
    });
}


