from pathlib import Path
from setuptools import setup, find_packages
from yaml import safe_load

with open(Path(__file__).parent / 'CITATION.cff') as f:
    version = safe_load(f)['version']

if __name__ == "__main__":
    setup(
        name = 'sigfig',
        description = 'Python library for rounding numbers (with expected results)',

        version = version,
        license = 'MIT',
        url = 'https://sigfig.readthedocs.io/',
        docs_url = 'https://sigfig.readthedocs.io/',
        bugtrack_url = 'https://github.com/drakegroup/sigfig/issues',
        install_requires =['SortedContainers'],
        packages = find_packages(exclude = ['doc', 'test']),
        long_description = open(Path(__file__).parent / 'README.rst', encoding='utf-8').read()[1:],
        long_description_content_type = 'text/x-rst',
        author = 'Mike & Travis',
        author_email = 'mike.busuttil@gmail.com, valdezt@gmail.com',
        maintainer = 'Mike Busuttil',
        maintainer_email = 'mike.busuttil@gmail.com',

        keywords = ['round', 'rounding', 'significant figures', 'significant digits',
                    'sigfigs', 'sigdigs', 'decimals', 'uncertainty', 'uncertainties',
                    'numeric', 'numerical', 'number', 'numbers', 'data',
                    'format', 'style',  'publication'],
        classifiers = ['Development Status :: 5 - Production/Stable',
                    'Intended Audience :: Developers',
                    'Intended Audience :: Education',
                    'Intended Audience :: Financial and Insurance Industry',
                    'Intended Audience :: Healthcare Industry',
                    'Intended Audience :: Other Audience',
                    'Intended Audience :: Manufacturing',
                    'Intended Audience :: Science/Research',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 2',
                    'Programming Language :: Python :: 3',
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 3.0',
                    'Programming Language :: Python :: 3.1',
                    'Programming Language :: Python :: 3.2',
                    'Programming Language :: Python :: 3.3',
                    'Programming Language :: Python :: 3.4',
                    'Programming Language :: Python :: 3.5',
                    'Programming Language :: Python :: 3.6',
                    'Programming Language :: Python :: 3.7',
                    'Programming Language :: Python :: 3.8',
                    'Programming Language :: Python :: 3.9',
                    'Programming Language :: Python :: 3.10',
                    'Programming Language :: Python :: 3.11',
                    'Programming Language :: Python :: 3.12',
                    'Topic :: Education',
                    'Topic :: Education :: Computer Aided Instruction (CAI)',
                    'Topic :: Office/Business :: Financial',
                    'Topic :: Scientific/Engineering',
                    'Topic :: Scientific/Engineering :: Information Analysis',
                    'Topic :: Scientific/Engineering :: Mathematics',
                    'Topic :: Scientific/Engineering :: Physics',
                    'Topic :: Software Development',
                    'Topic :: Software Development :: Libraries',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                    'Topic :: Utilities']
    )
