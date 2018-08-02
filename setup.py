from setuptools import setup, find_packages

setup(
    name='tinyhttp',
    version='0.3',
    author='Wincer',
    long_description=open('README.rst').read(),
    author_email='WincerChan@gmail.com',
    url='https://github.com/WincerChan/Tiny-Http',
    description='Async static HTTP server.',
    packages=find_packages(),
    license='GPL-3.0',
    entry_points={
        'console_scripts': [
            'tinyhttp=tinyhttp.async.asyncserver:main'
        ]
    }
)
