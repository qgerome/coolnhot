
chrome.storage.onChanged.addListener(function(changes) {
   let temperature;
   if ('latestMeasurement' in changes) {
      temperature = changes['latestMeasurement'].newValue.temperature;
   }
   chrome.browserAction.setBadgeText({text: '' + (temperature || 'ERR')});
});
