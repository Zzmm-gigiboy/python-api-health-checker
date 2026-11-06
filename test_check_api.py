import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from threading import Thread

import pytest

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


@pytest.mark.parametrize('payload', [[], ['ok'], 'ok', 42, 3.14, True, False, None])
def test_non_object_json_is_unhealthy(payload, monkeypatch, tmp_path, capsys):
    def open_health(url, timeout):
        response = BytesIO(json.dumps(payload).encode('utf-8'))
        response.status = 200
        return response

    monkeypatch.setattr('check_api.urlopen', open_health)
    address = 'http://example.test'
    report = probe(address)
    assert report['healthy'] is False
    assert report['http_status'] == 200

    path = tmp_path / 'report.json'
    assert main(['--url', address, '--out', str(path)]) == 1
    written_report = json.loads(path.read_text())
    assert written_report['healthy'] is False
    assert written_report['http_status'] == 200
    assert json.loads(capsys.readouterr().out) == written_report
