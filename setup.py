from setuptools import setup, find_packages

setup(
    name='courtrss',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'feedparser',
        'PyYAML',
        'requests',
        'tkinter',
    ],
    entry_points={
        'console_scripts': [
            'courtrss = courtrss.rss_feed:main',
        ],
    },
    author='Jon Cavallie Mester',
    description='A package to monitor court RSS feeds for keywords.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jonmest/courtrss',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
