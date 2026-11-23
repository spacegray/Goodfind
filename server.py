#!/usr/bin/env python3
"""Local preview and optional SerpApi search proxy. Bind to loopback only."""
import json, os, sqlite3, time, urllib.error, urllib.parse, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial

PORT = int(os.environ.get('PORT', '8011'))
KEY = os.environ.get('SERPAPI_API_KEY', '')
DB_PATH = os.environ.get('GOODFIND_DB_PATH', 'goodfind.sqlite3')
ALLOWED_INTERESTS = {'Fashion', 'Beauty', 'Home', 'Accessories'}
ALLOWED_PRIORITIES = {'recommended', 'price', 'delivery', 'rating'}

def valid_profile(data):
    return (isinstance(data, dict) and data.get('priority') in ALLOWED_PRIORITIES and isinstance(data.get('interests'), list) and len(data['interests']) <= 4 and all(isinstance(x, str) and x in ALLOWED_INTERESTS for x in data['interests']))

def connect_db():
    db=sqlite3.connect(DB_PATH)
    db.execute('CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY CHECK(id=1), preferences TEXT NOT NULL)')
    return db

def normalize(payload):
    results=[]
    for item in payload.get('shopping_results', []):
        if not isinstance(item,dict) or not item.get('title'):
            continue
        def url(value):
            return value if isinstance(value,str) and urllib.parse.urlparse(value).scheme in ('http','https') else ''
        results.append({'title':str(item['title'])[:300], 'store':str(item.get('source') or '')[:150], 'price':str(item.get('price') or '')[:100], 'delivery':str(item.get('delivery') or '')[:300], 'image':url(item.get('thumbnail')), 'link':url(item.get('product_link') or item.get('link'))})
    return results[:24]

class Handler(SimpleHTTPRequestHandler):
    def json_response(self,status,data):
        content=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(content))); self.end_headers(); self.wfile.write(content)
    def do_DELETE(self):
        if urllib.parse.urlparse(self.path).path != '/api/profile':return self.json_response(404,{'error':'Not found'})
        origin=self.headers.get('Origin',''); host=self.headers.get('Host','')
        if origin not in ('http://'+host, 'https://'+host):return self.json_response(403,{'error':'Invalid origin'})
        try:
            with connect_db() as db: db.execute('DELETE FROM profile WHERE id=1')
            return self.json_response(200,{'ok':True})
        except sqlite3.Error:return self.json_response(500,{'error':'Unable to clear profile'})
    def do_PUT(self):
        if urllib.parse.urlparse(self.path).path != '/api/profile':return self.json_response(404,{'error':'Not found'})
        origin=self.headers.get('Origin','')
        host=self.headers.get('Host','')
        if origin not in ('http://'+host, 'https://'+host):return self.json_response(403,{'error':'Invalid origin'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<1 or length>2048:raise ValueError('length')
            data=json.loads(self.rfile.read(length))
            if not valid_profile(data):raise ValueError('profile')
            with connect_db() as db: db.execute('INSERT OR REPLACE INTO profile(id,preferences) VALUES(1,?)',(json.dumps({'priority':data['priority'],'interests':data['interests']}),))
            return self.json_response(200,{'ok':True})
        except (ValueError,TypeError,UnicodeDecodeError,json.JSONDecodeError):return self.json_response(400,{'error':'Invalid profile'})
        except sqlite3.Error:return self.json_response(500,{'error':'Unable to save profile'})
    def do_GET(self):
        parts=urllib.parse.urlparse(self.path)
        if parts.path=='/api/profile':
            try:
                with connect_db() as db: row=db.execute('SELECT preferences FROM profile WHERE id=1').fetchone()
                return self.json_response(200,{'profile':json.loads(row[0]) if row else None})
            except (sqlite3.Error,ValueError):return self.json_response(500,{'error':'Unable to read profile'})
        if parts.path!='/api/search': return super().do_GET()
        q=urllib.parse.parse_qs(parts.query).get('q',[''])[0].strip()
        def send(status,data):
            content=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(content))); self.end_headers(); self.wfile.write(content)
        if not q or len(q)>150:return send(400,{'error':'Enter a search of 1–150 characters.'})
        if not KEY:return send(503,{'error':'Live web search needs a SerpApi key. See README for setup; sample search is available above.'})
        now=time.monotonic()
        if now-self.server.last_search<2:return send(429,{'error':'Please wait a moment before searching again.'})
        self.server.last_search=now
        params=urllib.parse.urlencode({'engine':'google_shopping','q':q,'gl':'us','hl':'en','api_key':KEY})
        try:
            with urllib.request.urlopen('https://serpapi.com/search.json?'+params, timeout=12) as response: data=json.load(response)
            if data.get('error'):return send(502,{'error':'The search provider could not complete this request.'})
            return send(200,{'results':normalize(data)})
        except (OSError,ValueError,urllib.error.URLError):return send(502,{'error':'Could not reach the search provider. Please try again.'})

if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',PORT),partial(Handler,directory='dist')); server.last_search=0
    print('Goodfind running at http://127.0.0.1:%d' % PORT,flush=True); server.serve_forever()
