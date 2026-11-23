import io, json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import server

class HandlerTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.previous=server.DB_PATH; server.DB_PATH=os.path.join(self.temp.name,'profile.sqlite3')
    def tearDown(self):
        server.DB_PATH=self.previous; self.temp.cleanup()
    def handler(self,method,path,data=None,origin='http://127.0.0.1:8011'):
        h=object.__new__(server.Handler);h.path=path;body=json.dumps(data).encode() if data is not None else b''
        h.headers={'Host':'127.0.0.1:8011','Origin':origin,'Content-Length':str(len(body))};h.rfile=io.BytesIO(body);h.wfile=io.BytesIO();h.send_response=lambda code:setattr(h,'status',code);h.send_header=lambda *x:None;h.end_headers=lambda:None
        getattr(h,method)();return h.status,json.loads(h.wfile.getvalue())
    def test_profile_roundtrip_and_delete(self):
        status,_=self.handler('do_PUT','/api/profile',{'priority':'price','interests':['Fashion']});self.assertEqual(status,200)
        self.assertEqual(self.handler('do_GET','/api/profile')[1]['profile']['priority'],'price')
        self.assertEqual(self.handler('do_DELETE','/api/profile')[0],200)
        self.assertIsNone(self.handler('do_GET','/api/profile')[1]['profile'])
    def test_profile_rejects_invalid_and_cross_origin(self):
        self.assertEqual(self.handler('do_PUT','/api/profile',{'priority':'bad','interests':[]})[0],400)
        self.assertEqual(self.handler('do_PUT','/api/profile',{'priority':'price','interests':[]},'http://bad.example')[0],403)
    def test_search_without_key_and_empty_query(self):
        key=server.KEY;server.KEY=''
        try:
            self.assertEqual(self.handler('do_GET','/api/search?q=')[0],400)
            self.assertEqual(self.handler('do_GET','/api/search?q=jacket')[0],503)
        finally:server.KEY=key
if __name__=='__main__':unittest.main()
