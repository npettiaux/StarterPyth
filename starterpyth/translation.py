import copy
from errno import ENOENT
import gettext
import os.path
import pkg_resources

__author__ = 'flanker'
__all__ = ['translation', 'gettext', 'lgettext', 'ugettext', 'ngettext', 'lngettext', 'ungettext']


# Locate a .mo file using the gettext strategy
def __find(domain, localedir='locale', languages=None, all_=False):
    # Get some reasonable defaults for arguments that were not supplied
    if languages is None:
        languages = []
        for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            if val:
                languages = val.split(':')
                break
        if 'C' not in languages:
            languages.append('C')
    # now normalize and expand the languages
    nelangs = []
    for lang in languages:
        for nelang in gettext._expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)
    # select a language
    if all_:
        result = []
    else:
        result = None
    for lang in nelangs:
        if lang == 'C':
            break
        mofile = '%s/%s/%s/%s.mo' % (localedir, lang, 'LC_MESSAGES', domain)
        if pkg_resources.resource_exists('starterpyth', mofile):
            if all_:
                result.append(mofile)
            else:
                return mofile
    return result


def translation(domain, localedir='locale', languages=None,
                class_=None, fallback=False, codeset=None):
    if class_ is None:
        class_ = gettext.GNUTranslations
    mofiles = __find(domain, localedir, languages, all_=True)
    if not mofiles:
        if fallback:
            return gettext.NullTranslations()
        raise IOError(ENOENT, 'No translation file found for domain', domain)
    # Avoid opening, reading, and parsing the .mo file after it's been done
    # once.
    result = None
    for mofile in mofiles:
        key = (class_, mofile)
        t = gettext._translations.get(key)
        if t is None:
            with pkg_resources.resource_stream('starterpyth', mofile) as fp:
                t = gettext._translations.setdefault(key, class_(fp))
        # Copy the translation object to allow setting fallbacks and
        # output charset. All other instance data is shared with the
        # cached object.
        t = copy.copy(t)
        if codeset:
            t.set_output_charset(codeset)
        if result is None:
            result = t
        else:
            result.add_fallback(t)
    return result


__trans = translation('starterpyth', fallback=True)

gettext = __trans.gettext
lgettext = __trans.lgettext
ugettext = __trans.ugettext
ngettext = __trans.ngettext
lngettext = __trans.lngettext
ungettext = __trans.ungettext


if __name__ == '__main__':
    import doctest
    doctest.testmod()