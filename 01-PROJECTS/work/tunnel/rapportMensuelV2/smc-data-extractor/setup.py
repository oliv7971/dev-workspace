from setuptools import setup, find_packages

setup(
    name='smc-data-extractor',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A tool for extracting and processing SMC data from Excel files.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'openpyxl',
        'reportlab',
        'PyYAML',
        'regex',
    ],
    entry_points={
        'console_scripts': [
            'smc_gui=smc_gui:main',
            'smc_evolutions=smc_evolutions:main',
            'produire_recaps=produire_recaps:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)