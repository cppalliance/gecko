import os
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def sanitize_title(title):
    title = re.sub('\s+', ' ', title).strip()

    if 'Header <' in title:
        title = title.replace('<', '')
        title = title.replace('>', '')

    # Workaround for Reference page in Boost.Beast
    if 'This Page Intentionally Left Blank' in title:
        return 'Reference'

    title = title.replace('¶', '')

    return title


def scrape_html_file(file_path: str, sections: dict) -> set:
    if not os.path.isfile(file_path):
        print("File doesn't exis", file_path)
        return []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

        if soup.select_one('body > .section > .index'):
            return []

        if soup.select_one('head > meta[http-equiv="refresh"]'):
            redirect_to = soup.select_one('body a').get("href")
            redirect_to = redirect_to.replace('https://www.boost.org/doc/libs/master/', '../../')
            return [urljoin(file_path, redirect_to)]

        up = soup.select_one('body > .spirit-nav > a[accesskey="u"]')
        if up and up.get('href') != '#':
            up = urljoin(file_path, up.get('href'))

        if soup.select_one('body > .refentry'):
            title = sanitize_title(soup.select_one('.refentry > .refnamediv > h2').text)

            for refsect1 in soup.select('.refentry > .refsect1'):
                anchor = refsect1.select_one('a').get('name')
                sub_title = sanitize_title(refsect1.select_one('h2').text)

                content = ''
                for sibling in refsect1.select_one('h2').find_next_siblings():
                    if sibling.has_attr('class') and 'refsect2' in sibling.get('class'):
                        break
                    content += sibling.get_text().strip() + ' '

                url = file_path + '#' + anchor
                lvls = [sub_title, title]
                sections[url] = {'lvls': lvls, 'content': content, 'up': up}

                for refsect2 in refsect1.select('.refsect2'):
                    anchor = refsect2.select_one('a').get('name')
                    sub_title = sanitize_title(refsect2.select_one('h3').text)

                    content = ''
                    for sibling in refsect2.select_one('h3').find_next_siblings():
                        if sibling.has_attr('class') and 'refsect3' in sibling.get('class'):
                            break
                        content += sibling.get_text().strip() + ' '

                    url = file_path + '#' + anchor
                    lvls = [sub_title, title]
                    sections[url] = {'lvls': lvls, 'content': content, 'up': up}

        else:
            for anchor in soup.select('h1 > a.headerlink, h2 > a.headerlink, h3 > a.headerlink, h4 > a.headerlink, h5 > a.headerlink, h6 > a.headerlink, h1 > a.link, h2 > a.link, h3 > a.link, h4 > a.link, h5 > a.link, h6 > a.link, h1.title > a:first-child, h2.title > a:first-child, h3.title > a:first-child, h4.title > a:first-child, h5.title > a:first-child, h6.title > a:first-child'):
                # titlepage headers
                header = anchor.find_parent(class_='titlepage')

                # regular headers
                if not header:
                    header = anchor.parent
                    if header.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        continue

                content = ''
                for sibling in header.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break

                    if sibling.has_attr('class') and 'section' in sibling.get('class'):
                        break

                    if sibling.has_attr('class') and 'toc' in sibling.get('class'):
                        continue

                    content += sibling.get_text().strip() + ' '

                if anchor.has_attr('href') and header != soup.select_one('.body > .section:first-child > h1'):
                    url = urljoin(file_path, anchor.get('href'))
                elif header != soup.select_one('body > div > .titlepage') and header != soup.select_one('.body > .section:first-child > h1'):
                    url = file_path + '#' + anchor.get('name')
                else:
                    url = file_path

                if soup.select_one('body > div > .titlepage .title'):
                    lvls = [sanitize_title(anchor.parent.text), sanitize_title(soup.select_one('body > div > .titlepage .title').text)]
                elif soup.select_one('.body > .section:first-child > h1'):
                    lvls = [sanitize_title(anchor.parent.text), sanitize_title(soup.select_one('.body > .section:first-child > h1').text)]
                else:
                    lvls = [sanitize_title(anchor.parent.text)]

                sections[url] = {'lvls': lvls, 'content': content, 'up': up}

        releative_links = []
        for a in soup.select('a:not([href^="http"])'):
            releative_links.append(urljoin(file_path, a.get('href')))

        return releative_links


def to_chunks(xs, n):
    n = max(1, n)
    return (xs[i:i+n] for i in range(0, len(xs), n))


def create_algolia_records(library: str, sections: dict, boost_root_path: str, boost_version: str):
    records = []
    for url, section in sections.items():
        url = url.replace(boost_root_path, 'https://www.boost.org/doc/libs/' + boost_version)

        records.append({
            'type': 'content',
            'library': library,
            'boost_version': boost_version,
            'url': url,
            'content': re.sub('\s+', ' ', section['content']).strip(),
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

    with open('./records/' + library + '.json', 'w') as outfile:
        json.dump(records, outfile, indent=4)


def populate_up(sections: dict, section: dict):
    if section['up'] not in sections:
        section['up'] = None
        return

    if 'up' in sections[section['up']]:
        populate_up(sections, sections[section['up']])

    section['lvls'].extend(sections[section['up']]['lvls'])
    section['up'] = None


if __name__ == "__main__":

    for library in [
        'hof', 'bimap', 'circular_buffer', 'contract', 'convert', 'date_time', 'detail', 'dll', 'graph', 'msm', 'multi_array', 'pool', 'property_map', 'safe_numerics', 'vmd', 'crc', 'asio',
        'thread', 'xpressive', 'regex', 'spirit', 'core', 'mpi', 'property_tree', 'heap', 'typeof', 'metaparse', 'intrusive', 'compute', 'geometry', 'random', 'coroutine2', 'tti', 'phoenix', 'fusion',
        'lockfree', 'test', 'multiprecision', 'poly_collection', 'json', 'chrono', 'signals2', 'icl', 'optional', 'function_types', 'log', 'ratio', 'lexical_cast', 'proto', 'fiber', 'local_function',
        'python', 'type_traits', 'foreach', 'sort', 'yap', 'callable_traits', 'container', 'scope_exit', 'coroutine', 'variant', 'beast', 'mysql', 'lambda', 'move', 'url', 'stl_interfaces', 'integer',
        'range', 'context', 'interprocess', 'atomic', 'histogram', 'align', 'config', 'tuple', 'units', 'program_options', 'type_index', 'math', 'accumulators', 'bind', 'function', 'array',
            'static_string', 'winapi', 'algorithm', 'any', 'utility', 'process', 'conversion', 'stacktrace', 'pfr', 'type_erasure', 'static_assert', 'tribool']:

        boost_root_path = '../boost_1_82_0'
        boost_root_path = os.path.abspath(boost_root_path)

        links_to_scrape = set()
        scraped_links = set()
        sections = dict()

        links_to_scrape.add(boost_root_path + '/libs/' + library + '/index.html')

        if library == 'tribool':
            links_to_scrape.add(boost_root_path + '/libs/' + 'logic' + '/index.html')

        while len(links_to_scrape) > 0:
            link = links_to_scrape.pop()
            scraped_links.add(link)

            releative_links = scrape_html_file(file_path=link, sections=sections)

            for link in releative_links:
                # remvoe anchor
                link = urlparse(link).path

                if not link.endswith(".html"):
                    continue

                if library not in link.lower() and library.replace('_', '') not in link.lower():
                    continue

                if link not in scraped_links:
                    links_to_scrape.add(link)

        # populate hierachy
        for url, section in sections.items():
            populate_up(sections, section)

        for url, section in sections.items():
            section['lvls'] = list(dict.fromkeys(section['lvls']))
            section['lvls'].pop()
            section['lvls'].reverse()

        create_algolia_records(library=library,
                            sections=sections,
                            boost_root_path=boost_root_path,
                            boost_version='1_82_0')
