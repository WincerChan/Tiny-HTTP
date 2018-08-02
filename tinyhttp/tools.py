import logging
from sys import argv
from os import listdir, path as p
from email.utils import formatdate


class Signal:
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
    params = {}
    if Signal.isdir:
        content_type = 'text/html;'
    else:
        path = url.decode('utf-8').split(' ')[1]
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
