from setuptools import setup, find_packages

setup(
    name='create-dmp',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'create_dmp': ['create-new-dmp.conf'],
        'create_dmp': ['.env'],
        'create_dmp': ['templates/*.html']
    },
    description='A tool to create Data Management Plans (DMPs) and project records from funder grant data.',
    author='Urban Andersson',
    install_requires=[
        'requests',
        'python-dotenv'
    ],
    entry_points={
    'console_scripts': [
        'create-dmp=create_dmp.main:main'
    ]
}
)
