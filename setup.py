from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name="GISIC",
      version='1.04',
      description="Gaussian Inflection Spline Interpolation Continuum",
      author='Devin D. Whitten',
      author_email='dwhitten@nd.edu',
      long_description=long_description,
      long_description_content_type='text/markdown',
      license="ND",
      packages=['GISIC'],
      zip_safe=False
)
