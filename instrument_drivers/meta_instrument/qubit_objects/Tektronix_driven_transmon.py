import logging
import numpy as np
from scipy.optimize import brent
from math import gcd
from qcodes.utils import validators as vals
from qcodes.instrument.parameter import ManualParameter

from modules.measurement import detector_functions as det
from modules.measurement import composite_detector_functions as cdet
from modules.measurement import mc_parameter_wrapper as pw

from modules.measurement import sweep_functions as swf
from modules.measurement import CBox_sweep_functions as cb_swf
from modules.measurement import awg_sweep_functions as awg_swf
from modules.analysis import measurement_analysis as ma
from modules.measurement.pulse_sequences import standard_sequences as st_seqs
import modules.measurement.randomized_benchmarking.randomized_benchmarking as rb
from modules.measurement.calibration_toolbox import mixer_carrier_cancellation_5014
from modules.measurement.optimization import nelder_mead

from .qubit_object import Transmon
from .CBox_driven_transmon import CBox_driven_transmon
# It would be better to inherit from Transmon directly and put all the common
# stuff in there but for now I am inheriting from what I already have
# MAR april 2016


class Tektronix_driven_transmon(CBox_driven_transmon):
    '''
    Setup configuration:
        Drive:                 Tektronix 5014 AWG
        Acquisition:           CBox
                    (in the future to be compatible with both CBox and ATS)
        Readout pulse configuration: LO modulated using AWG
    '''
    def __init__(self, name,
                 LO, cw_source, td_source,
                 IVVI, AWG, CBox,
                 heterodyne_instr,
                 MC):
        super(CBox_driven_transmon, self).__init__(name) # Change this when inheriting directly from Transmon instead of from CBox driven Transmon.
        self.LO = LO
        self.cw_source = cw_source
        self.td_source = td_source
        self.IVVI = IVVI
        self.heterodyne_instr = heterodyne_instr
        self.AWG = AWG
        self.CBox = CBox
        self.MC = MC

        self.add_parameter('mod_amp_cw', label='RO modulation ampl cw',
                           units='V', initial_value=0.5,
                           parameter_class=ManualParameter)
        self.add_parameter('spec_pow', label='spectroscopy power',
                           units='dBm',
                           parameter_class=ManualParameter)
        self.add_parameter('spec_pow_pulsed',
                           label='pulsed spectroscopy power',
                           units='dBm',
                           parameter_class=ManualParameter)
        self.add_parameter('td_source_pow',
                           label='Time-domain power',
                           units='dBm',
                           parameter_class=ManualParameter)
        # Rename f_RO_mod
        # Time-domain parameters
        self.add_parameter('pulse_I_channel', initial_value='ch1',
                           vals=vals.Strings(),
                           parameter_class=ManualParameter)
        self.add_parameter('pulse_Q_channel', initial_value='ch2',
                           vals=vals.Strings(),
                           parameter_class=ManualParameter)
        self.add_parameter('pulse_I_offset', initial_value=0.0,
                           vals=vals.Numbers(min_value=-0.1, max_value=0.1),
                           parameter_class=ManualParameter)
        self.add_parameter('pulse_Q_offset', initial_value=0.0,
                           vals=vals.Numbers(min_value=-0.1, max_value=0.1),
                           parameter_class=ManualParameter)

        self.add_parameter('RO_I_channel', initial_value='ch3',
                           vals=vals.Strings(),
                           parameter_class=ManualParameter)
        self.add_parameter('RO_Q_channel', initial_value='ch4',
                           vals=vals.Strings(),
                           parameter_class=ManualParameter)
        self.add_parameter('RO_I_offset', initial_value=0.0,
                           vals=vals.Numbers(min_value=-0.1, max_value=0.1),
                           parameter_class=ManualParameter)
        self.add_parameter('RO_Q_offset', initial_value=0.0,
                           vals=vals.Numbers(min_value=-0.1, max_value=0.1),
                           parameter_class=ManualParameter)

        self.add_parameter('f_pulse_mod',
                           initial_value=-100e6,
                           label='pulse-modulation frequency', units='Hz',
                           parameter_class=ManualParameter)
        self.add_parameter('f_RO_mod',
                           label='Readout-modulation frequency', units='Hz',
                           initial_value=-2e7,
                           parameter_class=ManualParameter)
        self.add_parameter('amp180',
                           label='Pi-pulse amplitude', units='V',
                           initial_value=.25,
                           vals=vals.Numbers(min_value=-0.5, max_value=0.5),
                           parameter_class=ManualParameter)
        self.add_parameter('gauss_sigma', units='s',
                           initial_value=10e-9,
                           parameter_class=ManualParameter)
        self.add_parameter('motzoi', label='Motzoi parameter', units='',
                           initial_value=0,
                           parameter_class=ManualParameter)

        # Single shot readout specific parameters
        self.add_parameter('RO_threshold', units='dac-value',
                           initial_value=0,
                           parameter_class=ManualParameter)
        # CBox specific parameter
        self.add_parameter('signal_line', parameter_class=ManualParameter,
                           vals=vals.Enum(0, 1), initial_value=0)

        # Specifying the int_avg det here should allow replacing it with ATS
        # or potential digitizer acquisition easily
        self.int_avg_det = det.CBox_integrated_average_detector(self.CBox,
                                                                self.AWG)

    def prepare_for_timedomain(self):
        self.LO.on()
        self.cw_source.off()
        self.td_source.on()
        # Set source to fs =f-f_mod such that pulses appear at f = fs+f_mod
        self.td_source.frequency.set(self.f_qubit.get()
                                     - self.f_pulse_mod.get())
        # Use resonator freq unless explicitly specified
        if self.f_RO.get() is None:
            f_RO = self.f_res.get()
        else:
            f_RO = self.f_RO.get()
        self.LO.frequency.set(f_RO - self.f_RO_mod.get())
        self.td_source.power.set(self.td_source_pow.get())
        self.get_pulse_pars()

        self.AWG.set(self.pulse_I_channel.get()+'_offset',
                     self.pulse_I_offset.get())
        self.AWG.set(self.pulse_Q_channel.get()+'_offset',
                     self.pulse_Q_offset.get())
        self.AWG.set(self.RO_I_channel.get()+'_offset', self.RO_I_offset.get())
        self.AWG.set(self.RO_Q_channel.get()+'_offset', self.RO_Q_offset.get())

    def get_pulse_pars(self):
        self.pulse_pars = {
            'I_channel': self.pulse_I_channel.get(),
            'Q_channel': self.pulse_Q_channel.get(),
            'amplitude': self.amp180.get(),
            'sigma': self.gauss_sigma.get(),
            'nr_sigma': 4,
            'motzoi': self.motzoi.get(),
            'mod_frequency': self.f_pulse_mod.get(),
            'pulse_separation': self.pulse_separation.get(),
            'phase': 0,
            'pulse_type': 'SSB_DRAG_pulse'}

        self.RO_pars = {
            'I_channel': self.RO_I_channel.get(),
            'Q_channel': self.RO_Q_channel.get(),
            'amplitude': self.RO_amp.get(),
            'length': self.RO_pulse_length.get(),
            'trigger_delay': self.RO_trigger_delay.get(),
            'pulse_delay': self.RO_pulse_delay.get(),
            'mod_frequency': self.f_RO_mod.get(),
            'fixed_point_frequency': gcd(int(self.f_RO_mod.get()), int(20e6)),
            'marker_ch1': self.RO_Q_channel.get()+'_marker1',
            'marker_ch2': self.RO_Q_channel.get()+'_marker2',
            'phase': 0,
            'pulse_type': 'MW_IQmod_pulse'}
        return self.pulse_pars, self.RO_pars

    def calibrate_mixer_offsets(self, signal_hound, offs_type='pulse',
                                update=True):
        '''
        input:
            signal_hound: instance of the SH instrument
            offs_type:         ['pulse' | 'RO'] whether to calibrate the
                                            RO or pulse IQ offsets
            update:        update the values in the qubit object

        Calibrates the mixer skewness and updates the I and Q offsets in
        the qubit object.
        signal hound needs to be given as it this is not part of the qubit
        object in order to reduce dependencies.
        '''
        # ensures freq is set correctly
        # Still need to test this, start by doing this in notebook
        self.prepare_for_timedomain()
        self.AWG.stop()  # Make sure no waveforms are played
        if offs_type == 'pulse':
            AWG_channel1 = self.pulse_I_channel.get()
            AWG_channel2 = self.pulse_Q_channel.get()
            source = self.td_source
        elif offs_type == 'RO':
            AWG_channel1 = self.RO_I_channel.get()
            AWG_channel2 = self.RO_Q_channel.get()
            source = self.LO
        else:
            raise ValueError('offs_type "{}" not recognized'.format(offs_type))

        offset_I, offset_Q = mixer_carrier_cancellation_5014(
            AWG=self.AWG, SH=signal_hound, source=source, MC=self.MC,
            AWG_channel1=AWG_channel1, AWG_channel2=AWG_channel2)

        if update:
            if offs_type == 'pulse':
                self.pulse_I_offset.set(offset_I)
                self.pulse_Q_offset.set(offset_Q)
            if offs_type == 'RO':
                self.RO_I_offset.set(offset_I)
                self.RO_Q_offset.set(offset_Q)



    def calibrate_mixer_skewness(self, signal_hound, update=True):
        raise NotImplementedError('parent class uses CBox')

    def calibrate_RO_threshold(self, method='conventional',
                               MC=None, close_fig=True,
                               verbose=False, make_fig=True):
        raise NotImplementedError()

    def measure_rabi(self, amps, n=1,
                     MC=None, analyze=True, close_fig=True,
                     verbose=False):
        self.prepare_for_timedomain()
        if MC is None:
            MC = self.MC

        MC.set_sweep_function(awg_swf.Rabi(
            pulse_pars=self.pulse_pars, RO_pars=self.RO_pars, n=n))
        MC.set_sweep_points(amps)
        MC.set_detector_function(self.int_avg_det)
        MC.run('Rabi-n{}'.format(n)+self.msmt_suffix)
        if analyze:
            ma.Rabi_Analysis(auto=True, close_fig=close_fig)

    def measure_T1(self, times, MC=None,
                   analyze=True, close_fig=True):
        self.prepare_for_timedomain()
        if MC is None:
            MC = self.MC

        MC.set_sweep_function(awg_swf.T1(
            pulse_pars=self.pulse_pars, RO_pars=self.RO_pars))
        MC.set_sweep_points(times)
        MC.set_detector_function(self.int_avg_det)
        MC.run('T1'+self.msmt_suffix)
        if analyze:
            a = ma.T1_Analysis(auto=True, close_fig=True)
            return a.T1

    def measure_ramsey(self, times, artificial_detuning=None,
                       f_qubit=None,
                       label='',
                       MC=None, analyze=True, close_fig=True, verbose=True):
        self.prepare_for_timedomain()
        if MC is None:
            MC = self.MC

        if f_qubit is None:
            f_qubit = self.f_qubit.get()

        Rams_swf = awg_swf.Ramsey(
            pulse_pars=self.pulse_pars, RO_pars=self.RO_pars,
            artificial_detuning=artificial_detuning)
        MC.set_sweep_function(Rams_swf)
        MC.set_sweep_points(times)
        MC.set_detector_function(self.int_avg_det)
        MC.run('Ramsey'+label+self.msmt_suffix)

        if analyze:
            a = ma.Ramsey_Analysis(auto=True, close_fig=True)
            if verbose:
                fitted_freq = a.fit_res.params['frequency'].value
                print('Artificial detuning: {:.2e}'.format(
                      artificial_detuning))
                print('Fitted detuning: {:.2e}'.format(fitted_freq))
                print('Actual detuning:{:.2e}'.format(
                      fitted_freq-artificial_detuning))

    def measure_allxy(self, double_points=True,
                      MC=None,
                      analyze=True, close_fig=True, verbose=True):
        self.prepare_for_timedomain()
        if MC is None:
            MC = self.MC

        MC.set_sweep_function(awg_swf.AllXY(
            pulse_pars=self.pulse_pars, RO_pars=self.RO_pars,
            double_points=double_points))
        MC.set_detector_function(self.int_avg_det)
        MC.run('AllXY'+self.msmt_suffix)

        if analyze:
            a = ma.AllXY_Analysis(close_main_fig=close_fig)
            return a

    def measure_randomized_benchmarking(self, nr_cliffords,
                                        nr_seeds=20, T1=None,
                                        MC=None, analyze=True, close_fig=True,
                                        verbose=False):
        '''
        Performs a randomized benchmarking fidelity.
        Optionally specifying T1 also shows the T1 limited fidelity.
        '''
        self.prepare_for_timedomain()
        if MC is None:
            MC = self.MC
        MC.set_sweep_function(awg_swf.Randomized_Benchmarking(
            pulse_pars=self.pulse_pars, RO_pars=self.RO_pars,
            nr_cliffords=nr_cliffords, nr_seeds=nr_seeds))
        MC.set_detector_function(self.int_avg_det)
        MC.run('RB_{}seeds'.format(nr_seeds)+self.msmt_suffix)
        ma.RandomizedBenchmarking_Analysis(
            close_main_fig=close_fig, T1=T1,
            pulse_separation=self.pulse_separation.get())

    def measure_discrimination_fid(self, no_fits=False,
                                   return_detector=False,
                                   MC=None,
                                   analyze=True,
                                   close_fig=True, make_fig=True,
                                   verbose=True):
        raise NotImplementedError()

    def measure_rb_vs_amp(self, amps, nr_cliff=1,
                      resetless=True,
                      MC=None, analyze=True, close_fig=True,
                      verbose=False):
        raise NotImplementedError()

    def measure_Echo(self, times, MC=None,
                     analyze=True, close_fig=True, verbose=True):
        raise NotImplementedError()