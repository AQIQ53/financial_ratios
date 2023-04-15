from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in financial_ratios/__init__.py
from financial_ratios import __version__ as version

setup(
	name="financial_ratios",
	version=version,
	description="Financial Ratio Calculating App",
	author="Aqiq Solutions Ltd",
	author_email="info@aqiqsolutions.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
