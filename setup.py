from setuptools import setup, find_packages
import pathlib

# Загрузка зависимостей из requirements.txt
here = pathlib.Path(__file__).parent.resolve()
with open(here / "requirements.txt") as f:
    requirements = f.read().splitlines()
    
setup(
    name='tactic',
    version='1.0.0',
    description='A tactic - implementation of clean architecture on Python contains some tactical patterns from DDD',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='DimaOshchepkov',
    author_email='odo.2003@yandex.ru',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.10.8',
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
