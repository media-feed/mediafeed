from setuptools import find_packages, setup


version = __import__('mediafeed').__version__
with open('README.rst', 'rb') as f:
    long_description = f.read().decode('utf-8')


setup(
    name='MediaFeed',
    version=version,
    packages=find_packages(),

    install_requires=[
        'bottle',
        'sqlalchemy',
    ],

    author='Eduardo Klosowski',
    author_email='eduardo_klosowski@yahoo.com',

    description='Download de arquivos de fonte de mídias',
    long_description=long_description,
    license='MIT',
    url='https://github.com/eduardoklosowski/mediafeed',
)
