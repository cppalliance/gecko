![Gecko](img/logo.png)

# Gecko

A crawler with the goal of creating a search index by crawling HTML documents for every library in the Boost release archive.

## How it works

It extracts contents with the correct hierarchy for each library and generates records like this:

```JSON
{
    "type": "content",
    "library_key": "url",
    "library_name": "URL",
    "content": "this->has_fragment() == false && this->encoded_fragment() == \"\"",
    "weight": {
        "pageRank": 0,
        "level": 60,
        "position": 0
    },
    "hierarchy": {
        "lvl0": {
            "title": "Reference",
            "path": "libs/url/doc/html/url/ref.html"
        },
        "lvl1": {
            "title": "url",
            "path": "libs/url/doc/html/url/ref/boost__urls__url.html"
        },
        "lvl2": {
            "title": "url::remove_fragment",
            "path": "libs/url/doc/html/url/ref/boost__urls__url/remove_fragment.html"
        },
        "lvl3": {
            "title": "Postconditions",
            "path": "libs/url/doc/html/url/ref/boost__urls__url/remove_fragment.html#url.ref.boost__urls__url.remove_fragment.postconditions"
        },
        "lvl4": null,
        "lvl5": null,
        "lvl6": null
    }
}
```

## TODOs

- Writing developer documentation.
- Considering a smarter approach for indexing libraries with unique structures that doesn't necessitate a dedicated crawler.
- Adding Test.
- Setting up the repository.
- Setting up CI.

## Acknowledgments

- [Tomasz Kalisiak](https://github.com/Bobini1) for adding a crawler for Boost.Hana library.

