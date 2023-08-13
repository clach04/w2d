# w2d

Dumb web to disk tool; html, markdown / md / text, epub

Python 3 and 2.7

- [w2d](#w2d)
  * [Getting Started](#getting-started)
    + [From a source code checkout](#from-a-source-code-checkout)
  * [Examples from checkout](#examples-from-checkout)
  * [Notes](#notes)
  * [Acknowledgements](#acknowledgements)
  * [Known Working Environments](#known-working-environments)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## Getting Started

### Without a source code checkout

    python3 -m venv py3venv  # optional...
    # TODO better way than directly from command line list
    python -m pip install --upgrade markdownify readability-lxml git+https://github.com/clach04/pypub.git git+https://github.com/clach04/w2d.git  # Python 2 or 3 - without trafilatura
    python -m pip install --upgrade markdownify readability-lxml trafilatura git+https://github.com/clach04/pypub.git git+https://github.com/clach04/w2d.git  # Python 3 only

## Examples after install

    w2d
    w2d https://en.wikipedia.org/wiki/EPUB
    w2d local_file.html


### From a source code checkout

TODO document debian packages that can be installed

    git clone https://github.com/clach04/w2d.git
    cd w2d
    python3 -m venv py3venv
    . py3venv/bin/activate

    python -m pip install -r requirements.txt
    python setup.py develop  # optional to have w2d binary

## Examples from checkout

    python -m w2d
    python -m w2d https://en.wikipedia.org/wiki/EPUB
    python -m w2d local_file.html

    # if setup.py ran in install or develop mode
    w2d
    w2d https://en.wikipedia.org/wiki/EPUB
    w2d local_file.html


## Notes

  * right now there is no commandline argument processing other than list of URLs
  * no control over output format - use operating system environment variable `W2D_OUTPUT_FORMAT` (may be set to `html`, `md`, `epub`, and `all`)
  * no control over whether readabilty extract is performed or not (it always performs an extract) - see environment variable `W2D_EXTRACTOR` (may be set to `readability` or `postlight`, if postlight use also see/set `MP_URL`)
  * no control over disk cache contents, all pages are cached.
      * cache location is controlled via operating system environment variable `W2D_CACHE_DIR`, if not set defaults to `scrape_cache` in current directory
      * cache name is md5sum in hex of the URL, same root URL with different parameters (or href shortcuts `#id_marker`) will cause new cache entry to be pulled down

## Acknowledgements

This project builds on a number of other tools to perform the heavy lifting:

  * https://github.com/matthewwithanm/python-markdownify - for outputing Markdown with python-readability
  * https://github.com/clach04/pypub is based on https://github.com/wcember/ original work for outputing epub2 files
  * https://github.com/buriy/python-readability - used to extract main content from html pages, in turn based on https://github.com/timbertson/ work, which is in turn pased on arc90's readability bookmarklet https://web.archive.org/web/20130519040221/http://www.readability.com/
  * https://github.com/adbar/trafilatura - has great meta data extraction support
  * Postlight (nee mercury) parser
      * https://github.com/HenryQW/mercury-parser-api
      * https://github.com/postlight/parser-api

## Known Working Environments

  * Windows 10 - Python 3.10

        (py310venv) C:\code\py\w2d>pip list
        Package          Version
        ---------------- ---------
        beautifulsoup4   4.9.3
        certifi          2023.7.22
        chardet          3.0.4
        courlan          0.5.0
        cssselect        1.2.0
        dateparser       1.1.8
        htmldate         0.8.1
        idna             2.8
        Jinja2           2.11.3
        jusText          3.0.0
        langcodes        3.3.0
        lxml             4.9.3
        markdownify      0.11.6
        MarkupSafe       1.1.1
        pip              22.0.4
        pypub            1.5
        python-dateutil  2.8.2
        pytz             2023.3
        readability      0.3.1
        readability-lxml 0.8.1
        regex            2023.6.3
        requests         2.22.0
        setuptools       58.1.0
        six              1.16.0
        soupsieve        2.4.1
        tld              0.13
        trafilatura      0.8.2
        tzdata           2023.3
        tzlocal          5.0.1
        urllib3          1.25.11

  * Windows 10 - Python 2.7.18


        (py210venv) C:\code\py\w2d>pip list
        DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop sup
        port for Python 2.7 in January 2021. More details about Python 2 support in pip can be found at https://pip.pypa.io/en/latest/development/release-process/#python-
        2-support pip 21.0 will remove support for this functionality.
        Package                       Version
        ----------------------------- ---------
        backports.functools-lru-cache 1.6.6
        beautifulsoup4                4.9.3
        certifi                       2021.10.8
        chardet                       3.0.4
        idna                          2.8
        Jinja2                        2.11.3
        lxml                          4.9.3
        markdownify                   0.11.6
        MarkupSafe                    1.1.1
        pip                           20.3.4
        pypub                         1.6
        readability                   0.3.1
        requests                      2.22.0
        setuptools                    44.1.1
        six                           1.16.0
        soupsieve                     1.9.6
        urllib3                       1.25.11
        wheel                         0.37.1

  * Linux Ubuntu 18.04.6 LTS (Bionic Beaver) - Python 3.6.9

    Without trafilatura:

        (py3venv) clach04@fugly:/tmp$ pip list
        DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.
        beautifulsoup4 (4.12.2)
        certifi (2023.7.22)
        chardet (5.0.0)
        charset-normalizer (2.0.12)
        cssselect (1.1.0)
        idna (3.4)
        Jinja2 (3.0.3)
        lxml (4.9.3)
        markdownify (0.11.6)
        MarkupSafe (2.0.1)
        pip (9.0.1)
        pkg-resources (0.0.0)
        pypub (1.6)
        readability-lxml (0.8.1)
        requests (2.27.1)
        setuptools (39.0.1)
        six (1.16.0)
        soupsieve (2.3.2.post1)
        urllib3 (1.26.16)
        w2d (0.0.1)

    With trafilatura:

        (py3venv) :~/w2d$ pip list
        DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.
        backports-datetime-fromisoformat (2.0.0)
        backports.zoneinfo (0.2.1)
        beautifulsoup4 (4.12.2)
        certifi (2023.7.22)
        chardet (5.0.0)
        charset-normalizer (3.0.1)
        courlan (0.9.3)
        cssselect (1.1.0)
        dateparser (1.1.3)
        htmldate (1.4.3)
        idna (3.4)
        importlib-resources (5.4.0)
        Jinja2 (3.0.3)
        jusText (3.0.0)
        langcodes (3.3.0)
        lxml (4.9.3)
        markdownify (0.11.6)
        MarkupSafe (2.0.1)
        pip (9.0.1)
        pkg-resources (0.0.0)
        pypub (1.6)
        python-dateutil (2.8.2)
        pytz (2023.3)
        pytz-deprecation-shim (0.1.0.post0)
        readability-lxml (0.8.1)
        regex (2022.3.2)
        requests (2.27.1)
        setuptools (39.0.1)
        six (1.16.0)
        soupsieve (2.3.2.post1)
        tld (0.12.6)
        trafilatura (1.6.1)
        tzdata (2023.3)
        tzlocal (4.2)
        urllib3 (1.26.16)
        zipp (3.6.0)
