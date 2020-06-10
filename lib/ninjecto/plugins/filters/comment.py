# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Filter to comment out a section of text.
"""

from jinja2.filters import environmentfilter


@environmentfilter
def filter_comment(environment, text, style='python', **kwargs):
    """
    Filter to comment out a section of text.

    :param str text: Text to comment out.
    :param str style: Formatting style for different languages.
     Available options are: ``bash``, ``c``, ``cblock``, ``cdoc``, ``cpp``,
     ``cppblock``, ``csharp``, ``csharpblock``, ``doxygen``, ``erlang``,
     ``html``, ``java``, ``javablock``, ``javadoc``, ``javascript``,
     ``javascriptblock``, ``js``, ``jsblock``, ``jsdoc``, ``openscad``,
     ``openscadblock``, ``perl``, ``phpdoc``, ``powershell``, ``python``,
     ``ruby``, ``sql``, ``swift``, ``swiftblock``, ``toml``, ``xml`` and
     ``yaml``. You may also use ``None`` or empty string ``''`` to not apply
     the comment filter at all, which can be useful when using it
     conditionally.

    :param kwargs: Style overrides. Possible keys are:

     - ``newline`` (str): Newline character to use. It defaults to Jinja's
       ``Environment.newline_sequence``.
     - ``beginning`` (str): String to place at the beginning of the comment.
       Usually for block style comments.
     - ``prefix`` (str): Decoration to use to prefix the text.
     - ``prefix_count`` (int): Number of prefixes to prepend to the text.
     - ``decoration`` (str): String to use at the beginning of each line.
     - ``postfix`` (str): Decoration to use to postfix the text.
     - ``postfix_count`` (int): Number of postfixes to append to the text.
     - ``end`` (str): String to place at the end of the comment.
       Usually for block style comments.

    :return: The text commented out.
    :rtype: str
    """

    if not style:
        return text

    families = {
        'pound': {
            'style': {
                'decoration': '# ',
            },
            'keys': [
                'python', 'bash', 'ruby', 'perl', 'yaml', 'toml', 'powershell',
            ],
        },
        'percent': {
            'style': {
                'decoration': '% ',
            },
            'keys': [
                'erlang',
            ],
        },
        'csingle': {
            'style': {
                'decoration': '// ',
            },
            'keys': [
                'c', 'cpp', 'csharp', 'java', 'javascript', 'js', 'swift',
                'openscad',
            ],
        },
        'cblock': {
            'style': {
                'beginning': '/*',
                'decoration': ' * ',
                'end': ' */',
            },
            'keys': [
                'cblock', 'cppblock', 'csharpblock', 'javablock',
                'javascriptblock', 'jsblock', 'swiftblock', 'openscadblock',
            ],
        },
        'cdoc': {
            'style': {
                'beginning': '/**',
                'decoration': ' * ',
                'end': ' */',
            },
            'keys': [
                'cdoc', 'doxygen', 'javadoc', 'phpdoc', 'jsdoc',
            ],
        },
        'pydoc': {
            'style': {
                'beginning': '"""',
                'decoration': '',
                'end': '"""',
                'prefix_count': 1,
            },
            'keys': [
                'pydoc',
            ],
        },
        'markup': {
            'style': {
                'beginning': '<!--',
                'decoration': ' - ',
                'end': '-->',
            },
            'keys': [
                'html', 'xml',
            ],
        },
        'db': {
            'style': {
                'decoration': '-- ',
            },
            'keys': [
                'sql',
            ],
        }
    }

    index = {
        key: registry['style']
        for registry in families.values()
        for key in registry['keys']
    }
    # print(', '.join(sorted(index.keys())))

    # Pointer to the right comment type
    styleopts = index[style]

    prepostfix = kwargs.get('decoration', styleopts['decoration']).rstrip()

    # Default params
    p = {
        'newline': environment.newline_sequence,
        'beginning': '',
        'prefix': prepostfix,
        'prefix_count': 0,
        'decoration': '',
        'postfix': prepostfix,
        'postfix_count': 0,
        'end': ''
    }

    # Update default params
    p.update(styleopts)
    p.update(kwargs)

    str_beginning = ''
    if p['beginning']:
        str_beginning = '{}{}'.format(p['beginning'], p['newline'])

    str_prefix = ''
    if p['prefix']:
        if p['prefix'] != p['newline']:
            str_prefix = (
                '{}{}'.format(p['prefix'], p['newline'])
            ) * int(p['prefix_count'])
        else:
            str_prefix = p['newline'] * int(p['prefix_count'])

    # Prepend each line of the text with the decorator
    str_text = '{}{}'.format(
        p['decoration'],
        text.replace(
            p['newline'],
            '{}{}'.format(p['newline'], p['decoration'])
        )
    )

    # Remove trailing spaces when only decorator is on the line
    str_text = str_text.replace(
        '{}{}'.format(p['decoration'], p['newline']),
        '{}{}'.format(p['decoration'].rstrip(), p['newline'])
    )

    str_postfix = p['newline'].join(
        [''] + [p['postfix']] * p['postfix_count']
    )

    str_end = ''
    if p['end']:
        str_end = '{}{}'.format(p['newline'], p['end'])

    # Compose substrings for the final string
    return ''.join([
        str_beginning,
        str_prefix,
        str_text,
        str_postfix,
        str_end,
    ])


__all__ = [
    'filter_comment',
]
