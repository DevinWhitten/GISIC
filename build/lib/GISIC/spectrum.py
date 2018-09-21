#Author: Devin Whitten
#Date: Nov 12, 2016
# This is will serve as the interface for the normalization function.
# So just defining some functions in here.

## Modifying to operate on synthetic spectra


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interp
from astropy.table import Table
from scipy.ndimage.filters import gaussian_filter
from GISIC.norm_functions import in_molecular_band
from GISIC.segment import Segment

################################
#Spectrum Class Definition
################################
class Spectrum():
    def __init__(self, wavelength, flux):


        self.wavelength = wavelength

        self.flux       = flux


        self.segments = None
        self.mad_global = None

        return

    def generate_segments(self, bins=25):

        ### Uniformally bin the spectrum. Maybe outdated.
        self.segments = [Segment(wl, flux) for wl, flux in zip(np.array_split(self.wavelength, bins), np.array_split(self.flux, bins))]
        print(self.segments)
        ### Need to handle the end points!!!!!!
        self.segments[0].is_edge("left")
        self.segments[-1].is_edge('right')

        [segment.get_statistics() for segment in self.segments]
        return


    def generate_inflection_segments(self, sigma=30, width=30):
        print("... generate_inflection_segments()")
        ### This method of generating segments bins for continuum definition is slightly different.
        ### Based on the inflection points of a smoothed spectrum


        self.smooth = gaussian_filter(self.flux, sigma=sigma)

        self.d1 = np.gradient(self.smooth)
        self.d2 = np.gradient(self.d1)
        #### put on the same scale
        self.d1 = self.d1/max(self.d1)
        self.d2 = self.d2/max(self.d2)

        ## I guess I should define a dataframe for ease
        hack = Table([self.wavelength, self.flux, self.d1, self.d2],
              names=('wave', 'flux', 'd1', 'd2'),
              dtype=('f8', 'f8', 'f8', 'f8'))

        self.frame = pd.DataFrame({"wave":hack['wave'],
                                   "flux": hack['flux'],
                                   "d1":  hack['d1'],
                                   "d2":  hack['d2']})

        #### We need to find the self.ZEROS in the second derivative
        self.ZEROS = []
        for i in range(len(self.d2) - 1):
            if (self.d2[i] * self.d2[i+1] < 0.0): # where flux crosses x-axis
                ## might as well take the midpoint of the wavelength
                self.ZEROS.append((self.frame.wave[i] + self.frame.wave[i+1])/2.)
            elif self.d2[i] == 0.0:
                self.ZEROS.append(self.frame.wave[i])
        ## Now that we have the ZEROS, let's build the segments
        ## ideally the segments should be variable to determine optimal length
        ## for now we will just set a hard value.

        MINIMUMS = []
        #### Look between the self.ZEROS
        for i in range(len(self.ZEROS) - 1):

            #print(self.frame[self.frame['wave'].between(4000, 5000, inclusive=True)])
            #print("HERE")
            SEGMENT = self.frame[self.frame['wave'].between(self.ZEROS[i], self.ZEROS[i+1], inclusive=True)].copy()
            ### I don't care about positive peaks
            ### so if everything is negative
            if len(SEGMENT[SEGMENT['d2'] < 0.0]) > 0.8*len(SEGMENT['d2']):
                MIN = SEGMENT[SEGMENT['d2'] == min(SEGMENT['d2'])].copy()
                MIN.loc[:, "size"] = len(SEGMENT)
                MINIMUMS.append(MIN)

        EXTREMA = pd.concat(MINIMUMS)

        #print("ZEROS:   ", self.ZEROS)
        #print("Median extrema:    ", np.median(EXTREMA['d2']), np.std(EXTREMA['d2']))
        #EXTREMA = EXTREMA[EXTREMA['d2'] < np.median(EXTREMA['d2']) + np.std(EXTREMA['d2'])]
        ########################################################################
        self.segments = []
        for i, row in EXTREMA.iterrows():
            #### G-band avoidance
            if not in_molecular_band(row['wave'], tol=10):
                #print(~norm_functions.in_molecular_band(row['wave'], tol=10))
                SEGMENT = self.frame[self.frame['wave'].between(row['wave'] - int(width/2), row['wave']+ int(width/2), inclusive=True)]
                self.segments.append(Segment(np.array(SEGMENT['wave']), np.array(SEGMENT['flux'])))
            else:
                print(row['wave'], " fail")

        ### need to add the endpoints
        self.segments.insert(0, Segment(np.array(self.frame['wave'].iloc[0:width]), np.array(self.frame['flux'].iloc[0:width])))
        self.segments.append(Segment(np.array(self.frame['wave'].iloc[-width:]), np.array(self.frame['flux'].iloc[-width:])))

        self.segments[0].is_edge("left")
        self.segments[-1].is_edge('right')

        [segment.get_statistics() for segment in self.segments]

        return




    def assess_segment_variation(self):
        print("...assess_segment_variation()")
        ### Precondition: self.segments must exist,
        ### generate_segments must have previously been run

        self.mad_array = np.array([segment.mad for segment in self.segments], dtype=float)
        self.mad_global = np.median(self.mad_array)
        self.mad_min = min(self.mad_array)
        self.mad_max = max(self.mad_array)
        self.mad_range = self.mad_max - self.mad_min

        self.mad_normal = np.divide(self.mad_array - self.mad_min, self.mad_range)
        return

    def define_cont_points(self):
        ### just runs define_cont_point in the Segment class, which boosts median
        ### by a scale estimate normalized to the distribution of mads from
        ### each segment

        ### Precondition: must run assess_segment_variation
        [segment.define_cont_point(self.mad_min, self.mad_range) for segment in self.segments]


    ### Accessors
    def set_segment_midpoints(self):
        self.midpoints = [segment.midpoint for segment in self.segments]
        ## add endpoints



        return np.array(self.midpoints, dtype=np.float)

    def set_segment_continuum(self):
        self.fluxpoints = [segment.continuum_point for segment in self.segments]
        ## add fluxpoints

        return np.array(self.fluxpoints, dtype=np.float)


    def add_continuum_point(self, point):
        print("...adding continuum point")
        self.midpoints.append(point[0])
        self.fluxpoints.append(point[1])

        self.fluxpoints = list(np.array(self.fluxpoints)[np.argsort(self.midpoints)])
        self.midpoints  = list(np.array(self.midpoints)[np.argsort(self.midpoints)])
        return

        return

    def remove_point(self, index):
        #self.midpoints = #self.midpoints[]
        del self.midpoints[index]
        del self.fluxpoints[index]
        return

###############################################################
    def get_continuum_points(self):
        print("continuum_points")
        for i in range(len(self.midpoints)):
            print(i, ": ", self.midpoints[i], self.fluxpoints[i])





    def set_wavelength(self, wavelength):

        self.midpoints = wavelength

        return


    def set_fluxpoints(self, flux_values):

        self.fluxpoints = flux_values

        return

#################################################




    def spline_continuum(self, k=2.0, s=1.0):
        ## Precondition:  define_cont_points has been run, segment.continuum_point exists

        ### Create the spline interpolation

        tck = interp.splrep(self.midpoints, self.fluxpoints)


        self.continuum = interp.splev(self.wavelength, tck)
        #self.continuum[self.wavelength > 5800.] = 87.


    def normalize(self):
        self.flux_norm = np.divide(self.flux, self.continuum)
        self.flux_norm[self.flux_norm < 0.0] = 1.
        self.flux_norm[self.flux_norm >2.0] = 1.


        #self.flux_norm[(self.wavelength < 3200) | (self.wavelength > 5750.)] = 1.0



    def poly_normalize(self, nlow=3.0, nhigh=3.0, boost=0.05, order=4, Regions=[]):
        return




    def spline_normalize(self, BINS=25):
        ### Trying to do this without any unneccesary parameters

        ### divide the spectrum into equal bins

        return
