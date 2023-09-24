# Test Data

Suitable for hosting with a static web server.

- [Test Data](#test-data)
  * [Test files for hosting](#test-files-for-hosting)
    + [Python3](#python3)
    + [Python2](#python2)
  * [Test URLs](#test-urls)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


## Test files for hosting

### Python3

    echo http://localhost:8000/
    echo http://localhost:8000/one.html
    python3 -m http.server 8000

### Python2


    echo http://localhost:8000/
    echo http://localhost:8000/one.html
    python2 -m SimpleHTTPServer 8000

## Test URLs

### Builtin

Assuming http://localhost:8000/

  * http://localhost:8000/one.html
  * http://localhost:8000/two.html
  * http://localhost:8000/sub_dir/three.html

TODO
