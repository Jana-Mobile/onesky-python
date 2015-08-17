
import collections
import hashlib
import mock
import os
import requests
import unittest

import onesky.client


TEST_API_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
TEST_API_SECRET = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'


# mock object to return a fake response from requests
class MockResponse():
    headers = requests.structures.CaseInsensitiveDict()
    status_code = 200

    def json(self):
        return {}


def mock_requests_function(*args, **kwargs):
    return MockResponse()


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        # we mock out all of the http requests and just make sure the correct
        # urls and parameters and such are being passed.
        self.patcher = mock.patch.multiple(
            requests,
            get=mock_requests_function,
            post=mock_requests_function,
            put=mock_requests_function,
            delete=mock_requests_function)
        self.patcher.start()

        self.client = onesky.client.Client(TEST_API_KEY, TEST_API_SECRET)

    def tearDown(self):
        del self.client
        self.patcher.stop()

    def execute_with_parameters(self, function_name,
                                expected_method, expected_url,
                                _parameters, ignored_parameters=[]):
        callback_results = {}

        def callback(method, absolute_url, url_parameters):
            callback_results.update({
                'method': method,
                'absolute_url': absolute_url,
                'url_parameters': url_parameters
            })

        try:
            self.client.request_callback = callback

            # we copy the parameters because we modify them in some cases to
            # accurately represent what's expected to be returned, and don't
            # want to modify the caller's parameters in-place.
            parameters = collections.OrderedDict(_parameters.items())

            api_function = getattr(self.client, function_name)
            (status_code, result) = api_function(**parameters)

            # check that the method (GET, POST, etc) is what we expected
            self.assertEqual(callback_results.get('method'), expected_method)

            # check the URL.  Some URL's have a parameter baked into them,
            # which is always the first param
            expected_absolute_url = self.client.api_url + expected_url

            if '{}' in expected_url:
                # for each occurance of {} in the url, substitute the first
                # parameter.
                substitutions = []
                for i in range(expected_url.count('{}')):
                    key, value = parameters.popitem(last=False)
                    substitutions.append(value)
                expected_absolute_url = expected_absolute_url.format(
                    *substitutions
                )

            self.assertEqual(callback_results.get('absolute_url'),
                             expected_absolute_url)

            # anything in 'ignored_parameters' is not expected to show up in
            # the URL variables.  this is the case for file uploads, where the
            # file is uploaded as part of the POST payload.
            for param in ignored_parameters:
                if param in parameters:
                    del parameters[param]

            # check the parameters.  we should have the correct API key, and
            # the hash should match the API secret based on the timestamp.
            result_params = callback_results.get('url_parameters')
            self.assertEqual(result_params.get('api_key'), TEST_API_KEY)

            expected_hash = hashlib.md5()
            expected_hash.update(result_params['timestamp'])
            expected_hash.update(TEST_API_SECRET)
            self.assertEqual(result_params['dev_hash'],
                             expected_hash.hexdigest())

            # finally, each of the other parameters should be passed through.
            for key, value in parameters.items():
                self.assertEqual(result_params.get(key), value)

            # and there should be nothing more in the url parameters than that
            # (the +3 is for api key, timestamp, and hash)
            self.assertEqual(len(result_params), len(parameters) + 3)

        finally:
            self.client.request_callback = None

    def execute(self, function_name,
                expected_method, expected_url,
                required_parameters=[], optional_parameters=[],
                fixed_parameters={},
                ignored_parameters=[]):
        # test with just the required parameters
        parameters = collections.OrderedDict()
        for i, p in enumerate(required_parameters):
            if p in fixed_parameters:
                parameters[p] = fixed_parameters[p]
            else:
                parameters[p] = 'param{}'.format(i)

        self.execute_with_parameters(function_name,
                                     expected_method, expected_url,
                                     parameters,
                                     ignored_parameters=ignored_parameters)

        # now test with the optional parameters.  we aren't bothering to test
        # with some of the optional parameters, but we could.
        for i, p in enumerate(optional_parameters):
            if p in fixed_parameters:
                parameters[p] = fixed_parameters[p]
            else:
                parameters[p] = 'optional_param{}'.format(i)

        self.execute_with_parameters(function_name,
                                     expected_method, expected_url,
                                     parameters,
                                     ignored_parameters=ignored_parameters)

    def test_project_group_list(self):
        self.execute('project_group_list',
                     'GET', 'project-groups',
                     [],
                     ['page', 'per_page'])

    def test_project_group_show(self):
        self.execute('project_group_show',
                     'GET', 'project-groups/{}',
                     ['project_group_id'])

    def test_project_group_create(self):
        self.execute('project_group_create',
                     'POST', 'project-groups',
                     ['name'],
                     ['locale'])

    def test_project_group_delete(self):
        self.execute('project_group_delete',
                     'DELETE', 'project-groups/{}',
                     ['project_group_id'])

    def test_project_group_languages(self):
        self.execute('project_group_languages',
                     'GET', 'project-groups/{}/languages',
                     ['project_group_id'])

    def test_project_list(self):
        self.execute('project_list',
                     'GET', 'project-groups/{}/projects',
                     ['project_group_id'],
                     ['page', 'per_page'])

    def test_project_show(self):
        self.execute('project_show',
                     'GET', 'projects/{}',
                     ['project_id'])

    def test_project_create(self):
        self.execute('project_create',
                     'POST', 'project-groups/{}/projects',
                     ['project_group_id', 'project_type'],
                     ['name', 'description'])

    def test_project_update(self):
        self.execute('project_update',
                     'PUT', 'projects/{}',
                     ['project_id'],
                     ['name', 'description'])

    def test_project_delete(self):
        self.execute('project_delete',
                     'DELETE', 'projects/{}',
                     ['project_id'])

    def test_project_languages(self):
        self.execute('project_languages',
                     'GET', 'projects/{}/languages',
                     ['project_id'])

    def test_project_type_list(self):
        self.execute('project_type_list', 'GET', 'project-types')

    def test_file_list(self):
        self.execute('file_list',
                     'GET', 'projects/{}/files',
                     ['project_id'], ['page', 'per_page'])

    def test_file_upload(self):
        # must specify an actual file name that will be loaded
        absfile = os.path.join(os.path.dirname(__file__), 'test_strings.pot')
        self.execute('file_upload',
                     'POST', 'projects/{}/files',
                     ['project_id', 'file_name', 'file_format'],
                     ['locale', 'is_keeping_all_strings'],
                     {'file_name': absfile},
                     ignored_parameters=['file_name'])

    def test_file_delete(self):
        self.execute('file_delete',
                     'DELETE', 'projects/{}/files',
                     ['project_id', 'file_name'])

    def test_translation_export(self):
        self.execute('translation_export',
                     'GET', 'projects/{}/translations',
                     ['project_id', 'locale', 'source_file_name'],
                     ['export_file_name'])

    def test_translation_export_multilingual(self):
        self.execute('translation_export_multilingual',
                     'GET', 'projects/{}/translations/multilingual',
                     ['project_id', 'source_file_name'],
                     ['export_file_name', 'file_format'])

    def test_translation_status(self):
        self.execute('translation_status',
                     'GET', 'projects/{}/translations/status',
                     ['project_id', 'file_name', 'locale'])

    def test_import_task_list(self):
        self.execute('import_task_list',
                     'GET', 'projects/{}/import-tasks',
                     ['project_id'], ['page', 'per_page', 'status'])

    def test_import_task_show(self):
        self.execute('import_task_show',
                     'GET', 'projects/{}/import-tasks/{}',
                     ['project_id', 'import_id'], [])

    def test_screenshot(self):
        # wrapper for the screenshot stuff is not yet implemented
        pass

    def test_quotation_show(self):
        self.execute('quotation_show',
                     'GET', 'projects/{}/quotations',
                     ['project_id', 'files', 'to_locale'],
                     ['is_including_not_translated',
                      'is_including_not_approved',
                      'is_including_outdated',
                      'specialization'])

    def test_order_list(self):
        self.execute('order_list',
                     'GET', 'projects/{}/orders',
                     ['project_id'], ['page', 'per_page'])

    def test_order_show(self):
        self.execute('order_show',
                     'GET', 'projects/{}/orders/{}',
                     ['project_id', 'order_id'])

    def test_order_create(self):
        self.execute('order_create',
                     'POST', 'projects/{}/orders',
                     ['project_id', 'files', 'to_locale'],
                     ['is_including_not_translated',
                      'is_including_not_approved',
                      'is_including_outdated',
                      'translator_type',
                      'tone', 'specialization', 'note'])

    def test_locale_list(self):
        self.execute('locale_list', 'GET', 'locales')
