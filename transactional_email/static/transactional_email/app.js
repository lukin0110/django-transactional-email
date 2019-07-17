/**
 * Just "vanilla" jQuery. Maybe later on I might switch to Vue or React but
 * I want to avoid a bloated JS setup with webpack for now.
 */
(function(global){
  var BASE_URL = '/transactional_email';

  var _errorCallback = function(xhr, ajaxOptions, thrownError) {
    showError(xhr.responseText);
  };

  // Construct full path to an API endpoint
  function u(path) {
    return BASE_URL + path;
  }

  // Redirect with Notification
  function redirect(notification, data) {
    var template_id = data['template_id'];
    var suffix = '&t=' + new Date().getTime() + '#template-' + template_id;
    window.location.href = '?notification=' + notification + suffix;
  }

  function configure(base_url) {
    console.log('API Base path configured: ' + base_url);
    BASE_URL = base_url;
  }

  function showError(text){
    // Hide all active modals
    $('.modal').modal('hide');
    var $error = $('#error');
    $error.find('.modal-body').html('<pre class="text-white">' + text + '</pre>');
    $error.modal('show');
  }

  function toast(message) {
    var delay = 4000;
    var $t = $('#toast');
    $t.show();
    $t.toast({delay: delay});
    $t.find('.toast-body').html(message);
    $t.toast('show');
    setTimeout(function(){$t.hide();}, delay+500);
  }

  function sendTestMail(data) {
    console.log('Send test: ' + JSON.stringify(data));

    $.ajax({
      url: u('/emails/'),
      method: "POST",
      data: data,
      success: function(data) {
        console.log(JSON.stringify(data));
      },
      error: function(xhr, ajaxOptions, thrownError) {
        showError(xhr.responseText);
      }
    });
  }

  function deleteTemplate(pk) {
    console.log('Template: ' + pk);

    $.ajax({
      url: u('/templates/' + pk + '/'),
      method: 'DELETE',
      data: {},
      success: function(data){
        console.log(JSON.stringify(data));
        window.location.href = '?notification=deleted';
      },
      error: _errorCallback
    });
  }

  function makeActive(pk) {
    console.log('Make Active: ' + pk);

    $.ajax({
      url: u('/versions/' + pk + '/'),
      method: 'PUT',
      success: function() {
        window.location.href = '?notification=activated';
      },
      error: _errorCallback
    });
  }

  function duplicateVersion(pk) {
    console.log('Version: ' + pk);

    $.ajax({
      url: u('/versions/' + pk + '/'),
      method: 'POST',
      success: function(data) {
        redirect('duplicated', data);
      },
      error: _errorCallback
    });
  }

  function addVersion(template_id) {
    console.log('Templated ID: ' + template_id);
    $.ajax({
      url: u('/versions/'),
      method: 'POST',
      data: {'template_id': template_id},
      success: function(data) {
        window.location.href = 'version/' + data['id'] + '/edit'
      },
      error: _errorCallback
    });
  }

  function deleteVersion(pk) {
    console.log('Delete Version: ' + pk);
    $.ajax({
      url: u('/versions/' + pk + '/'),
      method: 'DELETE',
      success: function(data){
        redirect('deleted_version', data);
      },
      error: function(xhr, ajaxOptions, thrownError) {
        showError(xhr.responseText);
      }
    });
  }

  // Send the CSRF Token on each Ajax request
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }
      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });

  // Export global available functions
  global.TE = {
    configure: configure,
    toast: toast,
    sendTestMail: sendTestMail,
    deleteTemplate: deleteTemplate,
    makeActive: makeActive,
    duplicateVersion: duplicateVersion,
    addVersion: addVersion,
    deleteVersion: deleteVersion
  }
})(window);
