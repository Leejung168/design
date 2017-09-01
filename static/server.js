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
                        '<li><a id=' + value + ' ' + 'href="#' + value + '"><i class="fa fa-heart fa-fw"></i>' + value + '</a></li>'
                    );
                    cg.addClass("panelisopen");
                    }
                )
           }
        })
        }
  });



$("#chinanetcloud").click(function(){
  $('#page-wrapper').load('server');
})


$("#keepass").click(function(){
  $('#page-wrapper').load('keepass');
})
