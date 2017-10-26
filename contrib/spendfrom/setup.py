# Copyright (c) 2013 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
from distutils.core import setup
setup(name='MATERspendfrom',
      version='1.0',
      description='Command-line utility for materia "coin control"',
      author='Gavin Andresen',
      author_email='gavin@materiafoundation.org',
      requires=['jsonrpc'],
      scripts=['spendfrom.py'],
      )
