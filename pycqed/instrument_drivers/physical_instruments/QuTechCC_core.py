"""
    File:       QuTechCC_core.py
    Author:     Wouter Vlothuizen, QuTech
    Purpose:    Core Instrument driver for QuTech Central Controller, independent of QCoDeS.
                All instrument protocol handling is provided here
    Usage:      Can be used directly, or with QuTechCC.py, which adds access via QCoDeS parameters
    Notes:      Here, we follow the SCPI convention of NOT checking parameter values but leaving that to
                the device
    Usage:
    Bugs:

"""

import logging
import sys

from pycqed.instrument_drivers.lib.SCPIBase import SCPIBase
from pycqed.instrument_drivers.lib.Transport import Transport

log = logging.getLogger(__name__)


class QuTechCC_core(SCPIBase):

    ##########################################################################
    # 'public' functions for the end user
    ##########################################################################

    def __init__(self,
                 name: str,
                 transport: Transport):
        super().__init__(name, transport)

    ##########################################################################
    # convenience functions
    ##########################################################################

    def assemble(self, program_string: str) -> None:
        self.sequence_program_assemble(program_string)
        if self.get_assembler_success() != 1:
            sys.stderr.write('error log = {}\n'.format(self.get_assembler_log()))  # FIXME: result is messy
            raise RuntimeError('assembly failed')

    def assemble_and_start(self, program_string: str) -> None:
        self.assemble(program_string)
        log.debug('starting CC')
        self.start()
        log.debug('checking for SCPI errors on CC')
        self.check_errors()
        log.debug('done checking for SCPI errors on CC')

    ##########################################################################
    # CC SCPI protocol wrapper functions
    ##########################################################################

    def sequence_program_assemble(self, program_string: str) -> None:
        """
        upload sequence program string
        """
        hdr = 'QUTech:SEQuence:PROGram:ASSEMble ' # NB: include space as separator for binblock parameter
        bin_block = program_string.encode('ascii')
        self.bin_block_write(bin_block, hdr)

    def get_assembler_success(self) -> int:
        return self._ask_int('QUTech:SEQuence:PROGram:ASSEMble:SUCCESS?')

    def get_assembler_log(self) -> str:
        return self._ask_bin('QUTech:SEQuence:PROGram:ASSEMble:LOG?').decode('utf-8', 'ignore')

    def set_q1_reg(self, ccio: int, reg: int, val: int) -> None:
        # only possible if CC is stopped
        self._transport.write(f'QUTech:CCIO{ccio}:Q1REG{reg} {val}')

    def get_q1_reg(self, ccio: int, reg: int) -> int:
        # only possible if CC is stopped
        return self._ask_int(f'QUTech:CCIO{ccio}:Q1REG{reg}')

    def calibrate_dio(self, ccio: int) -> None:
        self._transport.write(f'QUTech:CCIO{ccio}:DIOIN:CAL')

    def set_vsm_delay_rise(self, ccio: int, bit: int, cnt_in_833_ps_steps: int) -> None:
        self._transport.write(f'QUTech:CCIO{ccio}:VSMbit{bit}:RISEDELAY {cnt_in_833_ps_steps}')

    def get_vsm_delay_rise(self, ccio: int, bit: int) -> int:
        return self._ask_int(f'QUTech:CCIO{ccio}:VSMbit{bit}:RISEDELAY?')

    def set_vsm_delay_fall(self, ccio: int, bit: int, cnt_in_833_ps_steps: int) -> None:
        self._transport.write(f'QUTech:CCIO{ccio}:VSMbit{bit}:FALLDELAY {cnt_in_833_ps_steps}')

    def get_vsm_delay_fall(self, ccio: int, bit: int) -> int:
        return self._transport._ask_int(f'QUTech:CCIO{ccio}:VSMbit{bit}:FALLDELAY?')

    def debug_marker_off(self, ccio: int) -> None:
        self._transport.write(f'QUTech:DEBUG:CCIO{ccio}:MARKER:OFF')

    def debug_marker_in(self, ccio: int, bit: int) -> None:
        self._transport.write(f'QUTech:DEBUG:CCIO{ccio}:MARKER:IN {bit}')

    def debug_marker_out(self, ccio: int, bit: int) -> None:
        self._transport.write(f'QUTech:DEBUG:CCIO{ccio}:MARKER:OUT {bit}')

    def start(self) -> None:
        self._transport.write('awgcontrol:run:immediate')

    def stop(self) -> None:
        self._transport.write('awgcontrol:stop:immediate')

    ### status functions ###
    def get_status_questionable_frequency_condition(self) -> int:
        return self._ask_int('STATus:QUEStionable:FREQ:CONDition?')

    def get_status_questionable_frequency_event(self) -> int:
        return self._ask_int('STATus:QUEStionable:FREQ:EVENt?')

    def set_status_questionable_frequency_enable(self, val) -> None:
        self._transport.write(f'STATus:QUEStionable:FREQ:ENABle {val}')

    def get_status_questionable_frequency_enable(self) -> int:
        return self._ask_int('STATus:QUEStionable:FREQ:ENABle?')

    ##########################################################################
    # constants
    ##########################################################################

    # HDAWG DIO/marker bit definitions: CC output
    HDAWG_TOGGLE_DS = 30
    HDAWG_TRIG = 31
    HDAWG_CW = range(0,29)  # NB: bits used depend on mode

    # QWG DIO/marker bit definitions: CC output
    QWG_TOGGLE_DS = 30
    QWG_TRIG = 31
    QWG1_CW = range(0,11)
    QWG2_CW = range(16,27)

    # UHFQA DIO/marker bit definitions: CC output
    UHFQA_TOGGLE_DS = 31
    UHFQA_TRIG = 16
    UHFQA_CW = range(17,26)

    # UHFQA DIO/marker bit definitions: CC input
    UHFQA_DV = 0
    UHFQA_RSLT = range(1,10)
