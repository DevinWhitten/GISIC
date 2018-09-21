Gaussian Inflection Spline Interpolation Continuum (GISIC)
==========================================================
GISIC is a python package for normalization of astronomical spectra.
It is designed to accommodate spectra with heavy molecular features due to high
elemental abundance enhancements.
GISIC performs a gaussian smoothing of the flux array, and identifies molecular bands based on a numerical gradient. Continuum points are then interpolated with a cubic spline.

Author: Devin D. Whitten

Installation
------------

```python
pip install GISIC
```


Documentation
-------------

Coming soon.

```python
wave, norm_flux, continuum = GISIC.normalize(wave, flux, sigma=30)
```
<!-- Animated GIF of AutoGUI -->
<img src="https://github.com/DevinWhitten/GISIC/blob/master/images/continuum_animation.gif" width="80%"
style="display:block;margin: 0 auto;">
