#!/usr/bin/env python

import cmd
import pprint
import shlex
import termcolor
import urllib
import sys

import client


# helper to simplify the boilerplate wrapping all the API calls with command
# processors.
def make_cmd(name,
             required_parameters=[],
             optional_parameters=[],
             confirm=False):
    required_parameter_string = ''.join(
        [' <{}>'.format(param) for param in required_parameters])
    optional_parameter_string = ''.join(
        [' [{}]'.format(param) for param in optional_parameters])

    docstring = 'Usage: {}{}{}'.format(
        name, required_parameter_string, optional_parameter_string
    )

    def wrapped(self, line):
        try:
            parameters = shlex.split(line)
        except ValueError as e:
            self.stdout.write('Parse error: {}\n'.format(e))
            return

        optional_parameter_count = len(parameters) - len(required_parameters)
        if (optional_parameter_count < 0 or
                optional_parameter_count > len(optional_parameters)):
            self.stdout.write(docstring + '\n')
            return

        if confirm:
            while True:
                self.stdout.write('Are you sure? (y/N): ')
                self.stdout.flush()
                choice = raw_input().lower()
                if choice == '' or choice == 'n' or choice == 'no':
                    self.stdout.write('Canceled.\n')
                    return
                elif choice == 'y' or choice == 'yes':
                    break

        client_function = getattr(self.client, name)

        try:
            (status_code, response) = client_function(*parameters)
            self.print_response(status_code, response)
        except IOError as e:
            self.stdout.write('IOError: {}\n'.format(e))

    wrapped.__doc__ = docstring
    return wrapped


class Interpreter(cmd.Cmd):
    intro = (
        '\nWelcome to the OneSky command-line interface! '
        'Type {} for a list of commands.\n'.format(
            termcolor.colored('help', 'yellow')))
    prompt = termcolor.colored('onesky> ', 'blue')

    def __init__(self, api_key, api_secret):
        cmd.Cmd.__init__(self)
        self.printer = pprint.PrettyPrinter(stream=self.stdout)
        self.client = client.Client(
            api_key=api_key,
            api_secret=api_secret,
            request_callback=self.on_http_request
        )

    def on_http_request(self, method, url, params):
        self.stdout.write('{} {}\n'.format(
            termcolor.colored(method, 'green'), url))
        self.stdout.write('params: {}\n'.format(
            urllib.urlencode(params)
        ))

    def print_response(self, status_code, response):
        self.stdout.write('Status code: ')

        # write red, yellow, or green depending on the http status code
        if status_code < 300:
            self.stdout.write(termcolor.colored(status_code, 'green'))
        elif status_code < 400:
            self.stdout.write(termcolor.colored(status_code, 'yellow'))
        else:
            self.stdout.write(termcolor.colored(status_code, 'red'))

        self.stdout.write('\nResponse:\n')
        self.printer.pprint(response)

    # by default emptyline() repeats the previous command; I prefer it to do
    # nothing.  You can always press up-enter.
    def emptyline(self):
        return False

    # exit on Ctrl-D.
    def do_EOF(self, line):
        self.stdout.write('\n')
        return True

    # create command wrappers for all of the different API calls
    do_project_group_list = make_cmd('project_group_list',
                                     [], ['page', 'per_page'])
    do_project_group_show = make_cmd('project_group_show', ['id'])
    do_project_group_create = make_cmd('project_group_create',
                                       ['name'], ['locale'])
    do_project_group_delete = make_cmd('project_group_delete', ['id'],
                                       confirm=True)
    do_project_group_languages = make_cmd('project_group_languages', ['id'])

    do_project_list = make_cmd('project_list', ['group_id'])
    do_project_show = make_cmd('project_show', ['id'])
    do_project_create = make_cmd('project_create',
                                 ['group_id', 'type'],
                                 ['name', 'description'])
    do_project_update = make_cmd('project_update',
                                 [], ['name', 'description'])
    do_project_delete = make_cmd('project_delete', ['id'], confirm=True)
    do_project_languages = make_cmd('project_languages', ['id'])

    do_project_type_list = make_cmd('project_type_list')

    do_file_list = make_cmd('file_list', ['project_id'], ['page', 'per_page'])
    do_file_upload = make_cmd('file_upload',
                              ['project_id', 'file_name', 'file_format'],
                              ['locale', 'is_keeping_all_strings'])

    do_file_delete = make_cmd('file_delete', ['project_id', 'file_name'],
                              confirm=True)

    do_translation_export = make_cmd(
        'translation_export',
        ['project_id', 'locale', 'source_file_name'],
        ['export_file_name'])
    do_translation_export_multilingual = make_cmd(
        'translation_export_multilingual',
        ['project_id', 'source_file_name'],
        ['export_file_name', 'file_format']
    )
    do_translation_status = make_cmd('translation_status',
                                     ['project_id', 'file_name', 'locale'])
    do_import_task_list = make_cmd('import_task_list',
                                   ['project_id'],
                                   ['page', 'per_page', 'status'])
    do_import_task_show = make_cmd('import_task_show',
                                   ['project_id', 'import_id'])

    # wrapper for the screenshot stuff is not yet implemented
    # do_screenshot =

    do_quotation_show = make_cmd('quotation_show',
                                 ['project_id', 'files', 'to_locale'],
                                 ['is_including_not_translated',
                                  'is_including_not_approved',
                                  'is_including_outdated',
                                  'specialization'])

    do_order_list = make_cmd('order_list',
                             ['project_id'], ['page', 'per_page'])
    do_order_show = make_cmd('order_show',
                             ['project_id', 'order_id'])
    do_order_create = make_cmd('order_create',
                               ['project_id', 'files', 'to_locale'],
                               ['is_including_not_translated',
                                'is_including_not_approved',
                                'is_including_outdated',
                                'translator_type',
                                'tone', 'specialization', 'note'])

    do_locale_list = make_cmd('locale_list')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {} <api_key> <api_secret>'.format(sys.argv[0]))
    else:
        interpreter = Interpreter(sys.argv[1], sys.argv[2])
        interpreter.cmdloop()
