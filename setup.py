from setuptools import setup, find_packages
from src.slime_core import __version__

README = 'README.md'

setup(
    name='slime_core',
    version=__version__,
    packages=find_packages('./src'),
    package_dir={'': 'src'},
    include_package_data=False,
    entry_points={},
    install_requires=[],
    url='https://github.com/SlimeAI/slime_core',
    author='SlimeAI',
    author_email='liuzikang0625@gmail.com',
    license='MIT License',
    description='slime_core',
    long_description=open(README, encoding='utf-8').read(),
    long_description_content_type='text/markdown'
)
