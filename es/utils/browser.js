export function browserDownload(json) {
  var fileOutputLink = document.createElement('a');

  var filename = 'output' + Date.now() + '.json';
  filename = window.prompt('Insert output filename', filename);
  if (!filename) return;

  var output = JSON.stringify(json);
  var data = new Blob([output], { type: 'text/plain' });
  var url = window.URL.createObjectURL(data);
  fileOutputLink.setAttribute('download', filename);
  fileOutputLink.href = url;
  fileOutputLink.style.display = 'none';
  document.body.appendChild(fileOutputLink);
  fileOutputLink.click();
  document.body.removeChild(fileOutputLink);
}

export function browserUpload() {
  return new Promise(function (resolve, reject) {
    var fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'application/json'; // Accept only JSON files

    fileInput.addEventListener('change', function (event) {
      var file = event.target.files[0];
      if (file.name !== 'architectural_coordinates.json') {
        reject(new Error('Please select an architectural_coordinates.json file.'));
        return;
      }
      
      var reader = new FileReader();
      reader.addEventListener('load', function (fileEvent) {
        var loadedData = fileEvent.target.result;
        resolve(loadedData);
      });
      reader.readAsText(file);
    });

    // Automatically initiate file upload when the project starts
    fileInput.click();
  });
}

// Call browserUpload when the project starts
browserUpload().then(function(data) {
  // You can handle the loaded data here
}).catch(function(error) {
  // Handle any errors that occur during the file upload process
  console.error(error);
});
