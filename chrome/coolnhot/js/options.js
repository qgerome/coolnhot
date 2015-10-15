// Saves options to chrome.storage
function save_options() {
   var base_url = document.getElementById('base_url').value;
   if (base_url.slice(-1) !== '/') {
      base_url = base_url + '/';
   }

   chrome.storage.sync.set({
      base_url: base_url
   }, function() {
      // Update status to let user know options were saved.
      var status = document.getElementById('status');
      status.textContent = 'Options saved.';
      setTimeout(function() {
         status.textContent = '';
      }, 750);
   });
}

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options() {
   // Use default value color = 'red' and likesColor = true.
   chrome.storage.sync.get({
      base_url: 'http://127.0.0.1:5000/'
   }, function(items) {
      document.getElementById('base_url').value = items.base_url;
   });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click',
  save_options);