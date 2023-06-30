import React from 'react';
import PropTypes from 'prop-types';

import urlJoin from 'url-join';

import { useTheme } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import grey from '@mui/material/colors/grey';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import useMediaQuery from '@mui/material/useMediaQuery';
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Autocomplete from '@mui/material/Autocomplete';
import HistoryIcon from '@mui/icons-material/History';
import SvgIcon from '@mui/material/SvgIcon';
import CircularProgress from '@mui/material/CircularProgress';

import RecentSearches from 'recent-searches';

import algoliasearch from 'algoliasearch/lite';
import {
  InstantSearch,
  Index,
  Configure,
  useSearchBox,
  useInfiniteHits,
  useInstantSearch,
  useStats,
  Snippet,
  PoweredBy,
} from 'react-instantsearch-hooks-web';

import CppallianceLogo from './CppallianceLogo';

let queryHookTimerId;

function CustomSearchBox({ inputRef, recentSearches }) {
  const queryHook = React.useCallback((query, search) => {
    clearTimeout(queryHookTimerId);
    queryHookTimerId = setTimeout(() => search(query), 300);
  }, []);
  const { currentRefinement, refine } = useSearchBox({ queryHook });
  const { status } = useInstantSearch();

  return (
    <Autocomplete
      freeSolo
      disablePortal
      size='small'
      options={recentSearches.map((option) => option.query)}
      value={currentRefinement}
      onInputChange={(e, newValue) => refine(newValue)}
      onChange={(e, newValue) => refine(newValue || '')}
      renderOption={(props, option) => (
        <Box {...props}>
          <HistoryIcon fontSize='small' sx={{ pr: 1.5, color: grey[600] }} />
          {option}
        </Box>
      )}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder='Search...'
          inputRef={inputRef}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <React.Fragment>
                {status === 'loading' || status === 'stalled' ? (
                  <CircularProgress sx={{ color: grey[600] }} size={16} />
                ) : null}
                {params.InputProps.endAdornment}
              </React.Fragment>
            ),
            startAdornment: (
              <InputAdornment position='start'>
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      )}
    />
  );
}

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

function CustomInfiniteHits({ urlPrefix, setnbHits, onClick, singleLib }) {
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

function Search({ library, urlPrefix, algoliaIndex, alogliaAppId, alogliaApiKey }) {
  const [searchClient] = React.useState(algoliasearch(alogliaAppId, alogliaApiKey));

  const [recentSearches, setRecentSearches] = React.useState(null);

  React.useEffect(() => {
    setRecentSearches(new RecentSearches({ namespace: 'rs-' + library.key }));
  }, [library]);

  const [selectedTab, setSelectedTab] = React.useState('1');

  const [nbHits, setnbHits] = React.useState(0);
  const [otherLibrariesnbHits, setOtherLibrariesnbHits] = React.useState(0);
  const kFormatter = (num) => (num > 999 ? (num / 1000).toFixed(1) + 'k' : num);

  const handleTabChange = React.useCallback((event, newValue) => setSelectedTab(newValue), []);

  const [dialogOpen, setDialogOpen] = React.useState(window.location.hash === '#search-dialog');
  const [keepDialogMounted, setKeepDialogMounted] = React.useState(false);

  React.useEffect(() => {
    const onHashChange = () => setDialogOpen(window.location.hash === '#search-dialog');
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleDialogClose = React.useCallback(() => window.history.back(), []);

  const theme = useTheme();
  const dialogShouldBeFullScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const inputRef = React.useRef(null);

  const handleDialogOpen = React.useCallback(() => {
    window.location.hash = '#search-dialog';
    setKeepDialogMounted(true);
    setTimeout(() => {
      inputRef.current.focus();
    }, 0);
  }, [inputRef]);

  const onClick = React.useCallback(
    () => recentSearches.setRecentSearch(inputRef.current.value),
    [recentSearches, inputRef],
  );

  return (
    <InstantSearch searchClient={searchClient}>
      <Button
        fullWidth
        sx={{ textTransform: 'none' }}
        startIcon={<SearchIcon />}
        variant='outlined'
        onClick={handleDialogOpen}
      >
        Search...
      </Button>
      <Dialog
        fullScreen={dialogShouldBeFullScreen}
        keepMounted={keepDialogMounted}
        fullWidth
        disableRestoreFocus
        maxWidth='md'
        open={dialogOpen}
        onClose={handleDialogClose}
        PaperProps={{ style: dialogShouldBeFullScreen ? {} : { height: '95vh' } }}
        sx={{ zIndex: 99999 }}
      >
        <DialogTitle sx={{ p: 1.5, pb: 0 }}>
          <Grid container spacing={1}>
            <Grid item xs={12}>
              <CustomSearchBox
                inputRef={inputRef}
                recentSearches={inputRef.current ? recentSearches.getRecentSearches(inputRef.current.value) : []}
              />
            </Grid>
            <Grid item xs={12}>
              <Tabs
                value={selectedTab}
                onChange={handleTabChange}
                variant='fullWidth'
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab
                  value='1'
                  sx={{ textTransform: 'none', display: 'inline' }}
                  label={
                    <>
                      {library.name} <Typography variant='caption'>({kFormatter(nbHits)})</Typography>
                    </>
                  }
                />
                <Tab
                  value='2'
                  sx={{ textTransform: 'none', display: 'inline' }}
                  label={
                    <>
                      Other Libraries <Typography variant='caption'>({kFormatter(otherLibrariesnbHits)})</Typography>
                    </>
                  }
                />
              </Tabs>
            </Grid>
          </Grid>
        </DialogTitle>
        <DialogContent sx={{ p: 1.5 }}>
          <Box hidden={selectedTab !== '1'} sx={{ pt: 1, typography: 'body1' }}>
            <Index indexName={algoliaIndex}>
              <Configure hitsPerPage={30} filters={'library_key:' + library.key} />
              <CustomInfiniteHits urlPrefix={urlPrefix} setnbHits={setnbHits} onClick={onClick} singleLib />
            </Index>
          </Box>
          <Box hidden={selectedTab !== '2'} sx={{ pt: 1, typography: 'body1' }}>
            <Index indexName={algoliaIndex}>
              <Configure hitsPerPage={30} filters={'NOT library_key:' + library.key} />
              <CustomInfiniteHits urlPrefix={urlPrefix} setnbHits={setOtherLibrariesnbHits} onClick={onClick} />
            </Index>
          </Box>
        </DialogContent>
        <DialogActions sx={{ pc: 1.5, py: 0.5 }}>
          <Grid container>
            <Grid item xs={6}>
              <PoweredBy style={{ width: 130, paddingTop: 8 }} />
            </Grid>
            <Grid item xs={6} sx={{ textAlign: 'right' }}>
              <Button
                sx={{ textTransform: 'none' }}
                target='_blank'
                href='https://github.com/cppalliance/boost-gecko'
                startIcon={<SvgIcon component={CppallianceLogo} inheritViewBox />}
              >
                Report Issue
              </Button>
            </Grid>
          </Grid>
        </DialogActions>
      </Dialog>
    </InstantSearch>
  );
}

Search.propTypes = {
  library: PropTypes.shape({
    key: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
  }),
  urlPrefix: PropTypes.string.isRequired,
  algoliaIndex: PropTypes.string.isRequired,
  alogliaAppId: PropTypes.string.isRequired,
  alogliaApiKey: PropTypes.string.isRequired,
};

export default Search;
