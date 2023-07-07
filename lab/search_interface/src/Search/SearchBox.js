import React from 'react';

import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import grey from '@mui/material/colors/grey';
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
import Autocomplete from '@mui/material/Autocomplete';
import HistoryIcon from '@mui/icons-material/History';
import CircularProgress from '@mui/material/CircularProgress';

import { useSearchBox, useInstantSearch } from 'react-instantsearch-hooks-web';

let queryHookTimerId;

function SearchBox({ inputRef, recentSearches }) {
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

export default SearchBox;
