# w2d

Dumb web to disk tool; html, markdown / md / text, epub

Python 3 and 2.7


## Getting Started

### From a source code checkout

TODO document debian packages that can be installed

    python -m pip install -r requirements.txt

## Examples

    python w2d.py
    python w2d.py https://en.wikipedia.org/wiki/EPUB
    python w2d.py local_file.html


## Notes

  * right now there is no commandline argument processing
  * no control over output format
  * no control over whether readabilty extract is performed or not (it always performs an extract)
  * no control over disk cache contents, all pages are cached.
      * cache location is controlled via operating system environment variable `W2D_CACHE_DIR`, if not set defaults to `scrape_cache` in current directory
      * cache name is md5sum in hex of the URL, same root URL with different parameters (or href shortcuts `#id_marker`) will cause new cache entry to be pulled down

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
