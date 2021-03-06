#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import os
import json

import chevron

SPECS_PATH = os.path.join('spec', 'specs')
SPECS = [path for path in os.listdir(SPECS_PATH) if path.endswith('.json')]
STACHE = chevron.render


def _test_case_from_path(json_path):
    json_path = '%s.json' % json_path

    class MustacheTestCase(unittest.TestCase):
        """A simple yaml based test case"""

        def _test_from_object(obj):
            """Generate a unit test from a test object"""

            def test_case(self):
                result = STACHE(obj['template'], obj['data'],
                                partials_dict=obj.get('partials', {}))

                self.assertEqual(result, obj['expected'])

            test_case.__doc__ = 'suite: {0}    desc: {1}'.format(spec,
                                                                 obj['desc'])
            return test_case

        with open(json_path, 'r') as f:
            yaml = json.load(f)

        # Generates a unit test for each test object
        for i, test in enumerate(yaml['tests']):
            vars()['test_' + str(i)] = _test_from_object(test)

    # Return the built class
    return MustacheTestCase

# Create TestCase for each json file
for spec in SPECS:
    # Ignore optional tests
    if spec[0] != '~':
        spec = spec.split('.')[0]
        globals()[spec] = _test_case_from_path(os.path.join(SPECS_PATH, spec))


class ExpandedCoverage(unittest.TestCase):

    def test_unclosed_sections(self):
        test1 = {
            'template': '{{# section }} oops {{/ wrong_section }}'
        }

        test2 = {
            'template': '{{# section }} end of file'
        }

        self.assertRaises(SyntaxError, chevron.render, **test1)
        self.assertRaises(SyntaxError, chevron.render, **test2)

    def test_unicode_basic(self):
        args = {
            'template': '(╯°□°）╯︵ ┻━┻'
        }

        result = chevron.render(**args)
        expected = '(╯°□°）╯︵ ┻━┻'

        self.assertEqual(result, expected)

    def test_unicode_variable(self):
        args = {
            'template': '{{ table_flip }}',
            'data': {'table_flip': '(╯°□°）╯︵ ┻━┻'}
        }

        result = chevron.render(**args)
        expected = '(╯°□°）╯︵ ┻━┻'

        self.assertEqual(result, expected)

    def test_unicode_partial(self):
        args = {
            'template': '{{> table_flip }}',
            'partials_dict': {'table_flip': '(╯°□°）╯︵ ┻━┻'}
        }

        result = chevron.render(**args)
        expected = '(╯°□°）╯︵ ┻━┻'

        self.assertEqual(result, expected)

    def test_listed_data(self):
        args = {
            'template': '{{# . }}({{ . }}){{/ . }}',
            'data': [1, 2, 3, 4, 5]
        }

        result = chevron.render(**args)
        expected = '(1)(2)(3)(4)(5)'

        self.assertEqual(result, expected)

    def test_main(self):
        result = chevron.main('tests/test.mustache', 'tests/data.json',
                              partials_path='tests')

        with open('tests/test.rendered', 'r') as f:
            expected = f.read()

        self.assertEqual(result, expected)

    def test_recursion(self):
        args = {
            'template': '{{# 1.2 }}{{# data }}{{.}}{{/ data }}{{/ 1.2 }}',
            'data': {'1': {'2': [{'data': ["1", "2", "3"]}]}}
        }

        try:
            result = chevron.render(**args)
        except RuntimeError:
            result = 'recursion'
        expected = '123'

        self.assertEqual(result, expected)

    def test_unicode_inside_list(self):
        args = {
            'template': '{{#list}}{{.}}{{/list}}',
            'data': {'list': ['☠']}
        }

        result = chevron.render(**args)
        expected = '☠'

        self.assertEqual(result, expected)


# Run unit tests from command line
if __name__ == "__main__":
    unittest.main()
