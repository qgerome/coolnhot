/**
 * Created by quentingerome on 14/10/15.
 */
window.onload = main;
var pollInterval = 2000;
var timerId;

function main() {
   updateBadge();
   timerId = window.setTimeout(main, pollInterval);
}

function stop() {
   window.clearTimeout(timerId);
}

function getMeasure() {
   return new Promise(function (resolve, reject) {
      chrome.storage.sync.get('base_url', function (items) {
         $.ajax({
            url: `${items.base_url}measurements/avg`,
            method: 'GET',
            dataType: 'json',
            contentType: "application/json"
         })
           .success(function (rv) {
              resolve(rv.average);
           })
           .fail(function (jqXHR, textStatus, errorThrown) {
              reject(jqXHR, textStatus, errorThrown);
           })
      })
   });
}

function updateBadge() {
   getMeasure()
     .then(
        function (average) {
           chrome.browserAction.setBadgeText({text: '' + (average.temperature || 'ERR')});
           console.log(average);
        },
        function (jqXHR, textStatus, errorThrown) {
           console.log(jqXHR, textStatus, errorThrown);
        }
      );
}