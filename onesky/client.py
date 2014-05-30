import hashlib
import requests
import time

DEFAULT_API_URL = 'https://platform.api.onesky.io/1/'


# python wrapper for OneSky's REST API, see
# https://github.com/onesky/api-documentation-platform
class Client:
    def __init__(self, api_key, api_secret,
                 api_url=DEFAULT_API_URL,
                 request_callback=None):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.request_callback = request_callback

    def create_auth_variables(self):
        timestamp = str(int(time.time()))

        dev_hash = hashlib.md5()
        dev_hash.update(timestamp)
        dev_hash.update(self.api_secret)

        return {
            'api_key': self.api_key,
            'timestamp': timestamp,
            'dev_hash': dev_hash.hexdigest()
        }

    def do_http_request(self, relative_url, parameters=None, method='GET'):
        absolute_url = self.api_url + relative_url

        # the auth variables and any additional parameters are merged and
        # encoded in the URL (the 'params' parameter in the requests library).
        if parameters is None:
            url_parameters = {}
        else:
            # by rule, filter out None.  this makes things a bit easier for the
            # caller because he doesn't have to do the filtering for default
            # variables.
            url_parameters = dict([(k, v) for k, v in parameters.items()
                                   if v is not None])
        url_parameters.update(self.create_auth_variables())

        if self.request_callback:
            self.request_callback(method, absolute_url, url_parameters)

        # method is something like GET or POST or DELETE, for which we grab the
        # appropriate function from the requests library.
        request_function = getattr(requests, method.lower())
        response = request_function(absolute_url, params=url_parameters)

        # some requests (such as project_group_delete) don't return any
        # response data, just the status code.
        try:
            response_dict = response.json()
        except ValueError:
            response_dict = {}

        return (response.status_code, response_dict)

    ################################################################
    # project group API
    def project_group_list(self, page=None, per_page=None):
        relative_url = 'project-groups'
        params = {'page': page, 'per_page': per_page}
        return self.do_http_request(relative_url, params)

    def project_group_show(self, project_group_id):
        relative_url = 'project-groups/{}'.format(project_group_id)
        return self.do_http_request(relative_url)

    def project_group_create(self, name, locale=None):
        relative_url = 'project-groups'
        params = {'name': name, 'locale': locale}
        return self.do_http_request(relative_url, params, method='POST')

    def project_group_delete(self, project_group_id):
        relative_url = 'project-groups/{}'.format(project_group_id)
        return self.do_http_request(relative_url, method='DELETE')

    def project_group_languages(self, project_group_id):
        relative_url = 'project-groups/{}/languages'.format(project_group_id)
        return self.do_http_request(relative_url)
    ################################################################

    ################################################################
    # project API
    def project_list(self, project_group_id, page=None, per_page=None):
        relative_url = 'project-groups/{}/projects'.format(project_group_id)
        params = {'page': page, 'per_page': per_page}
        return self.do_http_request(relative_url, params)

    def project_show(self, project_id):
        relative_url = 'projects/{}'.format(project_id)
        return self.do_http_request(relative_url)

    def project_create(self, project_group_id, project_type,
                       name=None, description=None):
        relative_url = 'project-groups/{}/projects'.format(project_group_id)
        params = {'project_type': project_type,
                  'name': name, 'description': description}
        return self.do_http_request(relative_url, params, method='POST')

    def project_update(self, project_id, name=None, description=None):
        relative_url = 'projects/{}'.format(project_id)
        params = {'name': name, 'description': description}
        return self.do_http_request(relative_url, params, method='PUT')

    def project_delete(self, project_id):
        relative_url = 'projects/{}'.format(project_id)
        return self.do_http_request(relative_url, method='DELETE')

    def project_languages(self, project_id):
        relative_url = 'projects/{}/languages'.format(project_id)
        return self.do_http_request(relative_url)
    ################################################################

    # project type
    def project_type_list(self):
        return self.do_http_request('project-types')

    ################################################################
    # file API
    def file_list(self, project_id, page=None, per_page=None):
        relative_url = 'projects/{}/files'.format(project_id)
        params = {'page': page, 'per_page': per_page}
        return self.do_http_request(relative_url, params)

    # TODO: this doens't actually work; we need to send the file itself in the
    # POST payload.
    def file_upload(self, project_id, _file, file_format,
                    locale=None, is_keeping_all_strings=None):
        relative_url = 'projects/{}/files'.format(project_id)
        params = {'file': _file, 'file_format': file_format, 'locale': locale,
                  'is_keeping_all_strings': is_keeping_all_strings}
        return self.do_http_request(relative_url, params, method='POST')

    def file_delete(self, project_id, file_name):
        relative_url = 'projects/{}/files'.format(project_id)
        params = {'file_name': file_name}
        return self.do_http_request(relative_url, params, method='DELETE')
    ################################################################

    ################################################################
    # translation

    # TODO: this doesn't actually work; we need to get the file out of the
    # payload that's returned.
    def translation_export(self, project_id, locale,
                           source_file_name, export_file_name=None):
        relative_url = 'projects/{}/translations'.format(project_id)
        params = {'locale': locale, 'source_file_name': source_file_name,
                  'export_file_name': export_file_name}
        return self.do_http_request(relative_url, params, method='POST')

    def translation_status(self, project_id, file_name, locale):
        relative_url = 'projects/{}/translations'.format(project_id)
        params = {'file_name': file_name, 'locale': locale}
        return self.do_http_request(relative_url, params)
    ################################################################

    ################################################################
    # import task
    def import_task_list(self, project_id, page=None, per_page=None,
                         status=None):
        relative_url = 'projects/{}/import-tasks'.format(project_id)
        params = {'page': page, 'per_page': per_page, 'status': status}
        return self.do_http_request(relative_url, params)

    def import_task_show(self, project_id, import_id):
        relative_url = 'projects/{}/import-tasks/{}'.format(
            project_id, import_id
        )
        return self.do_http_request(relative_url)
    ################################################################

    # screenshot
    def screenshot_upload(self, project_id, screenshots):
        pass

    # quotation
    def quotation_show(self, project_id,
                       files, to_locale,
                       is_including_not_translated=None,
                       is_including_not_approved=None,
                       is_including_outdated=None,
                       specialization=None):
        relative_url = 'projects/{}/quotations'.format(project_id)
        params = {'files': str(files),
                  'to_locale': to_locale,
                  'is_including_not_translated': is_including_not_translated,
                  'is_including_not_approved': is_including_not_approved,
                  'is_including_outdated': is_including_outdated,
                  'specialization': specialization}
        return self.do_http_request(relative_url, params)

    ################################################################
    # order
    def order_list(self, project_id, page=None, per_page=None):
        relative_url = 'projects/{}/orders'.format(project_id)
        params = {'page': page, 'per_page': per_page}
        return self.do_http_request(relative_url, params)

    def order_show(self, project_id, order_id):
        relative_url = 'projects/{}/orders/{}'.format(
            project_id, order_id
        )
        return self.do_http_request(relative_url)

    def order_create(self, project_id,
                     files, to_locale,
                     order_type=None,
                     is_including_not_translated=None,
                     is_including_not_approved=None,
                     is_including_outdated=None,
                     translator_type=None,
                     tone=None,
                     specialization=None,
                     note=None):
        relative_url = 'projects/{}/orders'.format(project_id)
        params = {'files': str(files),
                  'to_locale': to_locale,
                  'order_type': order_type,
                  'is_including_not_translated': is_including_not_translated,
                  'is_including_not_approved': is_including_not_approved,
                  'is_including_outdated': is_including_outdated,
                  'translator_type': translator_type,
                  'tone': tone,
                  'specialization': specialization,
                  'note': note}
        return self.do_http_request(relative_url, params, 'POST')
    ################################################################

    # locale
    def locale_list(self):
        return self.do_http_request('locales')
