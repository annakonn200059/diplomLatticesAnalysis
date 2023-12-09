from setuptools import setup, find_packages

with open('requirements.txt', encoding='UTF-8') as f:
    requirements = f.read().splitlines()

setup(
    name='konnova_lattices_analysis',
    version='1.0.0',
    packages=find_packages(),
    long_description=open('README.md').read(),
    install_requires=requirements,
    author='Ann Konnova',
    author_email='konnova.anya2016@yandex.ru',
    license='MIT',
)
