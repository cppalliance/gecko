import React from 'react';

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

import algoliasearch from 'algoliasearch/lite';
import {
  InstantSearch,
  Index,
  Configure,
  useSearchBox,
  useInfiniteHits,
  useInstantSearch,
  Snippet,
  PoweredBy
} from 'react-instantsearch-hooks-web';

function CustomSearchBox({ inputRef }) {
  const { currentRefinement, refine } = useSearchBox();

  return (
    <TextField
      fullWidth
      size="small"
      placeholder="Search..."
      value={currentRefinement}
      onChange={event => refine(event.currentTarget.value)}
      inputRef={inputRef}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <SearchIcon />
          </InputAdornment>
        ),
      }}
    />
  );
}

function CustomHit(hit) {
  const { objectID, library_key, library_name, hierarchy, _highlightResult } = hit;
  let hierarchyLinks = []

  if (_highlightResult) {
    Object.keys(_highlightResult.hierarchy).forEach(function (key) {
      const { title } = _highlightResult.hierarchy[key];
      const { path } = hierarchy[key];
      hierarchyLinks.push(
        <Link
          underline="hover"
          dangerouslySetInnerHTML={{ __html: title.value }}
          key={path}
          href={'https://www.boost.org/doc/libs/1_82_0/' + path}
        ></Link>
      )
    });
  }

  return (
    <Box
      key={objectID}
      sx={{
        '& mark': {
          color: 'inherit',
          bgcolor: 'inherit',
          fontWeight: 'bolder',
        }
      }}
    >
      <Breadcrumbs separator="&rsaquo;" fontSize="small">
        <Link
          underline="hover"
          href={'https://www.boost.org/doc/libs/1_82_0/libs/' + library_key}
        >
          {library_name}
        </Link>
        {hierarchyLinks}
      </Breadcrumbs>
      <Snippet
        style={{ color: grey[700], fontSize: "small" }}
        hit={hit}
        attribute="content"
      />
    </Box>
  );
}

function CustomInfiniteHits(props) {
  const { hits, isLastPage, showMore } = useInfiniteHits(props);
  const { status } = useInstantSearch();

  return (
    <Stack spacing={2}>
      {hits.map(CustomHit)}
      <Box textAlign='center'>
        <LoadingButton
          size="small"
          loading={status === 'loading' || status === 'stalled'}
          disabled={isLastPage}
          onClick={showMore}
        >
          Show More
        </LoadingButton>
      </Box>
    </Stack >
  );
}

function Search({ library, algoliaIndex, alogliaAppId, alogliaApiKey }) {
  const [searchClient] = React.useState(algoliasearch(alogliaAppId, alogliaApiKey));

  const [selectedTab, setSelectedTab] = React.useState('1');

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [keepDialogMounted, setKeepDialogMounted] = React.useState(false);

  const handleDialogOpen = () => {
    setDialogOpen(true);
    setKeepDialogMounted(true);
    setTimeout(() => { inputRef.current.focus() }, 0);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
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
        variant="outlined"
        onClick={handleDialogOpen}
      >
        Search...
      </Button>
      <Dialog
        fullScreen={dialogShouldBeFullScreen}
        keepMounted={keepDialogMounted}
        fullWidth
        maxWidth="md"
        open={dialogOpen}
        onClose={handleDialogClose}
        PaperProps={{
          style: dialogShouldBeFullScreen ? {} : {
            minHeight: '95vh',
            maxHeight: '95vh',
          }
        }}
      >
        <DialogTitle sx={{ p: 2, pb: 0 }}>
          <Grid container spacing={1}>
            <Grid item xs={12}>
              <CustomSearchBox inputRef={inputRef} />
            </Grid>
            <Grid item xs={12}>
              <Tabs
                value={selectedTab}
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab value="1" sx={{ textTransform: 'none' }} label={library.name} />
                <Tab value="2" sx={{ textTransform: 'none' }} label="Other Libraries" />
              </Tabs>
            </Grid>
          </Grid>
        </DialogTitle>
        <DialogContent sx={{ p: 2 }}>
          <Box hidden={selectedTab !== "1"} sx={{ pt: 1, typography: 'body1' }}>
            <Index indexName={algoliaIndex}>
              <Configure
                hitsPerPage={30}
                filters={"library_key:" + library.key}
              />
              <CustomInfiniteHits />
            </Index>
          </Box>
          <Box hidden={selectedTab !== "2"} sx={{ pt: 1, typography: 'body1' }}>
            <Index indexName={algoliaIndex}>
              <Configure
                hitsPerPage={30}
                filters={"NOT library_key:" + library.key}
              />
              <CustomInfiniteHits />
            </Index>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Grid container>
            <Grid item xl={2} xs={4} sx={{ mt: 1 }}>
              <PoweredBy />
            </Grid>
            <Grid item xl={10} xs={8} sx={{ textAlign: 'right' }}>
              <Button size="small" sx={{ textTransform: 'none' }} onClick={handleDialogClose}>Close</Button>
            </Grid>
          </Grid>
        </DialogActions>
      </Dialog>
    </InstantSearch >
  );
}

export default Search;
