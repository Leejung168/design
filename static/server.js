//Plus Dialog needs
$(document).ready(function () {
  var navListItems = $('div.setup-panel div a'),
          allWells = $('.setup-content'),
          allNextBtn = $('.nextBtn');

  allWells.hide();

  navListItems.click(function (e) {
      e.preventDefault();
      var $target = $($(this).attr('href')),
              $item = $(this);
      if (!$item.hasClass('disabled')) {
          navListItems.removeClass('btn-primary').addClass('btn-default');
          $item.addClass('btn-primary');
          allWells.hide();
          $target.show();
          $target.find('input:eq(0)').focus();
      }
  });

  allNextBtn.click(function(){
      var curStep = $(this).closest(".setup-content"),
          curStepBtn = curStep.attr("id"),
          nextStepWizard = $('div.setup-panel div a[href="#' + curStepBtn + '"]').parent().next().children("a"),
          curInputs = curStep.find("input[type='text'],input[type='password']"),
          isValid = true;


      $(".form-group").removeClass("has-error");
      for(var i=0; i<curInputs.length; i++){
          if (!curInputs[i].validity.valid){
              isValid = false;
              $(curInputs[i]).closest(".form-group").addClass("has-error");
          }
      }

      if (isValid){
          if (nextStepWizard.attr("href") == "#step-3"){
//            var services = $('input[name="services"]:checked').serialize().split("&");
              var services = $('input[type="checkbox"]:checked').serialize().split("&");
              var res = [];
              var support = ["nginx", "apache", "mysql", "tomcat", "haproxy"];
              $.each(services, function(index, value){
                 res.push(value.split("=")[1]);
               }
              )

              for (i in res){
                  support.splice($.inArray(res[i], support), 1);
              }

//             TODO: when user wants to come back step2, it doesn't work
              for (i in support){
                  var service = "." + support[i];
                  $(service).remove();
              }
          }

          nextStepWizard.removeAttr('disabled').trigger('click');
       }

  });

  $('div.setup-panel div a.btn-primary').trigger('click');




});


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
        success: function() {
            location.reload();
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
           },
    })
  });



//$('.launch-button').on('click', function() {
//    var $this = $(this);
//    $this.button('loading');
//    setTimeout(function() {
//       $this.button('reset');
//   }, 80000);
//});

