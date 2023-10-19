import React from 'react';
import ReactDOM from 'react-dom/client';

import Demo from './Demo';
import SearchDialog from './Search/SearchDialog';
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
    const { boostVersion, library } = parseURL();
    const searchButton = document.getElementById('gecko-search-button');
    const currentBoostVersion = searchButton.getAttribute('data-current-boost-version');
    const themeMode = searchButton.getAttribute('data-theme-mode');

    const div = document.createElement('div');
    ReactDOM.createRoot(div).render(
      <React.StrictMode>
        <SearchDialog
          themeMode={themeMode}
          versionWarning={!!boostVersion && boostVersion !== currentBoostVersion}
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

  boostVersion = boostVersion.replace('boost_', '');

  return { boostVersion, library };
}
