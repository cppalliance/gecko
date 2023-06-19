import React from 'react';
import PropTypes from 'prop-types';

import urlJoin from 'url-join';

import { useTheme } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import LoadingButton from '@mui/lab/LoadingButton';
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

function CustomSearchBox({ inputRef }) {
  const { currentRefinement, refine } = useSearchBox();

  return (
    <TextField
      fullWidth
      size='small'
      placeholder='Search...'
      value={currentRefinement}
      onChange={(event) => refine(event.currentTarget.value)}
      inputRef={inputRef}
      InputProps={{
        startAdornment: (
          <InputAdornment position='start'>
            <SearchIcon />
          </InputAdornment>
        ),
      }}
    />
  );
}

function CustomHit(hit, url_prefix) {
  const { objectID, library_key, library_name, hierarchy, _highlightResult } = hit;
  let hierarchyLinks = [];

  if (_highlightResult) {
    Object.keys(_highlightResult.hierarchy).forEach(function (key) {
      const { title } = _highlightResult.hierarchy[key];
      const { path } = hierarchy[key];
      hierarchyLinks.push(
        <Link
          underline='hover'
          dangerouslySetInnerHTML={{
            __html: title.value,
          }}
          key={path}
          href={urlJoin(url_prefix, path)}
        ></Link>,
      );
    });
  }

  return (
    <Box
      key={objectID}
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
        <Link underline='hover' href={urlJoin(url_prefix, 'libs', library_key)}>
          {library_name}
        </Link>
        {hierarchyLinks}
      </Breadcrumbs>
      <Snippet style={{ color: grey[700], fontSize: 'small' }} hit={hit} attribute='content' />
    </Box>
  );
}

function CustomInfiniteHits({ url_prefix, setnbHits }) {
  const { hits, isLastPage, showMore } = useInfiniteHits();
  const { status } = useInstantSearch();
  const { nbHits } = useStats();

  React.useEffect(() => {
    setnbHits(nbHits);
  }, [nbHits, setnbHits]);

  return (
    <Stack spacing={2}>
      {hits.map((hit) => CustomHit(hit, url_prefix))}
      <Box textAlign='center'>
        <LoadingButton
          size='small'
          loading={status === 'loading' || status === 'stalled'}
          disabled={isLastPage}
          onClick={showMore}
          sx={{ textTransform: 'none' }}
        >
          Show More
        </LoadingButton>
      </Box>
    </Stack>
  );
}

function Search({ library, url_prefix, algoliaIndex, alogliaAppId, alogliaApiKey }) {
  const [searchClient] = React.useState(algoliasearch(alogliaAppId, alogliaApiKey));

  const [selectedTab, setSelectedTab] = React.useState('1');

  const [nbHits, setnbHits] = React.useState(0);
  const [otherLibrariesnbHits, setOtherLibrariesnbHits] = React.useState(0);
  const kFormatter = (num) => (num > 999 ? (num / 1000).toFixed(1) + 'k' : num);

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const [dialogOpen, setDialogOpen] = React.useState(window.location.hash === '#search-dialog');
  const [keepDialogMounted, setKeepDialogMounted] = React.useState(false);

  React.useEffect(() => {
    const onHashChange = () => setDialogOpen(window.location.hash === '#search-dialog');
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleDialogOpen = () => {
    window.location.hash = '#search-dialog';
    setKeepDialogMounted(true);
    setTimeout(() => {
      inputRef.current.focus();
    }, 0);
  };

  const handleDialogClose = () => {
    window.history.back();
  };

  const theme = useTheme();
  const dialogShouldBeFullScreen = useMediaQuery(theme.breakpoints.down('md'));

  const inputRef = React.useRef(null);

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
        maxWidth='md'
        open={dialogOpen}
        onClose={handleDialogClose}
        PaperProps={{ style: dialogShouldBeFullScreen ? {} : { height: '95vh' } }}
      >
        <DialogTitle sx={{ p: 1.5, pb: 0 }}>
          <Grid container spacing={1}>
            <Grid item xs={12}>
              <CustomSearchBox inputRef={inputRef} />
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
              <CustomInfiniteHits url_prefix={url_prefix} setnbHits={setnbHits} />
            </Index>
          </Box>
          <Box hidden={selectedTab !== '2'} sx={{ pt: 1, typography: 'body1' }}>
            <Index indexName={algoliaIndex}>
              <Configure hitsPerPage={30} filters={'NOT library_key:' + library.key} />
              <CustomInfiniteHits url_prefix={url_prefix} setnbHits={setOtherLibrariesnbHits} />
            </Index>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 1.5, pt: 1 }}>
          <Grid container>
            <Grid item xl={2} xs={4} sx={{ mt: 1.2 }}>
              <PoweredBy />
            </Grid>
            <Grid item xl={10} xs={8} sx={{ textAlign: 'right' }}>
              <Button
                size='small'
                sx={{ textTransform: 'none' }}
                target='_blank'
                href='https://github.com/cppalliance/boost-gecko/issues'
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
  url_prefix: PropTypes.string.isRequired,
  algoliaIndex: PropTypes.string.isRequired,
  alogliaAppId: PropTypes.string.isRequired,
  alogliaApiKey: PropTypes.string.isRequired,
};

export default Search;
