import 'babel/polyfill';  // support generator
import bluebird from 'bluebird';
import request from 'superagent';

function promisifier(method) {
  // return a function
  return function promisified() {
    let args = [].slice.call(arguments);

    // which returns a promise
    return new Promise((resolve, reject) => {
      args.push(resolve);
      method.apply(this, args);
    });
  };
}

function promisifyAll(obj, list) {
  list.forEach( (api) => bluebird.promisifyAll(obj[api], { promisifier }) );
}

// let chrome extension api support Promise
promisifyAll(chrome, [
  'tabs',
  'windows',
  'browserAction',
	'storage'
]);
promisifyAll(chrome.storage, [
  'local'
]);

function getAverageTemperature() {
	request
		.get(`http://cramike.synology.me:9000/measurements/avg`)
		.set('Accept', 'application/json')
		.end(function(err, res) {
			if (res.ok) {
				chrome.storage.local.set({latestMeasurement: res.body.average});
			} else {
				console.log('Error');
			}
		});
}

function loop() {
	getAverageTemperature();
	setTimeout(loop, 1000);
}
loop();

require('./badge');
