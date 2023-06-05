# Gecko

A crawler with the goal of creating a search index by crawling HTML documents for every library in the Boost release archive.

## How it works

It extracts contents with the correct hierarchy for each library and generates records like this:

```JSON
{
    "type": "content",
    "library": "hof",
    "boost_version": "1_82_0",
    "url": "https://www.boost.org/doc/libs/1_82_0/libs/hof/doc/html/doc/src/definitions.html#function-adaptor",
    "content": "A Function Adaptor takes a function(or functions) and returns a new function with enhanced capability. Each adaptor has a functional form with a corresponding class with _adaptor appended to it: template<class... Fs> FunctionAdaptor_adaptor<Fs...> FunctionAdaptor(Fs...); Both the functional form and the class form can be used to construct the adaptor.",
    "weight": {
        "pageRank": 0,
        "level": 70,
        "position": 0
    },
    "hierarchy": {
        "lvl0": "Overview",
        "lvl1": "Definitions",
        "lvl2": "Function Adaptor",
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
