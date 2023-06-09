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

const searchClient = algoliasearch('D7O1MLLTAF', '44d0c0aac3c738bebb622150d1ec4ebf');

function CustomSearchBox(props) {
  const { currentRefinement, refine, } = useSearchBox(props);

  return (
    <TextField
      fullWidth
      size="small"
      type="search"
      label="Search..."
      value={currentRefinement}
      onChange={event => refine(event.currentTarget.value)}
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
  const [library, setLibrary] = React.useState(libraries[0].key);

  const handleLibraryChange = (event) => {
    setLibrary(event.target.value);
  };

  const [selectedTab, setSelectedTab] = React.useState('1');

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  return (
    <InstantSearch searchClient={searchClient}>
      <Container maxWidth="md">
        <Grid container spacing={2}>
          <Grid item xs={10}>
            <Typography variant="h5">
              <Link
                underline="none"
                href="https://github.com/cppalliance/boost-gecko"
              >
                Boost.Gecko
              </Link>
            </Typography>
          </Grid>
          <Grid item xs={2} sx={{ mt: 1 }}>
            <PoweredBy />
          </Grid>
          <Grid item xs={4}>
            <FormControl fullWidth>
              <InputLabel>Library</InputLabel>
              <Select
                size="small"
                value={library}
                onChange={handleLibraryChange}
                label="Library"
              >
                {libraries.map(i => <MenuItem key={i.key} value={i.key}>{i.name}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={8}>
            <CustomSearchBox />
          </Grid>
          <Grid item xs={12}>
            <Tabs
              value={selectedTab}
              onChange={handleTabChange}
              textColor="inherit"
              variant="fullWidth"
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab value="1" label={"Boost." + library} />
              <Tab value="2" label="Other Libraries" />
            </Tabs>
            <Box hidden={selectedTab !== "1"} sx={{ pt: 2, typography: 'body1' }}>
              <Index indexName="all">
                <Configure
                  hitsPerPage={30}
                  filters={"library_key:" + library}
                />
                <CustomInfiniteHits />
              </Index>
            </Box>
            <Box hidden={selectedTab !== "2"} sx={{ pt: 2, typography: 'body1' }}>
              <Index indexName="all">
                <Configure
                  hitsPerPage={30}
                  filters={"NOT library_key:" + library}
                />
                <CustomInfiniteHits />
              </Index>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </InstantSearch >
  );
}

export default App;
