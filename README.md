# Gecko

A crawler with the goal of creating a search index by crawling HTML documents for every library in the Boost release archive.

## How it works

It extracts contents with the correct hierarchy for each library and generates records like this:

```JSON
{
    "type": "content",
    "library_key": "asio",
    "library_name": "Asio",
    "boost_version": "1_82_0",
    "content": "To aid in debugging asynchronous programs, Boost.Asio provides support for handler ...",
    "weight": {
        "pageRank": 0,
        "level": 70,
        "position": 0
    },
    "hierarchy": {
        "lvl0": {
            "title": "Overview",
            "url": "https://www.boost.org/doc/libs/1_82_0/doc/html/boost_asio/overview.html"
        },
        "lvl1": {
            "title": "Core Concepts and Functionality",
            "url": "https://www.boost.org/doc/libs/1_82_0/doc/html/boost_asio/overview/core.html"
        },
        "lvl2": {
            "title": "Handler Tracking",
            "url": "https://www.boost.org/doc/libs/1_82_0/doc/html/boost_asio/overview/core/handler_tracking.html"
        },
        "lvl3": null,
        "lvl4": null,
        "lvl5": null,
        "lvl6": null
    }
}
```

## TODOs
- Writing developer documentation.
- Improving the project structure and making a generic interface for adding crawlers.
- Writing crawler for the remaining libraries.
- Considering a smarter approach for indexing libraries with unique structures that doesn't necessitate a dedicated crawler.
- Adding Test.
- Setting up the repository.
- Setting up CI.


## Uncovered libraries

```python
['compatibility', 'exception', 'filesystem', 'format', 'gil', 'graph_parallel', 'hana', 'iostreams', 'iterator', 'locale', 'mpl', 'nowide', 'outcome', 'polygon', 'preprocessor', 'ptr_container', 'serialization', 'tokenizer', 'wave']
```
