from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from check_api import probe, main


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = 200 if self.path == '/health' else 404
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}' if status == 200 else b'{}')

    def log_message(self, *_):
        pass


def test_healthy_and_failure_paths(tmp_path):
    server = HTTPServer(('127.0.0.1', 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        address = f'http://127.0.0.1:{server.server_port}'
        assert probe(address)['healthy']
        path = tmp_path / 'report.json'
        assert main(['--url', address, '--out', str(path)]) == 0
        assert 'healthy' in path.read_text()
        assert main(['--url', address + '/missing']) == 1
    finally:
        server.shutdown()
        worker.join(timeout=5)
