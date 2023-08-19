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
import subprocess
import sys
import urllib
try:
    # Py3
    from urllib.error import HTTPError
    from urllib.request import urlopen, urlretrieve, Request
    from urllib.parse import quote_plus
    from urllib.parse import urlencode
except ImportError:
    # Py2
    from urllib import quote_plus, urlretrieve  #TODO is this in urllib2?
    from urllib2 import urlopen, Request, HTTPError
    from urllib import urlencode


def fake_module(name):
    # Fail with a clear message (possibly at an unexpected time)
    class MissingModule(object):
        def __getattr__(self, attr):
            raise ImportError('No module named %s' % name)

        def __bool__(self):  # Not sure __nonzero__ check was working in py3
            # if checks on this will fail
            return False
        __nonzero__ = __bool__

    return MissingModule()

#import readability
try:
    import readability  # https://github.com/buriy/python-readability/   pip install readability-lxml
except ImportError:
    readability = fake_module('readability')


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


try:
    import markdownify  # https://github.com/matthewwithanm/python-markdownify  pip install markdownify
except ImportError:
    markdownify = fake_module('markdownify')
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

from ._version import __version__, __version_info__


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

log.info('%s version %s', __name__, __version__)
log.info('Python %r on %r', sys.version, sys.platform)


is_win = sys.platform.startswith('win')

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

# headers to emulate Firefox - actual headers from real browser
MOZILLA_FIREFOX_HEADERS = {
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
            headers = MOZILLA_FIREFOX_HEADERS

            page = urllib_get_url(url, headers=headers)

        if cache:
            f = open(filename, 'wb')
            f.write(page)
            f.close()
            # initial index - needs reworking - if filename passed in, hash is not used
            index_filename = os.path.join(os.path.dirname(filename), 'index.tsv')
            f = open(index_filename, 'ab')
            entry = '%s\t%s\n' % (os.path.basename(filename), url)
            f.write(entry.encode('utf-8'))
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
    FORMAT_EPUB,  # assume pandoc available
]
"""
if pypub:
    SUPPORTED_FORMATS += [FORMAT_EPUB]
"""

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


def pandoc_epub_output_function(output_filename, url=None, content=None, title='Title Unknown', content_format=FORMAT_HTML):
    """url ignored, content expected
    TODO sanity checks
    """
    #echo hello world | pandoc -f gfm -o test.epub --metadata "title=test"
    pandoc_input_format = content_format
    if content_format != FORMAT_HTML:
        # Assume markdown, GitHub Flavored
        pandoc_input_format = 'gfm'

    if is_win:
        expand_shell = True  # avoid pop-up black CMD window
    else:
        expand_shell = False
    pandoc_exe = 'pandoc'  # TODO pick up from environ
    cmd = [pandoc_exe, '-f', pandoc_input_format, '-o', output_filename, '--metadata', 'title=%s' % title]
    p = subprocess.Popen(cmd, shell=expand_shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # time out is py3 (3.3+?)
    """
    try:
        timeout = 15
        timeout = 3
        stdout_value, stderr_value = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        #stdout_value, stderr_value = p.communicate()  # just hangs again
        stdout_value, stderr_value = '', ''
    """
    stdout_value, stderr_value = p.communicate(input=content.encode('utf-8'))

    if p.returncode == 0 and stdout_value == b'' and stderr_value == b'':
        # success!
        pass
    else:
        raise NotImplementedError('Error handling, %r, %r, %r' % (p.returncode, stderr_value, stdout_value))

def pypub_epub_output_function(output_filename, url=None, content=None, title='Title Unknown', content_format=FORMAT_HTML):
    """
    content_format - the format of content (or what url will return)
    """
    print('WARNING epub output is work-in-progress and problematic due to html2epub issues')
    # sanity checks needed? e.
    assert content_format == FORMAT_HTML  # TODO replace with actual check and/or transformation code, i.e. convert markdown code to html
    # ... wikipedia link fixing is not great
    my_epub = pypub.Epub(title)
    #my_chapter = pypub.create_chapter_from_url(url)  # NOTE does network IO
    my_chapter = pypub.create_chapter_from_string(content, url=url, title=title)
    my_epub.add_chapter(my_chapter)
    my_epub.create_epub('.', epub_name=output_filename[:-(len(FORMAT_EPUB)+1)])  # pypub does NOT want extension specified, strip '.epub' - NOTE requires fix for https://github.com/wcember/pypub/issues/29


MP_URL = os.environ.get('MP_URL', 'http://localhost:3000/parser')  # maybe remove the parser piece... rename OS var?

"""https://github.com/HenryQW/mercury-parser-api

GET /parser?url=[required:url]&contentType=[optional:contentType]&headers=[optional:url-encoded-headers]

only accepts url (other options available) but can not feed html into it
upstream appears to accept html (body)
same for the other server implementation

    docker exec -it mercury_postlight_parser /app/node_modules/.bin/postlight-parser
"""

def gen_postlight_url(url, format=None, headers=None, postlight_server_url=MP_URL):
    """format - valid values are 'html', 'markdown', and 'text'
    where markdown returns GitHub-flavored Markdown
    headers - a dict
    """
    # TODO clone and replace 'HTTP_USER_AGENT' with 'USER_AGENT' due to postlight behavior?
    # NOTE this still doesn't do anything useful with agent due to postlight behavior...
    if headers and 'USER-AGENT' not in headers and 'HTTP_USER_AGENT' in headers:
        headers = headers.copy()
        headers['USER-AGENT'] = headers['HTTP_USER_AGENT']  # see https://github.com/postlight/parser/issues/748
    headers_json_str = json.dumps(headers, separators=(',', ':'))  # convert to json, with no spaces
    vars = {
        'url': url,
        #'contentType': format,
        #'headers': headers_json_str,
    }
    if headers:
        vars['headers'] = headers_json_str
    if format:
        vars['contentType'] = format

    result = postlight_server_url + '?' + urlencode(vars)
    return result


## TODO raw extractor that does nothing other than return original content
## TODO support extractors that only return html (or only markdown)
## TODO in process support html2md then md2html as a cleaner
def extractor_readability(url, page_content=None, format=FORMAT_HTML, title=None):
    """if content is provided, try and use that instead of pulling from URL - NOTE not guaranteed
    """
    # TODO use title (is this a hint or an override, I think the later)
    output_format = format or FORMAT_HTML

    assert output_format in (FORMAT_HTML, FORMAT_MARKDOWN), '%r not in %r' % (output_format, (FORMAT_HTML, FORMAT_MARKDOWN))  # TODO replace with actual check
    assert url.startswith('http')  # FIXME DEBUG

    if page_content is None:
        # TODO handle "file://" URLs? see FIXME above
        if url.startswith('http'):
            page_content_bytes = get_url(url)
        else:
            # assume read file local filename
            f = open(url, 'rb')
            page_content_bytes = f.read()
            f.close()

        page_content = page_content_bytes.decode('utf-8')  # FIXME revisit this - cache encoding

    doc_metadata = None
    # * python-readability does a great job at
    #   extracting main content as html
    # * trafilatura does a great job at extracting meta data, but content
    #   is not usable (either not html or text that looks like Markdown
    # with odd paragraph spacing (or lack of))
    #
    # Use both for now
    if trafilatura:
        doc_metadata = trafilatura.bare_extraction(page_content, include_links=True, include_formatting=True, include_images=True, include_tables=True, with_metadata=True, url=url)
        # TODO cleanup and return null for unknown entries

    doc = readability.Document(page_content)

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
            'author': None,
            'date': None,  # TODO use now? Ideally if had http headers could use last-updated
        }

    if output_format == FORMAT_MARKDOWN:
        content = markdownify.markdownify(content.encode('utf-8'))

    postlight_metadata = {
        "title": doc_metadata['title'],
        "author": doc_metadata['author'],
        "date_published": doc_metadata['date'],
        "dek": None,
        "lead_image_url": None,  # FIXME
        "content": content,
        "next_page_url": None,
        "url": url,
        "domain": None,  # FIXME
        "excerpt": doc_metadata['description'],  # TODO review this
        "word_count": 0,  # FIXME make None for now to make clear not attempt made?
        "direction": "ltr",  # hard coded
        "total_pages": 1,  # hard coded
        "rendered_pages": 1  # hard coded
    }
    return postlight_metadata


def extractor_postlight_exe(url, page_content=None, format=FORMAT_HTML, title=None):
    """TODO implement js command line tool that can take content and skip url usage,
    See "Feature: parse support stdin/files" https://github.com/postlight/parser/issues/651
    """
    POSTLITE_EXE = os.environ.get('W2D_POSTLITE_EXE', 'C:\\code\\js\\mercury-parser-api\\node_modules\\.bin\\postlight-parser.cmd')  # FIXME
    # C:\code\js\mercury-parser-api\node_modules\.bin\postlight-parser.cmd
    commands_list = [POSTLITE_EXE, url]
    # FIXME validate format here (AGAIN). sanity check url too? does shell false help?
    commands_list += ['--format=%s' % format]
    headers = MOZILLA_FIREFOX_HEADERS
    if headers and 'USER-AGENT' not in headers and 'HTTP_USER_AGENT' in headers:
        headers = headers.copy()
        headers['USER-AGENT'] = headers['HTTP_USER_AGENT']  # see https://github.com/postlight/parser/issues/748
    for header_key in headers:
        header_value = headers[header_key]
        commands_list.append('--header.%s=%s' % (header_key, header_value))

    ## FIXME other args
    proc = subprocess.Popen(commands_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    #proc = subprocess.Popen(commands_list, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    stdout_value, stderr_value = proc.communicate()
    if stderr_value == '':
        stderr_value = None
    if stderr_value:
        raise NotImplementedError('error postlight commandline failed %r', stderr_value)
    if stdout_value:
        stdout_value = stdout_value.decode('utf-8')
    postlight_metadata = json.loads(stdout_value)
    return postlight_metadata



def extractor_postlight(url, page_content=None, format=FORMAT_HTML, title=None, no_cache=False):
    """Extract main article/content from url/content using Postlight (nee Mecury) Parser
    content is currenrtly ignored, postlight APIs do not expose the file access that the base API does have. NOTE content **maybe** used, it may be ignored depending on the extractor used (i.e. may scrape URL even if content provided).
    return postlight dict?
    """
    # TODO use title (is this a hint or an override, I think the later)
    postlight_format = 'html'
    if format == FORMAT_MARKDOWN:
        # request was for markdown, rely on postlight to convert to markdown for us
        postlight_format = 'markdown'  # test - this removes the need for other stuff...
    tmp_url = gen_postlight_url(url, format=postlight_format, headers=MOZILLA_FIREFOX_HEADERS)
    """TODO / FIXME set headers param
    Test case = https://www.richardkmorgan.com/2023/07/gone-but-not-forgotten/

{
"error": true,
"messages": "socket hang up"
}

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
    """
    if no_cache:
        postlight_json = get_url(tmp_url, force=True, cache=False)
    else:
        postlight_json = get_url(tmp_url)

    postlight_metadata = json.loads(postlight_json)
    return postlight_metadata
    #print(json.dumps(postlight_metadata, indent=4))


def process_page(url, content=None, output_format=FORMAT_MARKDOWN, raw=False, extractor_function=extractor_readability, output_filename=None, title=None, filename_prefix=None, epub_output_function=pypub_epub_output_function):
    """Process html content, writes to disk
    TODO add option to pass in file, rather than filename
    extractor - will replace raw
    NOTE content **maybe** used, it may be ignored depending on the extractor used (i.e. may scrape URL even if content provided).
    """

    if output_format not in SUPPORTED_FORMATS:
        raise NotImplementedError('output_format %r not supported (or missing dependency)' % output_format)
    if output_format == FORMAT_EPUB:
        content_format = os.environ.get('W2D_INTERMEDIATE_FORMAT', FORMAT_HTML)
    else:
        content_format = output_format

    assert url.startswith('http')  # FIXME DEBUG

    doc_metadata = None  # should be empty dict? None causes immediate failure which is handy for debugging

    if not raw:
        postlight_metadata = extractor_function(url, page_content=content, format=content_format, title=title)
        #print(json.dumps(postlight_metadata, indent=4))

        # TODO old dict format, replace
        content = postlight_metadata['content']  # TODO or content? FIXME handle case where postlight fails to get data
        doc_metadata = {
            'author': postlight_metadata['author'],
            'date': postlight_metadata['date_published'],  # maybe None/Null -- 'UnknownDate',  # TODO use now? Ideally if had http headers could use last-updated
            'description': postlight_metadata['excerpt'],  # maybe None/Null
            'title': postlight_metadata['title'],
            'word_count': postlight_metadata['word_count'],
            'image': None, ## FIXME!!!
        }
    else:
        # do not attempt extract? check extractof cunt not set? and remove raw check
        doc_metadata = None  # fail rather than get none?
        doc_metadata = {
            'title': title or 'UnknownTitle',
            'description': 'UnknownDescription',
            'author': 'UnknownAuthor',
            'date': 'UnknownDate',  # TODO use now? Ideally if had http headers could use last-updated
        }
        if content is None:
            # TODO handle "file://" URLs? see FIXME above
            if url.startswith('http'):
                page_content_bytes = get_url(url)
            else:
                # assume read file local filename
                f = open(url, 'rb')
                page_content_bytes = f.read()
                f.close()

            content = page_content_bytes.decode('utf-8')  # FIXME revisit this - cache encoding
            content_format = FORMAT_HTML  # guess, this is probably a good guess?

    title = title or doc_metadata['title']

    print(output_format)  # TODO logging
    if not output_filename:
        filename_prefix = filename_prefix or ''
        output_filename = '%s%s.%s' % (filename_prefix, safe_filename(title), output_format)
    print(output_filename)  # TODO logging

    if output_format == FORMAT_EPUB:
        epub_output_function(output_filename, url=url, content=content, title=title, content_format=content_format)
    else:
        if content_format != output_format and output_format == FORMAT_MARKDOWN:
            # assume html - TODO add check?
            content = markdownify.markdownify(content.encode('utf-8'))

        if output_format == FORMAT_MARKDOWN:
            # TODO TOC?
            markdown_text = '# %s\n\n%s %s\n\n%s\n\n' % (doc_metadata['title'] or 'MISSING_TITLE', doc_metadata['author'] or 'MISSING_AUTHOR', doc_metadata['date'] or 'MISSING_DATE', doc_metadata['description'] or 'MISSING_DESCRIPTION')
            if doc_metadata.get('image'):
                markdown_text += '![alt text - maybe use title but need to escape brackets?](%s)\n\n' % (doc_metadata['image'],)
            content = markdown_text + content
            if not content.endswith('\n'):
                # ensure there is a newline at the end, this allows concatinating files (e.g. with cat, pandoc, etc.) and avoids headers getting combined with last paragraph
                content += '\n'  # consider multiple?

        out_bytes = content.encode('utf-8')
        #print(type(out_bytes))

        f = open(output_filename, 'wb')
        f.write(out_bytes)
        f.close()

    #import pdb; pdb.set_trace()  # DEBUG

    # FIXME need epub filename
    result_metadata = {
        'title': doc_metadata['title'],
        'description': doc_metadata['description'],
        'author': doc_metadata['author'],
        'date': doc_metadata['date'],
        'filename': output_filename,
    }

    # FIXME this is from old approch before refactor to extractor functions
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

    extractor_function_name = os.environ.get('W2D_EXTRACTOR', 'readability')
    # TODO use introspection api rather than this hard coded one
    # TODO support raw (and remove raw parameter)
    if extractor_function_name == 'postlight':
        extractor_function = extractor_postlight
    elif extractor_function_name == 'postlight_exe':
        extractor_function = extractor_postlight_exe
    else:
        if readability:
            extractor_function = extractor_readability  # default to trafilatura and readability
        else:
            log.info('no extractors installed, defaulting to postlight parser, check MP_URL')
            extractor_function = extractor_postlight

    epub_output_function_name = os.environ.get('W2D_EPUB_TOOL')
    if epub_output_function_name == 'pypub':
        epub_output_function = pypub_epub_output_function
    elif epub_output_function_name == 'pandoc':
        epub_output_function = pandoc_epub_output_function
    else:
        if pypub:
            epub_output_function = pypub_epub_output_function
        else:
            log.info('pypub (epub) not installed, defaulting to pandoc, check pandoc is in the path')
            epub_output_function = pandoc_epub_output_function

    log.info('extractor_function=%r', extractor_function)
    log.info('epub_output_function=%r', epub_output_function)
    for output_format in output_format_list:
        result_metadata = process_page(url=url, output_format=output_format, extractor_function=extractor_function, raw=raw, filename_prefix=filename_prefix, epub_output_function=epub_output_function)
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

