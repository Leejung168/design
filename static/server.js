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
              var services = $('input[name="services"]:checked').serialize().split("&");
              var res = []
              var support = ["nginx", "apache", "mysql", "tomcat", "haproxy"]
              $.each(services, function(index, value){
                 res.push(value.split("=")[1])
               }
              )

              for (i in res){
                  support.splice($.inArray(res[i], support), 1);
              }


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

