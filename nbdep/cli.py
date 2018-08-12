#!/usr/bin/env python
"""nbdep get runtime deps for code blocks in a notebook
Usage:
    nbdep <notebook>... 
"""

import inspect
import modulefinder
import types
import nbformat
import pkg_resources
from pathlib import Path
from IPython import embed

basic_match = {'python':'import'}

def python(lines):
    # filter from lines
    src = '\n'.join(lines)
    code = compile(src, 'internal_imports', 'exec')
    exec(src)

    g = locals()
    modules = sorted(set(m for v in g.values()
                         for m in (inspect.getmodule(v),)
                         if m),
                     key=lambda m:m.__name__)
                  
    # TODO modules -> 

    pkgs = []
    for m in modules:
        try:
            pkgname = m.__name__.split('.')[0]
            pkg = pkg_resources.get_distribution(pkgname)
            mf = modulefinder.ModuleFinder(m.__file__)
            print(list(mf.modules.items()))
            #pkgs.append(pkg)
            #embed()
            #print(pkg.project_name, pkg.version)
            pkgs.append((pkg.project_name, pkg.version))
        except pkg_resources.DistributionNotFound:
            # TODO corelibs?
            print('WARNING: missing', m.__name__)

    embed()

    return pkgs


lang_report = {'python':python}


def read_notebook(file):
    path = Path(file).expanduser().absolute().resolve()
    with open(path.as_posix(), 'rt') as f:
        notebook = nbformat.read(f, as_version=4)

    lang_info = notebook['metadata']['language_info']
    lang = lang_info['name']

    lib_lines = [l for c in notebook['cells']
                 if c['cell_type'] == 'code'
                 for l in c['source'].split('\n')
                 if basic_match[lang] in l]
    report = lang_report[lang](lib_lines)

    return report

def test():
    lines = ('import requests',
             'import rdflib',
             'import IPython')
    l = python(lines)
    print(l)

test()
def main():
    from docopt import docopt
    args = docopt(__doc__)
    reports = [read_notebook(nb) for nb in args['<notebook>']]
    print(reports)


if __name__ == '__main__':
    main()
