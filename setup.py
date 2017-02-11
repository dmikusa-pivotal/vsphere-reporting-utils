from distutils.core import setup
import os

setup(name='vsphere_reporting_utils',
      author='Daniel Mikusa',
      author_email='dmikusa@pivotal.io',
      url='https://github.com/dmikusa-pivotal/vsphere_reporting_utils',
      license='Apache-2.0',
      description='Reporting utilities to get information out of vSphere.',
      long_description=open('README.rst', 'r').read(),
      version='1.0.0',
      py_modules=['cli_helper', 'vsphere_api', 'vsphere_objects'],
      scripts=['find_abandoned_files.py', 'report_vm_du.py'],
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7"
      ],
      keywords='vsphere reports',
      install_requires=['pyvmomi', 'hurry.filesize'])

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')
