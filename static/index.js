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
    var name = $(obj).attr("id");
    $('#page-wrapper').load('servers?name=' + name);
//    $.ajax({
//    url: "/servers",
//    type: "post",
//    dataType: "json",
//    data: {
//        "name": name,
//    },
//    complete: function(msg){
//        var servers = msg["responseJSON"];
//        $('#page-wrapper').load('servers', servers);
//        console.log(servers)
//    }
//  })
//    $('#page-wrapper').load('servers');
}