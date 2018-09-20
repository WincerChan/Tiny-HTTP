import logging
from sys import argv
from os import listdir, path as p
from email.utils import formatdate


class Signal:
    """
    一些全局变量的标识，采用 class 封装
    """
    go = True
    isdir = False
    path = ''
    debug = False
    mode = ''


if '--debug' in argv:
    Signal.debug = True
    logging.basicConfig(level=logging.DEBUG,
                        format=('%(asctime)s %(levelname)s '
                                '[%(threadName)s] %(message)s'))
    argv.remove('--debug')
else:
    logging.basicConfig(level=logging.INFO,
                        format=('%(asctime)s %(message)s'))


# 能识别的所有类型，会帮助浏览器识别这些文件
TYPE = {
    'css': 'text/css;',
    'png': 'image/png;',
    'jpg': 'image/jpg;',
    'gif': 'image/gif;',
    'txt': 'text/plain;',
    'html': 'text/html;',
    'pdf': 'application/pdf;',
    'js': 'application/javascript;',
}


def list_files():
    """ list_files() -> content

    When user get is a dir, if this dir has a index.html
    then return index.html file, else return all file
    in this dir.
    """
    html = '<h1>%s dictory.</h1><hr/><ul>' % Signal.path

    for file in listdir('.' + Signal.path):
        if p.isdir('.'+Signal.path + file):
            file += '/'
        elif file == 'index.html':
            return open('index.html', 'r').read()
        html += '<li style="font-size: 1.2em"><a href=%s>%s</a></li>' % (
            Signal.path + file, file)
    return html + '</ul>'


def parse_url(url, file_lengths)->str:
    """ parse_url(url, file_lengths) -> url_param

    Parse the url requested by the user and return the 
    corresponding header information.
    """
    params = {}
    if Signal.isdir:
        content_type = 'text/html;'
    else:
        path = to_str(url).split(' ')[1]
        suffix = path.split('.')[-1]
        content_type = TYPE.get(suffix, 'application/octet-stream')
    # 目录名
    if p.isdir('.'+Signal.path) and not Signal.path.endswith('/'):
        Signal.path += '/'
        params['Location'] = Signal.path
    params['Content-Length'] = file_lengths
    params['Content-Type'] = content_type + 'charset=utf-8'
    params['Date'] = formatdate(usegmt=True)
    params['Server'] = 'TinyHttp'
    return params


def to_str(bytes_or_str) -> str:
    return (bytes_or_str.decode('utf-8') if isinstance(bytes_or_str, bytes)
            else bytes_or_str)


def to_bytes(bytes_or_str) -> bytes:
    return (bytes_or_str.encode('utf-8') if isinstance(bytes_or_str, str)
            else bytes_or_str)
