//Delete the entry
function server_delete(obj){
    var server_name = $(obj).attr("id");
    $('#server_to_delete').val(server_name);
}

$("#server_delete_yes").click(function(){
    // Get the delete username/password id.
    var server_name = $("#server_to_delete").val();
    $.ajax({
        url: "/s_delete",
        type: "post",
        dataType: "json",
        data: {
            "server_delete": server_name,
        },

        complete: function(msg){
            var customer_name = msg["responseJSON"];
            $("#page-wrapper").load('servers?name=' + customer_name);
           },
    })
  });



// Launch button
$('.launch-button').on('click', function() {
    var $this = $(this);
    $this.button('loading');
    var server_name = $this.attr("value");

    $.ajax({
        url: "/s_launch",
        type: "post",
        dataType: "json",
        data: {
            "server_name": server_name,
        },
        complete: function(msg){
            $this.button('reset');
            var customer_name = msg["responseJSON"];
            console.log(customer_name);
            $("#page-wrapper").load('servers?name=' + customer_name);
           },
    })
  });


$("#plus-form").click(function(){
    server_info = $('form').serialize();
    console.log(server_info);
    $.ajax({
        url: "/s_plus?"+server_info,
        type: "post",
        complete: function(msg){
            var customer_name = msg["responseJSON"];
            $("#page-wrapper").load('servers?name=' + customer_name);
       }
    })
    }
)

$("#server-plus-button").click(function(){
   var group = ($('table').attr('id'));
   $("#user-group").val(group);
}
)

//$('.launch-button').on('click', function() {
//    var $this = $(this);
//    $this.button('loading');
//    setTimeout(function() {
//       $this.button('reset');
//   }, 80000);
//});