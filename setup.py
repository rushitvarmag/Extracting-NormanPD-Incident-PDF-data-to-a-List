from setuptools import setup, find_packages

setup(
	name='project0',
	version='1.0',
	author='RushitVarmaGadiraju',
	author_email='vgadiraju@ufl.edu',
	packages=find_packages(exclude=('tests', 'docs', 'resources')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)