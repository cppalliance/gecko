import React from 'react';
import PropTypes from 'prop-types';

import urlJoin from 'url-join';

import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import grey from '@mui/material/colors/grey';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';

import { useInfiniteHits, useInstantSearch, useStats, Snippet } from 'react-instantsearch-hooks-web';

function CustomHit({ hit, urlPrefix, onClick, singleLib }) {
  const { library_key, library_name, hierarchy, _highlightResult } = hit;
  const hierarchyLinks = React.useMemo(() => {
    if (!_highlightResult) return [];
    return Object.keys(_highlightResult.hierarchy).map((key) => (
      <Link
        underline='hover'
        dangerouslySetInnerHTML={{
          __html: _highlightResult.hierarchy[key].title.value,
        }}
        key={hierarchy[key].path}
        onClick={onClick}
        onAuxClick={onClick}
        href={urlJoin(urlPrefix, hierarchy[key].path)}
      ></Link>
    ));
  }, [urlPrefix, onClick, hierarchy, _highlightResult]);

  return (
    <Box
      sx={{
        wordWrap: 'break-word',
        '& mark': {
          color: 'inherit',
          bgcolor: 'inherit',
          fontWeight: 'bolder',
        },
      }}
    >
      <Breadcrumbs separator='&rsaquo;' fontSize='small' sx={{ wordBreak: 'break-all' }}>
        {(!singleLib || hierarchyLinks.length === 0) && (
          <Link underline='hover' href={urlJoin(urlPrefix, 'libs', library_key)}>
            {library_name}
          </Link>
        )}
        {hierarchyLinks}
      </Breadcrumbs>
      <Snippet style={{ color: grey[700], fontSize: 'small' }} hit={hit} attribute='content' />
    </Box>
  );
}

CustomHit.propTypes = {
  hit: PropTypes.object.isRequired,
  urlPrefix: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  singleLib: PropTypes.bool,
};

function InfiniteHits({ urlPrefix, setnbHits, onClick, singleLib }) {
  const { hits, isLastPage, showMore } = useInfiniteHits();
  const { use } = useInstantSearch();
  const [error, setError] = React.useState(null);
  const { nbHits } = useStats();

  React.useEffect(() => {
    setnbHits(nbHits);
  }, [nbHits, setnbHits]);

  React.useEffect(() => {
    const middleware = ({ instantSearchInstance }) => {
      function handleError(searchError) {
        setError(searchError);
      }
      return {
        subscribe() {
          instantSearchInstance.addListener('error', handleError);
        },
        unsubscribe() {
          instantSearchInstance.removeListener('error', handleError);
        },
      };
    };

    return use(middleware);
  }, [use]);

  const memoizedHits = React.useMemo(
    () =>
      hits.map((hit) => (
        <CustomHit key={hit.objectID} hit={hit} urlPrefix={urlPrefix} onClick={onClick} singleLib={singleLib} />
      )),
    [hits, urlPrefix, onClick, singleLib],
  );

  if (error) {
    return (
      <Alert severity='error'>
        <AlertTitle>{error.name}</AlertTitle>
        {error.message}
      </Alert>
    );
  }

  return (
    <Stack spacing={2}>
      {memoizedHits}
      <Box textAlign='center'>
        <Button size='small' disabled={isLastPage} onClick={showMore} sx={{ textTransform: 'none' }}>
          Show More
        </Button>
      </Box>
    </Stack>
  );
}

InfiniteHits.propTypes = {
  urlPrefix: PropTypes.string.isRequired,
  setnbHits: PropTypes.func.isRequired,
  onClick: PropTypes.func.isRequired,
  singleLib: PropTypes.bool,
};

export default InfiniteHits;
