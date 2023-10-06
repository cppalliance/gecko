import { libraries } from './libraries';
import SearchButton from './Search/SearchButton';

import React from 'react';

import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Link from '@mui/material/Link';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';

function Demo() {
  const [library, setLibrary] = React.useState(libraries[0]);

  const handleLibraryChange = (event) => {
    setLibrary(libraries.filter((i) => i.key === event.target.value)[0]);
  };

  const [mode, setMode] = React.useState('light');
  const theme = React.useMemo(() =>
    createTheme({
      palette: {
        mode,
      }
    }), [mode]);

  const handleModeChange = (event) => {
    setMode(event.target.value);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth='md'>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Link variant='h6' underline='none' href='https://github.com/cppalliance/boost-gecko'>
              Boost.Gecko
            </Link>
          </Grid>
          <Grid item md={2} xs={3}>
            <FormControl fullWidth>
              <InputLabel>Theme</InputLabel>
              <Select size='small' value={mode} onChange={handleModeChange} label='Theme' sx={{ height: 36 }}>
                <MenuItem value='light'>
                  Light
                </MenuItem>
                <MenuItem value='dark'>
                  Dark
                </MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item md={8} xs={5}>
            <FormControl fullWidth>
              <InputLabel>Library</InputLabel>
              <Select size='small' value={library.key} onChange={handleLibraryChange} label='Library' sx={{ height: 36 }}>
                {libraries.map((i) => (
                  <MenuItem key={i.key} value={i.key}>
                    {i.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item md={2} xs={4}>
            <SearchButton
              versionWarning={false}
              library={library}
              urlPrefix={'https://www.boost.org/doc/libs/1_82_0'}
              algoliaIndex={'1_82_0'}
              alogliaAppId={'D7O1MLLTAF'}
              alogliaApiKey={'44d0c0aac3c738bebb622150d1ec4ebf'}
            />
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default Demo;
