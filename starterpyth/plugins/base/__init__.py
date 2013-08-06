import datetime
import os.path
import shutil
import pkg_resources
from starterpyth import defaults
from starterpyth.fields import RegexpInput, CharInput, ChoiceInput, BooleanInput

__author__ = 'flanker'

from starterpyth.core import Plugin
from starterpyth.translation import ugettext as _


licenses = [('cecill a', 'cecill_a'), ('cecill b', 'cecill_b'), ('cecill c', 'cecill_c'), ('lpgl 2', 'lgpl_2'),
            ('lgpl 3', 'lgpl3'), ('gpl2', 'gpl_2'), ('gpl3', 'gpl_3'), ('other', 'Other')]
license_names = {
    'cecill_a': 'CeCILL-A', 'cecill_b': 'CeCILL-B', 'cecill_c': 'CeCILL-C', 'lgpl_2': 'LGPL 2',
    'lgpl_3': 'LGPL 3', 'gpl_2': 'GPL 2', 'gpl 3': 'GPL 3', 'Other': 'Other license',
}
pyversions = [('2.6', 2.6), ('2.7', 2.7), ('3.0', 3.0), ('3.1', 3.1), ('3.2', 3.2), ('3.3', 3.3), ('3.4', 3.4)]


class BasePlugin(Plugin):
    def update_global_context(self, context, filters):
        project_name = RegexpInput(_('Project name'), regexp=r'[A-Za-z]\w*', default='Project').input()
        module_name = RegexpInput(_('Python module name'), regexp=r'[A-Za-z]\w*', default=project_name.lower()).input()
        company = CharInput(_('Company name'), max_length=255, blank=True, default=defaults.COMPANY).input()
        author = CharInput(_('Author name'), max_length=255, default=defaults.AUTHOR).input()
        email = RegexpInput(_('Author e-mail'), default='%s@%s' % (author, company),
                            regexp=r'[\w_\-\.]+@[\w_\-\.]').input()
        license_ = ChoiceInput(_('License'), choices=licenses, blank=True, default='cecill b').input()
        pyversion = ChoiceInput(_('Minimum Python version'), choices=pyversions, default='2.7').input()
        use_2to3 = False
        use_six = False
        py3compat = 'source'
        if pyversion < 3.:
            use_six = BooleanInput(_('Use six tool for Python 3 compatibility'), default=True).input()
            if not use_six:
                use_2to3 = BooleanInput(_('Use 2to3 tool for Python 3 compatibility'), default=True).input()
                py3compat = '2to3' if use_2to3 else None
            else:
                py3compat = 'six'

        module_version = RegexpInput(_('Initial version'), regexp=r'[\w\.\-]', default='0.1').input()
        context['project_name'] = project_name
        context['module_name'] = module_name
        context['use_2to3'] = use_2to3
        context['use_six'] = use_six
        context['py3compat'] = py3compat
        context['license'] = license_names[license_]
        if license_ != 'Other':
            with pkg_resources.resource_stream('starterpyth.plugins.base', 'licenses/%s.txt' % license_) as fd:
                context['license_content'] = fd.read().decode('utf-8')
        else:
            context['license_content'] = ''
        context['pyversion'] = pyversion
        if py3compat == 'six':
            filters['unicode'] = lambda x: 'six.u("{0}")'.format(x.replace("\"", "\\\""))
            filters['binary'] = lambda x: 'six.b("{0}")'.format(x.replace("\"", "\\\""))
            context['unicode'] = 'six.text_type'
            context['binary'] = 'six.binary_type'
            context['install_requires'].append('six')
            context['setup_requires'].append('six')
            context['tests_requires'].append('six')
        elif py3compat == 'source':
            filters['unicode'] = lambda x: '"{0}"'.format(x.replace("\"", "\\\""))
            filters['binary'] = lambda x: 'b"{0}"'.format(x.replace("\"", "\\\""))
            context['unicode'] = 'str'
            context['binary'] = 'bytes'
        else:  # no compatibility or compatibility through 2to3
            filters['unicode'] = lambda x: 'u"{0}"'.format(x.replace("\"", "\\\""))
            filters['binary'] = lambda x: '"{0}"'.format(x.replace("\"", "\\\""))
            context['unicode'] = 'unicode'
            context['binary'] = 'str'
        context['company'] = company
        context['email'] = email
        context['author'] = author
        context['module_version'] = module_version
        context['install_requires'].append('distribute')
        context['setup_requires'].append('distribute')
        context['tests_requires'].append('distribute')
        context['classifiers'].append('Programming Language :: Python')
        if py3compat in ('source', 'six'):
            context['classifiers'].append('Programming Language :: Python :: 3')
        context['year'] = datetime.date.today().year
        context['doc_urls']['python'] = ('http://docs.python.org/%.1f/' % pyversion,
                                         'externals/python_%.1f.inv' % pyversion)
        path = os.path.join(context['project_root'], project_name)
        if os.path.isdir(path):
            rm = ChoiceInput(_('The folder %(f)s already exists. Remove it?') % {'f': path}, default='yes',
                             choices=(('yes', 'yes'), ('no', 'no'))).input()
            if rm == 'yes':
                shutil.rmtree(path)

    def get_resources(self):
        return 'starterpyth.plugins.base', 'templates'