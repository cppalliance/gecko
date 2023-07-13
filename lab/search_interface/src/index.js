import React from 'react';
import ReactDOM from 'react-dom/client';

import Demo from './Demo';
import SearchButton from './Search/SearchButton';
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
    let { boostVersion, library } = parseURL();

    const currentBoostVersion = document
      .querySelector('script[data-current-version]')
      .getAttribute('data-current-version')
      .replaceAll('.', '_');

    const div = Object.assign(document.createElement('div'), { id: 'search-button-react-root' });

    // Workaround for gil and hana that have searchbox in their pages
    if (library && (library.key === 'gil' || library.key === 'hana')) {
      let searchBox = document.querySelector('#searchbox, #MSearchBox');
      addCSS('#search-button-react-root {float: right; width: 120px; padding-right: 18px;}');
      searchBox.replaceChildren(div);
      // Workaround for spirit/classic and wave headers
    } else if (library && (library.key === 'spirit/classic' || library.key === 'wave')) {
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
        <SearchButton
          versionWarning={boostVersion && boostVersion !== currentBoostVersion}
          library={library}
          urlPrefix={window.location.origin + `/doc/libs/${currentBoostVersion}`}
          algoliaIndex={currentBoostVersion}
          alogliaAppId={'D7O1MLLTAF'}
          alogliaApiKey={'44d0c0aac3c738bebb622150d1ec4ebf'}
        />
      </React.StrictMode>,
    );
  } catch { }
}

function addCSS(css) {
  document.head.appendChild(document.createElement('style')).innerHTML = css;
}

function parseURL() {
  let library = undefined;
  let boostVersion = undefined;
  let path = window.location.pathname;

  const pathPrefix = '/doc/libs/';
  if (!path.startsWith(pathPrefix)) return { boostVersion, library };
  path = path.replace(pathPrefix, '');

  {
    const match = path.match(/^(.*?)\//);
    if (!match || !match[1]) return { boostVersion, library };
    boostVersion = match[1];
  }

  path = path.replace(boostVersion + '/', '');
  path = path.replace('doc/html/boost_', '');
  path = path.replace('doc/html/boost/', '');
  path = path.replace('doc/html/', '');
  path = path.replace('libs/', '');

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

  const specialPages = [
    '/doc/libs',
    `/doc/libs/${boostVersion}`,
    `/doc/libs/${boostVersion}/doc/html`,
    `/doc/libs/${boostVersion}/doc/html/index.html`,
    `/doc/libs/${boostVersion}/libs/libraries.htm`,
  ];

  if (!library && !specialPages.includes(window.location.pathname.replace(/\/+$/, '')))
    throw new Error(`Cannot extract the library_key from the URL`);

  return { boostVersion, library };
}
