#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# Convert from html to on disk format
# Copyright (C) 2023 Chris Clark - clach04

import json
import logging
import os
import sys

try:
    import hashlib
    #from hashlib import md5
    md5 = hashlib.md5
except ImportError:
    # pre 2.6/2.5
    from md5 import new as md5

import logging
import os
import sys
import urllib
try:
    # Py2
    from urllib import quote_plus, urlretrieve  #TODO is this in urllib2?
    from urllib2 import urlopen, Request, HTTPError
except ImportError:
    # Py3
    from urllib.error import HTTPError
    from urllib.request import urlopen, urlretrieve, Request
    from urllib.parse import quote_plus

import readability
from readability import Document  # https://github.com/buriy/python-readability/   pip install readability-lxml

try:
    import trafilatura  # readability alternative, note additional module htmldate available for date processing - pip install  requests trafilatura
    """
    https://github.com/adbar/trafilatura

    pip install  requests trafilatura

    Successfully installed certifi-2023.5.7 charset-normalizer-3.2.0 courlan-0.9.3 dateparser-1.1.8 htmldate-1.4.3 idna-3.4 justext-3.0.0 langcodes-3.3.0 lxml-4.9.3 p
    python-dateutil-2.8.2 pytz-2023.3 regex-2023.6.3 requests-2.31.0 six-1.16.0 tld-0.13 trafilatura-1.6.1 tzdata-2023.3 tzlocal-5.0.1 urllib3-2.0.3
    """
except ImportError:
    # Py2 not supported
    trafilatura = None


from markdownify import markdownify as md  # https://github.com/matthewwithanm/python-markdownify  pip install markdownify
# https://github.com/matthewwithanm/python-markdownify  pip install markdownify
# Successfully installed beautifulsoup4-4.12.2 markdownify-0.11.6 soupsieve-2.4.1

"""Py2
pip install requests
pip install beautifulsoup4==4.9.3
pip install markdownify
pip install readability-lxml

py3
    pip install requests beautifulsoup4 markdownify readability-lxml
    pip install requests beautifulsoup4==4.9.3 markdownify readability-lxml

Successfully installed beautifulsoup4-4.12.2 certifi-2023.5.7 chardet-5.0.0 charset-normalizer-2.0.12 cssselect-1.1.0 idna-3.4 lxml-4.9.3 markdownify-0.11.6 readability-lxml-0.8.1 requests-2.27.1 soupsieve-2.3.2.post1 urllib3-1.26.16
"""


try:
    import pypub  # https://github.com/clach04/pypub
except ImportError:
    # optional
    pypub = None


log = logging.getLogger("w2d")
log.setLevel(logging.DEBUG)
disable_logging = False
#disable_logging = True
if disable_logging:
    log.setLevel(logging.NOTSET)  # only logs; WARNING, ERROR, CRITICAL

ch = logging.StreamHandler()  # use stdio

formatter = logging.Formatter("logging %(process)d %(thread)d %(asctime)s - %(filename)s:%(lineno)d %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)


def urllib_get_url(url, headers=None):
    """
    @url - web address/url (string)
    @headers - dictionary - optional
    """
    log.debug('get_url=%r', url)
    #log.debug('headers=%r', headers)
    response = None
    try:
        if headers:
            request = Request(url, headers=headers)
        else:
            request = Request(url)  # may not be needed
        response = urlopen(request)
        url = response.geturl()  # may have changed in case of redirect
        code = response.getcode()
        #log("getURL [{}] response code:{}".format(url, code))
        result = response.read()
        return result
    finally:
        if response != None:
            response.close()

def safe_mkdir(newdir):
    result_dir = os.path.abspath(newdir)
    try:
        os.makedirs(result_dir)
    except OSError as info:
        if info.errno == 17 and os.path.isdir(result_dir):
            pass
        else:
            raise

cache_dir = os.environ.get('W2D_CACHE_DIR', 'scrape_cache')
safe_mkdir(cache_dir)

def hash_url(url):
    m = md5()
    m.update(url.encode('utf-8'))
    return m.hexdigest()

def get_url(url, filename=None, force=False, cache=True):
    """Get a url, optionally with caching
    TODO get headers, use last modified date (save to disk file as meta data), return it (and other metadata) along with page content
    """
    #filename = filename or 'tmp_file.html'
    filename = filename or os.path.join(cache_dir, hash_url(url))
    ## cache it
    if force or not os.path.exists(filename):
        log.debug('getting web page %r', url)
        # TODO grab header information
        # TODO error reporting?

        use_requests = False
        if use_requests:
            response = requests.get(url)
            page = response.text.encode('utf8')  # FIXME revisit this - cache encoding
        else:
            # headers to emulate Firefox - actual headers from real browser
            headers = {
                #'HTTP_HOST': 'localhost:8000',
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'HTTP_ACCEPT': '*/*',
                'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.5',
                'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
                'HTTP_SERVICE_WORKER': 'script',
                'HTTP_CONNECTION': 'keep-alive',
                'HTTP_COOKIE': 'js=y',  # could be problematic...
                'HTTP_SEC_FETCH_DEST': 'serviceworker',
                'HTTP_SEC_FETCH_MODE': 'same-origin',
                'HTTP_SEC_FETCH_SITE': 'same-origin',
                'HTTP_PRAGMA': 'no-cache',
                'HTTP_CACHE_CONTROL': 'no-cache'
            }

            page = urllib_get_url(url, headers=headers)

        if cache:
            f = open(filename, 'wb')
            f.write(page)
            f.close()
            # TODO log hash and original url to an index of some kind (sqlite3 db probably best)
    else:
        log.debug('getting cached file %r', filename)
        f = open(filename, 'rb')
        page = f.read()
        f.close()
    log.debug('page %d bytes', len(page))  # TODO human bytes
    return page


FORMAT_MARKDOWN = 'md'  # Markdown
FORMAT_HTML = 'html'  # (potentiall) raw html/xhtml only - no external images, fonts, css, etc.
FORMAT_EPUB = 'epub'  # epub2
FORMAT_ALL = 'all'  # all of the supported formats in SUPPORTED_FORMATS

SUPPORTED_FORMATS = [
    FORMAT_HTML,
    FORMAT_MARKDOWN,  # TODO review should this be optional?
]
if pypub:
    SUPPORTED_FORMATS += [FORMAT_EPUB]

def safe_filename(filename, replacement_char='_'):
    """safe filename for almost any platform, NOTE filename NOT pathname
    aka slugify()

        filter option with allow:

            safechars = string.letters + string.digits + " -_."
            return filter(lambda c: c in safechars, inputFilename)

            '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            >>> filename = "This Is a (valid) - filename%$&$ .txt"
            >>> ''.join(c for c in filename if c in valid_chars)

        replace '-_' and '_-' with '_'

        remove dupes: ''.join(ch for ch, _ in itertools.groupby(foo))

        remove names:
            * https://en.wikipedia.org/wiki/Filename#In_Windows
            * https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file?redirectedfrom=MSDN
                blocked_filenames = CON, PRN, AUX, NUL, COM0, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, LPT0, LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9'
                and NULL for good measue

            name.startswith(....
                then prix with '_'

        max len: 255 - trim down - maybe less as missing extension and prefix which will be tacked on. Make this an input?
    """
    # TODO replace with an allow list, rather than block list like below. Originally intended to allow unicode characters. new plan, alphanumeric with , '_', '-',- maybe not ' ' and '.'? and replace with '_' if not those. then restrict to single instances of '_', and disallow DOS special names like 'con', 'con.txt', 'con.c'...
    result = []
    last_char = ''
    for x in filename:
        if not(x.isalnum() or x in '-_'):
            x = replacement_char
        if x not in ['-', replacement_char] or last_char not in ['-', replacement_char]:
            # avoid duplicate '_'
            result.append(x)
        last_char = x

    return ''.join(result)


def process_page(url, content=None, output_format=FORMAT_MARKDOWN, raw=False, output_filename=None, title=None, filename_prefix=None):
    """Process html content, writes to disk
    TODO add option to pass in file, rather than filename
    """

    if output_format not in SUPPORTED_FORMATS:
        raise NotImplementedError('output_format %r not supported (or missing dependency)' % output_format)

    assert url.startswith('http')  # FIXME DEBUG
    if content is None:
        # TODO handle "file://" URLs? see FIXME above
        if url.startswith('http'):
            page_content = get_url(url)
        else:
            # assume read file local filename
            f = open(url, 'rb')
            page_content = f.read()
            f.close()

        content = page_content.decode('utf-8')  # FIXME revisit this - cache encoding


    # * python-readability does a great job at
    #   extracting main content as html
    # * trafilatura does a great job at extracting meta data, but content
    #   is not usable (either not html or text that looks like Markdown
    # with odd paragrah spacing (or lack of))
    #
    # Use both for now
    if trafilatura:
        doc_metadata = trafilatura.bare_extraction(content, include_links=True, include_formatting=True, include_images=True, include_tables=True, with_metadata=True, url=url)
    else:
        doc_metadata = None
    #print(doc_metadata)

    if not raw:
        # try and extract main content, throw away cruft

        doc = Document(content)  # python-readability

        content = doc.summary()  # Unicode string
        # NOTE at this point any head that was in original is now missing, including title information
        if not doc_metadata:
            """We have:
                .title() -- full title
                .short_title() -- cleaned up title
                .content() -- full content
                .summary() -- cleaned up content
            """
            doc_metadata = {
                'title': doc.short_title(),  # match trafilatura
                'description': doc.title(),
                'author': 'Unknown Author',
                'date': 'UnknownDate',  # TODO use now? Ideally if had http headers could use last-updated
            }
    #print('%s' % json.dumps(doc_metadata, indent=4))  # TODO debug logging

    title = title or doc_metadata['title']

    print(output_format)  # TODO logging
    if not output_filename:
        filename_prefix = filename_prefix or ''
        output_filename = '%s%s.%s' % (filename_prefix, safe_filename(title), output_format)
    print(output_filename)  # TODO logging

    if output_format == FORMAT_HTML:
        out_bytes = content.encode('utf-8')
    elif output_format == FORMAT_MARKDOWN:
        # TODO TOC?
        markdown_text = '# %s\n\n%s %s\n\n%s\n\n' % (doc_metadata['title'], doc_metadata['author'], doc_metadata['date'], doc_metadata['description'])
        if doc_metadata.get('image'):
            markdown_text += '![alt text - maybe use title but need to escape brackets?](%s)\n\n' % (doc_metadata['image'],)
        markdown_text += md(content.encode('utf-8'))
        out_bytes = markdown_text.encode('utf-8')
        print(type(out_bytes))
    elif output_format == FORMAT_EPUB:
        print('WARNING epub output is work-in-progress and problematic due to html2epub issues')
        # ... wikipedia link fixing is not great
        my_epub = pypub.Epub(title)
        #my_chapter = pypub.create_chapter_from_url(url)  # NOTE does network IO
        my_chapter = pypub.create_chapter_from_string(content, url=url, title=title)
        my_epub.add_chapter(my_chapter)
        my_epub.create_epub('.', epub_name=output_filename[:-(len(FORMAT_EPUB)+1)])  # pypub does NOT want extension specified, strip '.epub' - NOTE requires fix for https://github.com/wcember/pypub/issues/29

    #import pdb; pdb.set_trace()  # DEBUG

    if output_format != FORMAT_EPUB:
        f = open(output_filename, 'wb')
        f.write(out_bytes)
        f.close()

    # FIXME need epub filename
    result_metadata = {
        'title': doc_metadata['title'],
        'description': doc_metadata['description'],
        'author': doc_metadata['author'],
        'date': doc_metadata['date'],
        'filename': output_filename,
    }

    debug_trafilatura = os.environ.get('W2D_DEBUG_TRAFILATURA', False)
    if debug_trafilatura and doc_metadata.get('text') and output_format == FORMAT_MARKDOWN:
        f = open(output_filename + '_tr.txt', 'wb')
        f.write(doc_metadata.get('text').encode('utf-8'))
        f.close()

    return result_metadata

def dump_url(url, output_format=FORMAT_MARKDOWN, raw=False, filename_prefix=None):
    print(url)  # FIXME logging

    if output_format == FORMAT_ALL:
        output_format_list = SUPPORTED_FORMATS
    else:
        output_format_list = [output_format]

    for output_format in output_format_list:
        result_metadata = process_page(url=url, output_format=output_format, raw=raw, filename_prefix=filename_prefix)
    return result_metadata  # the most recent one for output_format == FORMAT_ALL


def dump_urls(urls, output_format=FORMAT_MARKDOWN):
    for url in urls:
        # TODO capture result_metadata? return as list, dictionary on filename?
        dump_url(url, output_format=output_format)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))

    urls = argv[1:]  # no argument processing (yet)
    print(urls)
    if not urls:
        # demo
        urls = [
        'http://www.pcgamer.com/2012/08/09/an-illusionist-in-skyrim-part-1/',
        ]

    output_format = os.environ.get('W2D_OUTPUT_FORMAT', FORMAT_MARKDOWN)
    dump_urls(urls, output_format=output_format)

    return 0


if __name__ == "__main__":
    sys.exit(main())

