$(".searchbutton").click(function(){
    var keywords = $('#inputbutton').val();
    $('.pwresult').load('pw?sname=' + keywords);
})

$('#inputbutton').keydown(function (e){
    if(e.keyCode == 13){
        var keywords = $('#inputbutton').val();
        $('.pwresult').load('pw?sname=' + keywords);
    }
})



//Will list customer names.
$("#customer_group").click(function(){
    if($(this).hasClass("panelisopen")){
        console.log("Already loaded!");
    } else {
        var cg = $(this);
        $.ajax({
            url: "/customer",
            type: "post",
            dataType: "json",
            data: {
                "iid": 1,
            },
            complete: function(msg){
                var customer = msg["responseJSON"];
                $.each(customer, function(key, value){
                    $("#customer").append(
                        '<li><a onclick="customer(this)" id=' + value + ' ' + 'href="#' + value + '"><i class="fa fa-heart fa-fw"></i>' + value + '</a></li>'
                    );
                    cg.addClass("panelisopen");
                    }
                )
           }
        })
        }
  });


function customer(obj){
   // Get name when choose customer
    var name = $(obj).attr("id");
    $('#page-wrapper').load('servers?name=' + name);
}


function server_selection(obj){
    var server_name = $(obj).val();
    $('.detailed_pages').load("s_detailed?server=" + server_name);
}