function toggleCheckbox(element) {

   if (element.checked) {
              $('#company').attr('required', true); //to add required
              $('#namecompany').css("display","block");
              $('#tvacompany').css("display","block");
    } else {
              $('#company').attr('required', false); //to remove required
              $('#tva').attr('required', false);
              $('#namecompany').css("display","none");
              $('#tvacompany').css("display","none");
   }
};

