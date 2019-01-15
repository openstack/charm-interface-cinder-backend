import unittest
import mock


with mock.patch('charmhelpers.core.hookenv.metadata') as _meta:
    _meta.return_Value = 'ss'
    import provides


_hook_args = {}

TO_PATCH = [
]


def mock_hook(*args, **kwargs):

    def inner(f):
        # remember what we were passed.  Note that we can't actually determine
        # the class we're attached to, as the decorator only gets the function.
        _hook_args[f.__name__] = dict(args=args, kwargs=kwargs)
        return f
    return inner


class _unit_mock:
    def __init__(self, unit_name, received=None):
        self.unit_name = unit_name
        self.received = received or {}


class _relation_mock:
    def __init__(self, application_name=None, units=None):
        self.to_publish_raw = {}
        self.application_name = application_name
        self.units = units


class TestCinderBackendProvides(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._patched_hook = mock.patch('charms.reactive.when', mock_hook)
        cls._patched_hook_started = cls._patched_hook.start()
        # force provides to rerun the mock_hook decorator:
        # try except is Python2/Python3 compatibility as Python3 has moved
        # reload to importlib.
        try:
            reload(provides)
        except NameError:
            import importlib
            importlib.reload(provides)

    @classmethod
    def tearDownClass(cls):
        cls._patched_hook.stop()
        cls._patched_hook_started = None
        cls._patched_hook = None
        # and fix any breakage we did to the module
        try:
            reload(provides)
        except NameError:
            import importlib
            importlib.reload(provides)

    def patch(self, method):
        _m = mock.patch.object(self.obj, method)
        _mock = _m.start()
        self.addCleanup(_m.stop)
        return _mock

    def setUp(self):
        self.cr = provides.CinderBackendProvides('some-relation', [])
        self._patches = {}
        self._patches_start = {}
        self.obj = provides
        for method in TO_PATCH:
            setattr(self, method, self.patch(method))

    def tearDown(self):
        self.cr = None
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None

    def patch_kr(self, attr, return_value=None):
        mocked = mock.patch.object(self.cr, attr)
        self._patches[attr] = mocked
        started = mocked.start()
        started.return_value = return_value
        self._patches_start[attr] = started
        setattr(self, attr, started)

    def test_cinder_backend_joined(self):
        mock_conv = mock.MagicMock()
        self.patch_kr('conversation', mock_conv)
        self.cr.cinder_backend_joined()
        expected_calls = [
            mock.call('{relation_name}.joined'),
            mock.call('{relation_name}.connected'),
            mock.call('{relation_name}.available')]
        mock_conv.set_state.assert_has_calls(expected_calls)

    def test_cinder_backend_departed(self):
        mock_conv = mock.MagicMock()
        self.patch_kr('conversation', mock_conv)
        self.cr.cinder_backend_departed()
        expected_calls = [
            mock.call('{relation_name}.joined'),
            mock.call('{relation_name}.available'),
            mock.call('{relation_name}.connected')]
        mock_conv.remove_state.assert_has_calls(expected_calls)
        mock_conv.set_state.assert_called_once_with(
            '{relation_name}.departing')

    def test_configure_principal(self):
        mock_conv = mock.MagicMock()
        self.patch_kr('conversation', mock_conv)
        self.cr.configure_principal(
            'cinder-supernas',
            [('cinder', 'ss')],
            True)
        expect = ('{"cinder": {"/etc/cinder/cinder.conf": {"sections": '
                  '{"cinder-supernas": [["cinder", "ss"]]}}}}')
        mock_conv.set_remote.assert_called_once_with(
            backend_name='cinder-supernas',
            stateless=True,
            subordinate_configuration=expect)
