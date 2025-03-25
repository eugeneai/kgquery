# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)

try:
    import multiprocessing
except ImportError:
    pass

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.rst')).read()

version = '0.2.0'


setup(name='kgquery',
      version=version,
      description="Knowledge Graph Query Set",
      long_description=README + '\n\n' + NEWS,
      # classifiers=[
      #     'Development Status :: 5 - Production/Stable',
      #     'Environment :: Console',
      #     'Environment :: Plugins',
      #     'Framework :: Paste',
      #     'Intended Audience :: Developers',
      #     'License :: OSI Approved :: GNU General Public License (GPL)',
      #     'Operating System :: OS Independent',
      #     'Programming Language :: Python',
      #     'Topic :: Software Development :: Code Generators',
      # ],
      keywords='',
      author='Evgeny Cherkashin',
      author_email='eugeneai@irnok.net',
      url="https://github.com/eugeneai/kgquery",
      license='GNU General Public License v3',
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "Paste",
          "PasteScript",
          "rdflib",
          "chevron"
      ],
      # tests_require=['nose'],
      # test_suite='nose.collector',
      # entry_points="""
      # [paste.paster_create_template]
      # modern_package = modern_package:ModernPackageTemplate
      # """,
      )
