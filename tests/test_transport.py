import socket
import types
import unittest
from unittest.mock import Mock
from nbloader import load_notebook, notebook


def transport():
    module = load_notebook()
    module.socket = socket
    module.requests = types.SimpleNamespace(Session=Mock())
    cell = next(c for c in notebook()['cells'] if c['id'] == '454ee782')
    exec(compile(''.join(cell['source']), cell['id'], 'exec'), module.__dict__)
    return module


class Response:
    def __init__(self, status=200):
        self.status_code = status
        self.headers = {'Content-Type': 'application/dns-message'}
        self.content = bytes.fromhex('000081800001000100000000076578616d706c6503636f6d0000010001'
                                     'c00c0001000100000e1000045db8d822')
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError('HTTP failure')
    def json(self):
        return {'Status': 3, 'AD': False}


class TransportTests(unittest.TestCase):
    def test_unknown_provider_before_network(self):
        module = transport()
        with self.assertRaises(ValueError):
            module.resolve_doh('example.com', 'invalid')
        module.requests.Session.assert_not_called()

    def test_request_modes_timeout_and_ownership(self):
        module = transport()
        session = Mock()
        session.get.return_value = Response()
        reply = module.resolve_doh('example.com', 'google', 'wire', 7, session)
        self.assertEqual(reply['answers'][0]['data'], '93.184.216.34')
        kwargs = session.get.call_args.kwargs
        self.assertEqual(kwargs['timeout'], 7)
        self.assertFalse(kwargs['allow_redirects'])
        self.assertEqual(kwargs['headers'], {'accept': 'application/dns-message'})
        self.assertEqual(kwargs['params']['dns'], 'AAABAAABAAAAAAAAB2V4YW1wbGUDY29tAAABAAE')
        session.close.assert_not_called()
        module.requests.Session.return_value = session
        self.assertEqual(module.resolve_doh('example.com', 'cloudflare', 'json')['rcode'], 3)
        self.assertFalse(session.trust_env)
        session.close.assert_called_once()
        self.assertEqual(session.get.call_args.kwargs['headers'], {'accept': 'application/dns-json'})

    def test_401_stops_and_session_closes(self):
        module = transport()
        session = Mock()
        session.get.return_value = Response(401)
        module.requests.Session.return_value = session
        with self.assertRaises(SystemExit):
            module.resolve_doh('example.com')
        session.get.assert_called_once()
        session.close.assert_called_once()

    def test_negative_os_answer_and_temporary_failure(self):
        module = transport()
        module.socket = types.SimpleNamespace(
            gethostbyname=Mock(side_effect=socket.gaierror(socket.EAI_NONAME, 'not found')),
            gaierror=socket.gaierror, EAI_NONAME=socket.EAI_NONAME,
        )
        self.assertEqual(module.resolve_standard_dns('example.com')['answers'], [])
        module.socket.gethostbyname.side_effect = socket.gaierror(socket.EAI_AGAIN, 'try again')
        with self.assertRaises(socket.gaierror):
            module.resolve_standard_dns('example.com')

    def test_new_and_reused_connections_are_separate(self):
        module = transport()
        sessions = []
        def make_session():
            session = Mock()
            session.get.return_value = Response()
            sessions.append(session)
            return session
        module.requests.Session.side_effect = make_session
        module.resolve_standard_dns = lambda domain: {'rcode': 0}
        # JSONならランダムな名前にも使える固定の否定応答。
        records = module.run_measurements(['example.com'], query_count=2, mode='json', warmup=1)
        self.assertEqual(len(records), 2 * 5 * 3)
        self.assertEqual(len(sessions), 2 + 2 * 2 * 3)
        self.assertEqual([session.get.call_count for session in sessions[:2]], [6, 6])
        self.assertTrue(all(session.get.call_count == 1 for session in sessions[2:]))
        for session in sessions:
            session.close.assert_called_once()
