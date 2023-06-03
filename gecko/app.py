from pathlib import Path
import re
import json

from .crawlers.quickbook import QuickBook


def create_algolia_records(library_key: str, sections: dict, boost_root: Path, boost_version: str):
    records = []
    for url, section in sections.items():
        url = url.replace(str(boost_root.resolve()), 'https://www.boost.org/doc/libs/' + boost_version)

        records.append({
            'type': 'content',
            'library_key': library_key,
            'boost_version': boost_version,
            'url': url,
            'content': re.sub(r'\s+', ' ', section['content']).strip(),
            'weight': {
                'pageRank': 0,
                'level': 100 - len(section['lvls']) * 10,
                'position': 0
            },
            'hierarchy': {
                'lvl0': section['lvls'][0] if len(section['lvls']) > 0 else None,
                'lvl1': section['lvls'][1] if len(section['lvls']) > 1 else None,
                'lvl2': section['lvls'][2] if len(section['lvls']) > 2 else None,
                'lvl3': section['lvls'][3] if len(section['lvls']) > 3 else None,
                'lvl4': section['lvls'][4] if len(section['lvls']) > 4 else None,
                'lvl5': section['lvls'][5] if len(section['lvls']) > 5 else None,
                'lvl6': section['lvls'][6] if len(section['lvls']) > 6 else None
            }})

    with open('./algolia_records/' + library_key + '.json', 'w', encoding='utf-8') as outfile:
        json.dump(records, outfile, indent=4)


if __name__ == "__main__":
    libraries = [
        'hof', 'bimap', 'circular_buffer', 'contract', 'convert', 'date_time', 'detail', 'dll', 'graph', 'msm',
        'multi_array', 'pool', 'safe_numerics', 'vmd', 'crc', 'asio', 'thread', 'xpressive', 'regex', 'spirit', 'core',
        'mpi', 'property_tree', 'heap', 'typeof', 'metaparse', 'intrusive', 'compute', 'geometry', 'random',
        'coroutine2', 'tti', 'phoenix', 'fusion', 'lockfree', 'test', 'multiprecision', 'poly_collection', 'json',
        'chrono', 'signals2', 'icl', 'optional', 'function_types', 'log', 'ratio', 'lexical_cast', 'proto', 'fiber',
        'local_function', 'python', 'type_traits', 'foreach', 'sort', 'yap', 'callable_traits', 'container',
        'scope_exit', 'coroutine', 'variant', 'beast', 'mysql', 'lambda', 'move', 'url', 'stl_interfaces', 'integer',
        'range', 'context', 'interprocess', 'atomic', 'histogram', 'align', 'config', 'tuple', 'units',
        'program_options', 'type_index', 'math', 'accumulators', 'bind', 'function', 'array', 'static_string', 'winapi',
        'algorithm', 'any', 'utility', 'process', 'conversion', 'stacktrace', 'pfr', 'type_erasure', 'static_assert',
        'tribool']
    boost_root = Path('../boost_1_82_0')
    BOOST_VERSION = '1_82_0'

    for library_key in libraries:
        crawler = QuickBook(boost_root)
        sections = crawler.crawl(library_key)
        create_algolia_records(library_key, sections, boost_root, BOOST_VERSION)
