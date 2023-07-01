import React from 'react';
import ReactDOM from 'react-dom/client';

import Demo from './Demo';
import Search from './Search';
import { libraries } from './libraries';

const searchDemo = document.querySelector('#search-demo-react-root');

if (searchDemo) {
  ReactDOM.createRoot(searchDemo).render(
    <React.StrictMode>
      <Demo />
    </React.StrictMode>,
  );
} else {
  try {
    const indexedVersions = ['1_82_0'];
    const { boostVersion, library } = parseURL();

    if (!indexedVersions.includes(boostVersion))
      throw new Error(`There is not search index for this version of boost.`);

    const div = Object.assign(document.createElement('div'), { id: 'search-button-react-root' });

    // Workaround for gil and hana that have searchbox in their pages
    if (library.key === 'gil' || library.key === 'hana') {
      let searchBox = document.querySelector('#searchbox, #MSearchBox');
      addCSS('#search-button-react-root {float: right; width: 120px; padding-right: 18px;}');
      searchBox.replaceChildren(div);
      // Workaround for spirit/classic and wave headers
    } else if (library.key === 'spirit/classic' || library.key === 'wave') {
      let td = document.querySelector('body > table:first-of-type td:nth-child(2)');
      addCSS('#search-button-react-root {float: right; width: 120px;}');
      td.append(div);
    } else {
      const heading = document.querySelector('#boost-common-heading-doc .heading-inner, #heading .heading-inner');
      if (heading) {
        addCSS('#search-button-react-root {float: right; width: 100px; padding-right: 18px;}');
        addCSS('@media (max-device-width: 480px) {#search-button-react-root {padding-top: 18px;}}');
        addCSS('#search-button-react-root * {color: #1976d2;}');
        addCSS('#search-button-react-root button {background-color: #FFF;}');
        heading.appendChild(div);
      } else {
        addCSS('#search-button-react-root button {background-color: #FFF;}');
        addCSS('#search-button-react-root {width: 120px; top: 10px; right: 10px; position: absolute;}');
        document.body.prepend(div);
      }
    }

    ReactDOM.createRoot(div).render(
      <React.StrictMode>
        <Search
          library={library}
          urlPrefix={window.location.origin + '/doc/libs/1_82_0'}
          algoliaIndex={boostVersion}
          alogliaAppId={'D7O1MLLTAF'}
          alogliaApiKey={'44d0c0aac3c738bebb622150d1ec4ebf'}
        />
      </React.StrictMode>,
    );
  } catch {}
}

function addCSS(css) {
  document.head.appendChild(document.createElement('style')).innerHTML = css;
}

function parseURL() {
  let path = window.location.pathname;

  const pathPrefix = '/doc/libs/';
  if (!path.startsWith(pathPrefix)) throw new Error(`Cannot find prefix of ${pathPrefix} in the URL.`);
  path = path.replace(pathPrefix, '');

  const boostVersion = (function () {
    const match = path.match(/^(.*?)\//);
    if (!match || !match[1]) throw new Error(`Cannot extract boost version from the URL.`);
    return match[1];
  })();
  path = path.replace(boostVersion + '/', '');

  path = path.replace('doc/html/boost_', '');
  path = path.replace('doc/html/boost/', '');
  path = path.replace('doc/html/', '');
  path = path.replace('libs/', '');

  let library = undefined;

  // First we try to match libraries like functional/factory and numeric/odeint
  const match = path.match(/([^/]+\/[^/]+)\//);
  if (match && match[1])
    library = libraries.filter((i) => i.key === match[1] || i.key.replace('_', '') === match[1])[0];

  if (!library) {
    const match = path.match(/^(.*?)(?:\.|\/)/);
    if (match && match[1])
      library = libraries.filter((i) => i.key === match[1] || i.key.replace('_', '') === match[1])[0];
  }

  if (!library) {
    const match = path.match(/BOOST_([^_]+)/);
    if (match && match[1]) library = libraries.filter((i) => i.key === match[1].toLowerCase())[0];
  }

  if (!library) throw new Error(`Cannot extract a library_key from the URL`);

  return { boostVersion, library };
}
