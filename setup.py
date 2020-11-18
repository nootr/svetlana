from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='svetlana',
    version='0.1',
    description='A WebDiplomacy notification bot for Discord.',
    long_description=long_description,
    author='Joris Hartog',
    author_email='jorishartog@gmail.com',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3',
    scripts=[
        'scripts/svetlana',
        'scripts/run_svetlana.py',
    ],
    install_requires=[
        'requests',
        'discord',
        'asyncio',
    ],
)
