import React from 'react';
import 'todomvc-app-css/index.css';

chrome.storage.local.get('state', (obj) => {
  let state = obj.state;
  if (state) {
    window.state = JSON.parse(state);
  }

  React.render(
    <h1>test</h1>,
    document.querySelector('#root')
  );
});