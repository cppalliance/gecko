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
- Improving project structure and making a generic interface for adding crawlers.
- Writing crawler for remaining libraries.
- Considering a smarter approach to indexing libraries with unique structures that doesn't necessitate a dedicated crawler.
- Refactoring current crawlers (they look horrible).
- Adding Configuration.
- Adding Test.
- Setting up the repository.
- Setting up CI.


## Covered libraries

### QuickBook

```python
['accumulators', 'algorithm', 'align', 'any', 'array', 'asio', 'atomic', 'beast', 'bimap', 'bind', 'callable_traits', 'chrono', 'circular_buffer', 'compute', 'config', 'container', 'context', 'contract', 'conversion', 'convert', 'core', 'coroutine', 'coroutine2', 'crc', 'date_time', 'detail', 'dll', 'fiber', 'foreach', 'function_types', 'function', 'fusion', 'geometry', 'graph', 'heap', 'histogram', 'hof', 'icl', 'integer', 'interprocess', 'intrusive', 'json', 'lambda', 'lexical_cast', 'local_function', 'lockfree', 'log', 'math', 'metaparse', 'move', 'mpi', 'msm', 'multi_array', 'multiprecision', 'mysql', 'optional', 'pfr', 'phoenix', 'poly_collection', 'pool', 'process', 'program_options', 'property_map', 'property_tree', 'proto', 'python', 'random', 'range', 'ratio', 'regex', 'safe_numerics', 'scope_exit', 'signals2', 'sort', 'spirit', 'stacktrace', 'static_assert', 'static_string', 'stl_interfaces', 'test', 'thread', 'tribool', 'tti', 'tuple', 'type_erasure', 'type_index', 'type_traits', 'typeof', 'units', 'url', 'utility', 'variant', 'vmd', 'winapi', 'xpressive', 'yap']
```

### AsciiDoc

```python
['assert', 'container_hash', 'describe', 'endian', 'io', 'lambda2', 'leaf', 'mp11', 'predef', 'qvm', 'smart_ptr', 'system', 'throw_exception', 'unordered', 'variant2']
```

## Uncovered libraries

```python
['assign', 'compatibility', 'concept_check', 'dynamic_bitset', 'exception', 'filesystem', 'flyweight', 'format', 'functional', 'gil', 'graph_parallel', 'hana', 'iostreams', 'iterator', 'locale', 'mpl', 'multi_index', 'nowide', 'numeric', 'outcome', 'parameter_python''parameter', 'polygon', 'preprocessor', 'property_map', 'ptr_container', 'rational', 'serialization', 'statechart', 'timer', 'tokenizer', 'uuid', 'wave']
```
