### Author: Devin Whitten
### Main driver for normalization routine, intended for SEGUE medium-resolution spectra.

import numpy as np
import pandas as pd
import sys, os
#sys.path.append("interface")
from spectrum import Spectrum
from astropy.io import fits
import norm_functions


def normalize(wavelength, flux, sigma=30):
    spec = Spectrum(wavelength, flux, fits=False)
    spec.generate_inflection_segments(sigma=sigma)
    spec.assess_segment_variation()
    spec.define_cont_points()
    spec.set_segment_continuum()
    spec.set_segment_midpoints()

    spec.spline_continuum()
    spec.normalize()

    return spec.flux_norm, spec.continuum
