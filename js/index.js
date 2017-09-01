//Edit the entry
$("#customer_group").click(function(){
    $.ajax({
        url: "/customer",
        type: "post",
        dataType: "json",
        data: {
            "id": 1,
        },
        success: function() {
            location.reload();
        },
        complete: function(mesg){
            alert(mesg["responseJSON"]);
       }
    })
  });


$("#chinanetcloud").click(function(){
  $('#page-wrapper').load('server');
})


$("#keepass").click(function(){
  $('#page-wrapper').load('keepass');
})
