import logging
from sys import argv
from os import listdir, path as p


class Signal:
    """
    Some global variable,
    set them into a class.
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


def formatdate(now=None, usegmt=False)-> str:
    """
    format time as UTC
    """
    import time
    import datetime
    if not now:
        now = time.time()
    if usegmt:
        dt = datetime.datetime.fromtimestamp(
            now, datetime.timezone.utc
        )  # type: datetime.datetime
    else:
        dt = datetime.datetime.utcfromtimestamp(
            now
        )  # type: datetime.datetime
    zone = "-0000"

    months = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec"
    }
    weeks = {
        0: "Mon",
        1: "Tue",
        2: "Wed",
        3: "Thu",
        4: "Fri",
        5: "Sat",
        6: "Sun"
    }

    return "{week}, {d} {m} {y} {h}:{M}:{s:02} {zone}".format(
        week=weeks.get(dt.weekday()),
        d=dt.day,
        m=months.get(dt.month),
        y=dt.year,
        h=dt.hour,
        M=dt.minute,
        s=dt.second,
        zone=zone
    )


# there are the all file types that the can display
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


def list_files()-> str:
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


def parse_url(url: str, file_lengths: int)->str:
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
    # directory name
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
