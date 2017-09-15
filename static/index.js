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

$('body').bind('beforeunload',function(){
    $("#customer_group").trigger('click');
});

function customer(obj){
   // Get name when choose customer
    var name = $(obj).attr("id");
    $('#page-wrapper').load('servers?name=' + name);
}

$(".show_tasks").click(function(){
    $("#show_tasks").load('show_tasks')
}
)


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
              var support = ["Nginx", "Apache", "Mysql", "Tomcat", "Haproxy"];
//              var support = ["nginx", "apache", "mysql", "tomcat", "haproxy"];
              $.each(services, function(index, value){
                 res.push(value.split("=")[1]);
               }
              )

              for (i in res){
                  console.log($.inArray(res[i], support));
                  if ($.inArray(res[i], support) != -1){
                      support.splice($.inArray(res[i], support), 1);
                  }
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