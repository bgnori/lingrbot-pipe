#!/usr/bin/env python
#


from werkzeug import Request, ClosingIterator
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug import Response
from werkzeug.routing import Map, Rule

import json
import sys


DEBUG = True
MAGIC = "!pipe"

url_map = Map([
    Rule("/pipe", endpoint="pipe"),
    Rule("/", endpoint="index"),
])


def index(request):
    return Response("Hello, world!", mimetype="text/plain")

import urllib2 

def forge(data):
    t = """
    {
        "status":"ok",
        "counter":13934721,
        "events":[
            {
                "message":{
                    "id":"14333031",
                "room":"bgnori",
                "public_session_id":"IrrMxt",
                "icon_url":"http://www.gravatar.com/avatar/a00efd2efcb4f4efb65f01efd366f4b2.jpg",
                "type":"user",
                "speaker_id":"bgnori",
                "nickname":"bgnori",
                "text":"#!py27 %s",
                "timestamp":"2013-03-17T07:38:51Z",
                "local_id":"pending-IrrMxt-4"},
                "event_id":13934721
            }
        ]}
    """
    return t%(data,)


def foo(data):
    print >> sys.stderr, data
    j = forge(data)
    req = urllib2.Request("http://lingrbot.tonic-water.com:10080/py27")
    req.add_header('Content-Type', 'application/json')
    h = urllib2.urlopen(req, j)

    r = h.read()
    print >> sys.stderr, r
    return r


def pipe(request):
    try:
        data = json.loads(request.data)
    except:
        return Response('bad json', mimetype="text/plain")

    for evt in data['events']:
        msg = evt.get("message", None)
        if msg and msg["text"].startswith(MAGIC):
            source = msg["text"][len(MAGIC)+1:]
            try:
                r = foo(source)
            except Exception, e:
                return Response(str(e), mimetype="text/plain")
            return Response(str(r), mimetype="text/plain")
        else:
            print >> sys.stderr, "nothing to send"
            break
    return Response('', mimetype="text/plain")


views = {
        'index': index,
        'pipe': pipe,
        }


class Application(object):
    def __call__(self, environ, start_response):
        try:
            self._setup()
            request = Request(environ)
            if(DEBUG):
                print >> sys.stderr, request.base_url 
                print >> sys.stderr, request.data
            adapter = url_map.bind_to_environ(environ)
            endpoint, values = adapter.match()
            handler = views.get(endpoint)
            response = handler(request, **values)
        except HTTPException, e:
            response = e
        except:
            response = InternalServerError()

        return ClosingIterator(response(environ, start_response), self._cleanup)

    def _setup(self):
        pass
    def _cleanup(self):
        pass



from wsgiref.simple_server import make_server

bot = Application()

from werkzeug import DebuggedApplication
#bot = DebuggedApplication(bot)

httpd = make_server('192.168.2.64', 10081, bot)
httpd.serve_forever()

