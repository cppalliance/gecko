import React from 'react';
import ReactDOM from 'react-dom/client';

import Demo from './Demo';
import Search from './Search';
import { libraries } from './libraries';

const searchDemo = document.querySelector('#search-demo-react-root');
const boostCommonHeadingDoc = document.querySelector('#boost-common-heading-doc .heading-inner');


if (searchDemo) {
  ReactDOM.createRoot(searchDemo).render(
    <React.StrictMode>
      <Demo />
    </React.StrictMode>,
  );
} else if (boostCommonHeadingDoc) {
  let url = window.location.href;
  const url_prefix = 'https://www.boost.org/doc/libs/1_82_0/';

  if (!url.startsWith(url_prefix))
    throw new Error(`Cannot find prefix of ${url_prefix} in the URL.`);

  url = url.replace(url_prefix, '');
  url = url.replace('doc/html/boost_', '');
  url = url.replace('doc/html/boost/', '');
  url = url.replace('doc/html/', '');
  url = url.replace('libs/', '');

  const match = url.match(/^(.*?)(?:\.|\/)/);

  if (!match || !match[1])
    throw new Error(`Cannot extract library_key from the URL.`);

  const library = libraries.filter((i) => i.key === match[1])[0];

  if (!library)
    throw new Error(`Cannot find a library with such key: ${match[1]}.`);

  const addCSS = (css) => (document.head.appendChild(document.createElement('style')).innerHTML = css);
  addCSS('#search-button-react-root {float: right; width: 100px; padding-right: 18px;}');
  addCSS('#search-button-react-root * {color: #1976d2;}');
  addCSS('#search-button-react-root button {background-color: #FFF;}');

  const div = Object.assign(document.createElement('div'), { id: 'search-button-react-root' })

  boostCommonHeadingDoc.appendChild(div);

  ReactDOM.createRoot(div).render(
    <React.StrictMode>
      <Search
        library={library}
        url_prefix={'https://www.boost.org/doc/libs/1_82_0'}
        algoliaIndex={'1_82_0'}
        alogliaAppId={'D7O1MLLTAF'}
        alogliaApiKey={'44d0c0aac3c738bebb622150d1ec4ebf'}
      />
    </React.StrictMode>,
  );
}
