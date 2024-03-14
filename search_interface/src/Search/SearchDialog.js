import React from 'react';
import PropTypes from 'prop-types';

import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import useMediaQuery from '@mui/material/useMediaQuery';
import Typography from '@mui/material/Typography';
import SvgIcon from '@mui/material/SvgIcon';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import RecentSearches from 'recent-searches';

import algoliasearch from 'algoliasearch/lite';
import { InstantSearch, Index, Configure, PoweredBy } from 'react-instantsearch';

import CppallianceLogo from './CppallianceLogo';
import SearchBox from './SearchBox';
import InfiniteHits from './InfiniteHits';

function SearchDialog({ themeMode, fontFamily, versionWarning, library, urlPrefix, algoliaIndex, alogliaAppId, alogliaApiKey }) {
  const [searchClient] = React.useState(() => {
    const algoliaClient = algoliasearch(alogliaAppId, alogliaApiKey);
    // Prevents empty search query
    return {
      ...algoliaClient,
      search(requests) {
        if (requests.every(({ params }) => !params.query)) {
          return Promise.resolve({
            results: requests.map(() => ({
              hits: [],
              nbHits: 0,
              nbPages: 0,
              page: 0,
              processingTimeMS: 0,
              hitsPerPage: 0,
              exhaustiveNbHits: false,
              query: '',
              params: '',
            })),
          });
        }

        return algoliaClient.search(requests);
      }
    };
  });

  const [recentSearches, setRecentSearches] = React.useState(null);

  React.useEffect(() => {
    if (library) setRecentSearches(new RecentSearches({ namespace: 'rs-' + library.key }));
    else setRecentSearches(new RecentSearches({ namespace: 'rs-main-page' }));
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

  const theme = React.useMemo(() => createTheme({
    palette: {
      mode: themeMode,
      primary: {
        main: (themeMode === 'dark' ? '#7DD3FC' : '#0284C7'),
      },
      ...(themeMode === 'dark' &&
      {
        background: {
          paper: '#172A34',
        }
      })
    },
    typography: {
      allVariants: { ...fontFamily && { fontFamily } }
    },
  }), [themeMode, fontFamily]);

  const dialogShouldBeFullScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const inputRef = React.useRef(null);

  const handleDialogOpen = React.useCallback(() => {
    window.location.hash = '#search-dialog';
    setKeepDialogMounted(true);
    setTimeout(() => {
      inputRef.current.focus();
    }, 0);
  }, [inputRef]);

  React.useEffect(() => {
    const searchButton = document.getElementById('gecko-search-button');
    searchButton.addEventListener('click', handleDialogOpen);
    return () => searchButton.removeEventListener('click', handleDialogOpen);
  }, [handleDialogOpen]);

  const setRecentSearch = React.useCallback(
    () => recentSearches.setRecentSearch(inputRef.current.value),
    [recentSearches, inputRef],
  );

  return (
    <InstantSearch searchClient={searchClient} future={{ preserveSharedStateOnUnmount: true }}>
      <ThemeProvider theme={theme}>
        <Dialog
          fullScreen={dialogShouldBeFullScreen}
          disableScrollLock={true}
          keepMounted={keepDialogMounted}
          fullWidth
          disableRestoreFocus
          maxWidth='md'
          open={dialogOpen}
          onClose={handleDialogClose}
          PaperProps={{ style: dialogShouldBeFullScreen ? {} : { height: '95vh' } }}
          sx={{ zIndex: 99999 }}
        >
          <DialogTitle sx={{ p: 1.5, pb: 0, color: theme.palette.text.primary }}>
            <Grid container spacing={1}>
              <Grid item xs={12}>
                <SearchBox
                  inputRef={inputRef}
                  recentSearches={inputRef.current ? recentSearches.getRecentSearches(inputRef.current.value) : []}
                />
              </Grid>
              <Grid item xs={12}>
                {versionWarning && (
                  <Typography variant='caption' sx={{ display: 'block' }}>
                    <Box component='span' fontWeight='bolder'>
                      Note:
                    </Box>{' '}
                    search limited to the latest version of documentation.
                  </Typography>
                )}
                {!library ? (
                  <Typography
                    variant='caption'
                    gutterBottom
                    sx={{ display: 'block', borderBottom: 1, borderColor: 'divider' }}
                  >
                    <Box component='span' fontWeight='bolder'>
                      Tip:
                    </Box>{' '}
                    limit the search scope by navigating to a library page.
                  </Typography>
                ) : (
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
                )}
              </Grid>
            </Grid>
          </DialogTitle>
          <DialogContent sx={{ p: 1.5 }}>
            {!library ? (
              <Index indexName={algoliaIndex}>
                <Configure hitsPerPage={30} />
                <InfiniteHits urlPrefix={urlPrefix} setnbHits={setnbHits} onClick={setRecentSearch} />
              </Index>
            ) : (
              <>
                <Box hidden={selectedTab !== '1'} sx={{ pt: 1, typography: 'body1' }}>
                  <Index indexName={algoliaIndex}>
                    <Configure hitsPerPage={30} filters={'library_key:' + library.key} />
                    <InfiniteHits urlPrefix={urlPrefix} setnbHits={setnbHits} onClick={setRecentSearch} singleLib />
                  </Index>
                </Box>
                <Box hidden={selectedTab !== '2'} sx={{ pt: 1, typography: 'body1' }}>
                  <Index indexName={algoliaIndex}>
                    <Configure hitsPerPage={30} filters={'NOT library_key:' + library.key} />
                    <InfiniteHits urlPrefix={urlPrefix} setnbHits={setOtherLibrariesnbHits} onClick={setRecentSearch} />
                  </Index>
                </Box>
              </>
            )}
          </DialogContent>
          <DialogActions sx={{ pc: 1.5, py: 0.5 }}>
            <Grid container>
              <Grid item xs={6}>
                <PoweredBy theme={theme.palette.mode} style={{ width: 140, paddingTop: 12 }} />
              </Grid>
              <Grid item xs={6} sx={{ textAlign: 'right' }}>
                <Button
                  sx={{ textTransform: 'none' }}
                  target='_blank'
                  href='https://github.com/cppalliance/boost-gecko/issues'
                  startIcon={<SvgIcon component={CppallianceLogo} inheritViewBox />}
                >
                  Report Issue
                </Button>
              </Grid>
            </Grid>
          </DialogActions>
        </Dialog>
      </ThemeProvider>
    </InstantSearch>
  );
}

SearchDialog.propTypes = {
  themeMode: PropTypes.string.isRequired,
  fontFamily: PropTypes.string,
  versionWarning: PropTypes.bool.isRequired,
  library: PropTypes.shape({
    key: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
  }),
  urlPrefix: PropTypes.string.isRequired,
  algoliaIndex: PropTypes.string.isRequired,
  alogliaAppId: PropTypes.string.isRequired,
  alogliaApiKey: PropTypes.string.isRequired,
};

export default SearchDialog;
