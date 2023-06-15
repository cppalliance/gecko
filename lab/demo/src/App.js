import { libraries } from './libraries.js'

import React from 'react';

import TextField from '@mui/material/TextField';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Select from '@mui/material/Select';
import LoadingButton from '@mui/lab/LoadingButton';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import grey from '@mui/material/colors/grey';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import SearchIcon from '@mui/icons-material/Search';

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
      label="Search..."
      value={currentRefinement}
      onChange={event => refine(event.currentTarget.value)}
      inputRef={inputRef}
    />
  );
}

function CustomHit(hit) {
  const { objectID, boost_version, library_key, library_name, hierarchy, _highlightResult } = hit;
  let hierarchyLinks = []

  if (_highlightResult) {
    Object.keys(_highlightResult.hierarchy).forEach(function (key) {
      const { title } = _highlightResult.hierarchy[key];
      const { url } = hierarchy[key];
      hierarchyLinks.push(
        <Link
          underline="hover"
          dangerouslySetInnerHTML={{ __html: title.value }}
          key={url}
          href={url}
        ></Link>
      )
    });
  }

  return (
    <Box key={objectID}>
      <Breadcrumbs separator="&rsaquo;">
        <Link
          underline="hover"
          href={'https://www.boost.org/doc/libs/' + boost_version + '/libs/' + library_key}
        >
          {library_name}
        </Link>
        {hierarchyLinks}
      </Breadcrumbs>
      <Snippet
        style={{ color: grey[700] }}
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

function App() {
  const [searchClient] = React.useState(algoliasearch('D7O1MLLTAF', '44d0c0aac3c738bebb622150d1ec4ebf'));

  const [library, setLibrary] = React.useState(libraries[0]);

  const handleLibraryChange = (event) => {
    setLibrary(libraries.filter(i => i.key === event.target.value)[0]);
  };

  const [selectedTab, setSelectedTab] = React.useState('1');

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const [dialogOpen, setDialogOpen] = React.useState(false);

  const handleDialogOpen = () => {
    setDialogOpen(true);
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
      <Container maxWidth="md">
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h6">
              <Link
                underline="none"
                href="https://github.com/cppalliance/boost-gecko"
              >
                Boost.Gecko
              </Link>
            </Typography>
          </Grid>
          <Grid item xl={10} xs={8}>
            <FormControl fullWidth>
              <InputLabel>Library</InputLabel>
              <Select
                size="small"
                value={library.key}
                onChange={handleLibraryChange}
                label="Library"
              >
                {libraries.map(i => <MenuItem key={i.key} value={i.key}>{i.name}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xl={2} xs={4}>
            <Button
              fullWidth
              sx={{ textTransform: 'capitalize', height: 40 }}
              startIcon={<SearchIcon />}
              variant="outlined"
              onClick={handleDialogOpen}
            >
              Search...
            </Button>
          </Grid>
        </Grid>
      </Container>
      <Dialog
        fullScreen={dialogShouldBeFullScreen}
        keepMounted
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
          <Grid container spacing={2}>
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
                <Tab value="1" sx={{ textTransform: 'capitalize' }} label={library.name} />
                <Tab value="2" sx={{ textTransform: 'capitalize' }} label="Other Libraries" />
              </Tabs>
            </Grid>
          </Grid>
        </DialogTitle>
        <DialogContent sx={{ p: 2 }}>
          <Box hidden={selectedTab !== "1"} sx={{ pt: 1, typography: 'body1' }}>
            <Index indexName="all">
              <Configure
                hitsPerPage={30}
                filters={"library_key:" + library.key}
              />
              <CustomInfiniteHits />
            </Index>
          </Box>
          <Box hidden={selectedTab !== "2"} sx={{ pt: 1, typography: 'body1' }}>
            <Index indexName="all">
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
              <Button size="small" onClick={handleDialogClose}>Close</Button>
            </Grid>
          </Grid>
        </DialogActions>
      </Dialog>
    </InstantSearch >
  );
}

export default App;
