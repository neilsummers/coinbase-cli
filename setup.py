from pathlib import Path
import shutil

from setuptools import setup, find_packages

root = Path(__file__).parent

with (root / 'requirements.txt').open('r') as f:
    requirements = f.read().splitlines()

with (root / 'README.md').open('r') as f:
    README = f.read()

key_file = Path('coinbase_cloud_api_key.json')
if Path(key_file).exists():
    shutil.move(key_file, root/'coinbase_cli')

if not (root/'coinbase_cli'/key_file).exists():
    raise FileNotFoundError(
        'Generate Coinbase Advanced Trade API Key at'
        'https://docs.cloud.coinbase.com/advanced-trade-api/docs/rest-api-auth#creating-trading-keys'
        'and download to current directory')

setup(
    name='coinbase-cli',
    version='0.1',
    author='Neil Summers',
    license='MIT',
    url='',
    description='Command Line Interface utilizing the "Coinbase Advanced API Python SDK"',
    long_description=README,
    long_description_content_type='text/markdown',
    keywords=['Coinbase', 'Advanced Trade', 'API', 'Advanced API', 'CLI'],
    install_requires=[req for req in requirements],
    scripts=['coinbase_cli/coinbase'],
    packages=find_packages(where='.'),
    package_data={'coinbase_cli': ['coinbase_cloud_api_key.json']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.10',
)
