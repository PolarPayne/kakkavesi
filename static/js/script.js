host  = window.location.host;
depth = 2;

$("#loading").hide();

function getData(code, start, end){
    var station = code ? code : $("#station").val();
    var start_time = start ? start : $("#start_time").val();
    var end_time = end ? end : $("#end_time").val();
    $("#loading").show();

    $.ajax("http://" +host + "/neighbors/"+station+"/"+depth, {
        success : function(data){
            console.log(data);
            var codes = JSON.parse(data);
            var links = $("#links");
            console.log(codes);

            $.each(codes, function(i,k){
                links.prepend('<a href="javascript:void(0);" onclick="getData('+k +','+start +','+ end+')">'+k +', '+'</a>');
            });
        }
    });

    $.ajax("http://" + host + "/avg/" + station + "/" + start_time + "/" + end_time, {
        success : function(data){
            var path = data;
            console.log(data);

            $('#image').remove();
            $('#img').prepend($('<img>',{id:'image',src:data, width:"70%"}));
            $("#loading").hide();

        },
        error: function(){
            console.log("Äh!");
        }
    });
}


