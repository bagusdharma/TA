// Send Jquery AJAX request
function send_ajax_request(method, url, data){

  // Set default value
  if (data === undefined) {
    data = null
  }

  // Prepare ajax settings
  var settings = {
    "async": true,
    "url": url,
    "method": method,
    "processData": false,
    "contentType": false,
    "mimeType": "multipart/form-data",
    "data": data,
    error: function (xhr, responseData, textStatus) {
      console.log(xhr.status+" ERROR: "+textStatus);
    }
  }
  return $.ajax(settings)
}
