import numpy as np
import unittest
import warnings
from pycqed.measurement.waveform_control_CC import waveform as wf

# These are test waveforms
g_env = np.array([0.,  0.0056186,  0.01165567,
                  0.01812183,  0.02502537,
                  0.03237195,  0.04016432,  0.04840195,
                  0.05708081,  0.06619307,
                  0.07572687,  0.08566613,  0.09599033,
                  0.10667444,  0.11768883,
                  0.12899923,  0.14056679,  0.15234816,
                  0.16429566,  0.17635752,
                  0.18847815,  0.20059853,  0.21265661,
                  0.2245878,  0.2363255,
                  0.24780173,  0.2589477,  0.26969455,
                  0.27997397,  0.28971899,
                  0.29886465,  0.30734872,  0.31511243,
                  0.32210111,  0.32826488,
                  0.33355918,  0.33794536,  0.3413911,
                  0.34387088,  0.3453662,
                  0.34586589,  0.3453662,  0.34387088,
                  0.3413911,  0.33794536,
                  0.33355918,  0.32826488,  0.32210111,
                  0.31511243,  0.30734872,
                  0.29886465,  0.28971899,  0.27997397,
                  0.26969455,  0.2589477,
                  0.24780173,  0.2363255,  0.2245878,
                  0.21265661,  0.20059853,
                  0.18847815,  0.17635752,  0.16429566,
                  0.15234816,  0.14056679,
                  0.12899923,  0.11768883,  0.10667444,
                  0.09599033,  0.08566613,
                  0.07572687,  0.06619307,  0.05708081,
                  0.04840195,  0.04016432,
                  0.03237195,  0.02502537,  0.01812183,
                  0.01165567,  0.0056186,  0.])

d_env = np.array([0.07903581,  0.08505798,
                  0.09125043,  0.09758165,  0.10401556,
                  0.1105115,  0.11702435,  0.12350468,
                  0.12989903,  0.13615021,
                  0.14219778,  0.14797855,  0.15342718,
                  0.15847683,  0.16305997,
                  0.16710918,  0.17055799,  0.17334187,
                  0.17539911,  0.17667183,
                  0.17710695,  0.17665709,  0.17528151,
                  0.17294695,  0.16962842,
                  0.16530987,  0.15998481,  0.1536567,
                  0.14633934,  0.13805702,
                  0.12884455,  0.11874711,  0.10781999,
                  0.0961281,  0.08374538,
                  0.07075403,  0.0572436,  0.04331001,
                  0.02905436,  0.01458176,
                  -0., -0.01458176, -0.02905436, -
                  0.04331001, -0.0572436,
                  -0.07075403, -0.08374538, -
                  0.0961281, -0.10781999, -0.11874711,
                  -0.12884455, -0.13805702, -
                  0.14633934, -0.1536567, -0.15998481,
                  -0.16530987, -0.16962842, -
                  0.17294695, -0.17528151, -0.17665709,
                  -0.17710695, -0.17667183, -
                  0.17539911, -0.17334187, -0.17055799,
                  -0.16710918, -0.16305997, -
                  0.15847683, -0.15342718, -0.14797855,
                  -0.14219778, -0.13615021, -
                  0.12989903, -0.12350468, -0.11702435,
                  -0.1105115, -0.10401556, -
                  0.09758165, -0.09125043, -0.08505798,
                  -0.07903581])


class Test_Waveforms(unittest.TestCase):

    def test_gauss_pulse(self):
        amplitude = .4  # something not equal to one to prevent some bugs
        motzoi = .73
        sigma = 20e-9

        I, Q = wf.gauss_pulse(amplitude, sigma, axis='x', nr_sigma=4,
                              sampling_rate=1e9,
                              motzoi=motzoi, delay=0)
        self.assertEqual(np.shape(I), np.shape(g_env))

        self.assertEqual(np.shape(Q), np.shape(d_env))

        np.testing.assert_almost_equal(I, g_env)
        np.testing.assert_almost_equal(Q, d_env)

        I, Q = wf.gauss_pulse(amplitude, sigma, axis='y', nr_sigma=4,
                              sampling_rate=1e9,
                              motzoi=motzoi, delay=0)
        np.testing.assert_almost_equal(I, -d_env)
        np.testing.assert_almost_equal(Q, g_env)

        I, Q = wf.gauss_pulse(amplitude, sigma, axis='x', phase=90,
                              nr_sigma=4,
                              sampling_rate=1e9,
                              motzoi=motzoi, delay=0)
        np.testing.assert_almost_equal(I, -d_env)
        np.testing.assert_almost_equal(Q, g_env)

    def test_mod_gauss(self):
        amplitude = .4  # something not equal to one to prevent some bugs
        motzoi = .73
        sigma = 20e-9
        I, Q = wf.mod_gauss(amplitude, sigma, axis='x', nr_sigma=4,
                            sampling_rate=1e9, f_modulation=0,
                            motzoi=motzoi, delay=0)

        np.testing.assert_almost_equal(I, g_env)
        np.testing.assert_almost_equal(Q, d_env)

    def test_mod_gauss_VSM(self):
        amplitude = .4  # something not equal to one to prevent some bugs
        motzoi = .73
        sigma = 20e-9
        G_I, G_Q, D_I, D_Q = wf.mod_gauss_VSM(
            amplitude, sigma, axis='x', nr_sigma=4,
            sampling_rate=1e9, f_modulation=0,
            motzoi=motzoi, delay=0)

        np.testing.assert_almost_equal(G_I, g_env)
        np.testing.assert_almost_equal(G_Q, np.zeros(len(g_env)))
        np.testing.assert_almost_equal(D_I, np.zeros(len(g_env)))
        np.testing.assert_almost_equal(D_Q, d_env)

    def test_martinis_flux_pulse(self):
        pass
        # This test is disabled and needs to be recreated as per issue #89
        # g2 = 1/(120e-9/(14.5/2))
        # f_bus = 4.8e9
        # f_01_max = 5.94e9
        # dac_flux_coefficient = 0.679
        # E_c = 369.2e6
        # theta_f = .4
        # length = 40e-9
        # lambda_coeffs_list = [[.1, 0], [.4, .2, .1, .01, .2]]
        # for lambda_coeffs in lambda_coeffs_list:

        #     th_pulse = wf.martinis_flux_pulse(
        #         length=length, theta_f=theta_f, lambda_coeffs=lambda_coeffs,
        #         g2=g2, E_c=E_c, f_01_max=f_01_max, f_bus=f_bus,
        #         dac_flux_coefficient=dac_flux_coefficient,
        #         return_unit='theta')
        #     V_pulse = wf.martinis_flux_pulse(
        #         length=length, theta_f=theta_f, lambda_coeffs=lambda_coeffs,
        #         g2=g2, E_c=E_c, f_01_max=f_01_max, f_bus=f_bus,
        #         dac_flux_coefficient=dac_flux_coefficient,
        #         return_unit='V')

        #     theta_0 = np.arctan(2*g2/(f_01_max-E_c-f_bus))
        #     np.testing.assert_almost_equal(theta_0, th_pulse[0])
        #     np.testing.assert_almost_equal(0, V_pulse[0])

        #     self.assertEqual(len(th_pulse), 40)
        #     np.testing.assert_almost_equal(np.max(th_pulse), theta_f)

        #     self.assertEqual(np.argmax(th_pulse), 20)
        #     self.assertEqual(np.argmax(V_pulse), 20)

    def test_martinis_flux_pulse_v2(self):
        length = 200e-9
        lambda_2 = 0.015
        lambda_3 = 0
        theta_f = 8
        f_01_max = 6.089e9
        J2 = 4.2e6
        E_c = 0
        V_per_phi0 = np.pi/1.7178
        f_interaction = 4.940e9
        f_bus = None
        asymmetry = 0
        sampling_rate = 1e9
        return_unit = 'V'

        theta_wave = wf.martinis_flux_pulse_v2(
            length=length,
            lambda_2=lambda_2,
            lambda_3=lambda_3,
            theta_f=theta_f,
            f_01_max=f_01_max,
            J2=J2,
            E_c=E_c,
            V_per_phi0=V_per_phi0,
            f_interaction=f_interaction,
            f_bus=f_bus,
            asymmetry=asymmetry,
            sampling_rate=sampling_rate,
            return_unit=return_unit)

        test_wave = np.array(
            [0.,  0.03471175,  0.06891321,  0.10213049,  0.13395662,
             0.16407213,  0.19225372,  0.21837228,  0.24238259,  0.26430828,
             0.28422502,  0.30224448,  0.31850026,  0.33313676,  0.34630067,
             0.35813509,  0.36877569,  0.37834846,  0.38696864,  0.39474049,
             0.40175751,  0.40810307,  0.41385119,  0.41906739,  0.42380953,
             0.42812868,  0.43206986,  0.43567281,  0.43897257,  0.44200007,
             0.44478268,  0.4473446,  0.44970728,  0.45188975,  0.45390895,
             0.45577993,  0.45751613,  0.45912955,  0.46063093,  0.46202989,
             0.46333506,  0.46455423,  0.46569439,  0.46676186,  0.46776234,
             0.468701,  0.46958252,  0.47041115,  0.47119076,  0.47192487,
             0.47261668,  0.47326913,  0.4738849,  0.47446644,  0.47501598,
             0.47553561,  0.47602721,  0.47649252,  0.47693314,  0.47735057,
             0.47774615,  0.47812115,  0.47847674,  0.47881399,  0.47913389,
             0.47943738,  0.4797253,  0.47999845,  0.48025757,  0.48050334,
             0.4807364,  0.48095734,  0.48116671,  0.48136502,  0.48155275,
             0.48173034,  0.48189819,  0.4820567,  0.48220622,  0.48234707,
             0.48247957,  0.48260399,  0.48272061,  0.48282967,  0.48293139,
             0.48302598,  0.48311363,  0.48319452,  0.4832688,  0.48333663,
             0.48339813,  0.48345343,  0.48350263,  0.48354583,  0.4835831,
             0.48361452,  0.48364015,  0.48366003,  0.48367421,  0.4836827,
             0.48368553,  0.4836827,  0.48367421,  0.48366003,  0.48364015,
             0.48361452,  0.4835831,  0.48354583,  0.48350263,  0.48345343,
             0.48339813,  0.48333663,  0.4832688,  0.48319452,  0.48311363,
             0.48302598,  0.48293139,  0.48282967,  0.48272061,  0.48260399,
             0.48247957,  0.48234707,  0.48220622,  0.4820567,  0.48189819,
             0.48173034,  0.48155275,  0.48136502,  0.48116671,  0.48095734,
             0.4807364,  0.48050334,  0.48025757,  0.47999845,  0.4797253,
             0.47943738,  0.47913389,  0.47881399,  0.47847674,  0.47812115,
             0.47774615,  0.47735057,  0.47693314,  0.47649252,  0.47602721,
             0.47553561,  0.47501598,  0.47446644,  0.4738849,  0.47326913,
             0.47261668,  0.47192487,  0.47119076,  0.47041115,  0.46958252,
             0.468701,  0.46776234,  0.46676186,  0.46569439,  0.46455423,
             0.46333506,  0.46202989,  0.46063093,  0.45912955,  0.45751613,
             0.45577993,  0.45390895,  0.45188975,  0.44970728,  0.4473446,
             0.44478268,  0.44200007,  0.43897257,  0.43567281,  0.43206986,
             0.42812868,  0.42380953,  0.41906739,  0.41385119,  0.40810307,
             0.40175751,  0.39474049,  0.38696864,  0.37834846,  0.36877569,
             0.35813509,  0.34630067,  0.33313676,  0.31850026,  0.30224448,
             0.28422502,  0.26430828,  0.24238259,  0.21837228,  0.19225372,
             0.16407213,  0.13395662,  0.10213049,  0.06891321,  0.03471175])

        self.assertEqual(np.shape(theta_wave), np.shape(test_wave))
        np.testing.assert_almost_equal(theta_wave, test_wave)

        lambda_2 = -0.02
        # FIXME: we should test if the right warning is raised.
        # with warnings.catch_warnings(record=True) as w:
        theta_wave = wf.martinis_flux_pulse_v2(
            length=length,
            lambda_2=lambda_2,
            lambda_3=lambda_3,
            theta_f=theta_f,
            f_01_max=f_01_max,
            J2=J2,
            E_c=E_c,
            V_per_phi0=V_per_phi0,
            f_interaction=f_interaction,
            f_bus=f_bus,
            asymmetry=asymmetry,
            sampling_rate=sampling_rate,
            return_unit=return_unit)

        test_wave_2 = np.array(
            [0.,  0.03234928,  0.06428708,  0.09542742,  0.12543163,
             0.1540241,  0.18100034,  0.20622772,  0.22964031,  0.25122954,
             0.2710329,  0.28912228,  0.30559317,  0.32055543,  0.33412579,
             0.34642229,  0.35756021,  0.3676494,  0.37679261,  0.38508466,
             0.39261214,  0.3994535,  0.40567941,  0.41135325,  0.41653169,
             0.42126526,  0.42559899,  0.42957296,  0.43322283,  0.43658032,
             0.43967369,  0.44252809,  0.44516595,  0.44760729,  0.44987001,
             0.45197009,  0.45392188,  0.45573822,  0.45743067,  0.45900961,
             0.4604844,  0.46186349,  0.46315449,  0.46436431,  0.4654992,
             0.46656483,  0.46756635,  0.46850846,  0.46939543,  0.47023115,
             0.47101919,  0.47176279,  0.47246495,  0.47312839,  0.47375563,
             0.47434897,  0.47491052,  0.47544225,  0.47594595,  0.47642329,
             0.47687579,  0.47730487,  0.47771185,  0.47809794,  0.47846427,
             0.47881187,  0.47914172,  0.47945471,  0.47975169,  0.48003341,
             0.48030062,  0.48055396,  0.48079408,  0.48102155,  0.4812369,
             0.48144065,  0.48163325,  0.48181516,  0.48198676,  0.48214843,
             0.48230053,  0.48244338,  0.48257727,  0.48270249,  0.4828193,
             0.48292792,  0.48302858,  0.48312148,  0.4832068,  0.48328471,
             0.48335536,  0.48341888,  0.4834754,  0.48352503,  0.48356785,
             0.48360394,  0.48363339,  0.48365623,  0.48367252,  0.48368228,
             0.48368553,  0.48368228,  0.48367252,  0.48365623,  0.48363339,
             0.48360394,  0.48356785,  0.48352503,  0.4834754,  0.48341888,
             0.48335536,  0.48328471,  0.4832068,  0.48312148,  0.48302858,
             0.48292792,  0.4828193,  0.48270249,  0.48257727,  0.48244338,
             0.48230053,  0.48214843,  0.48198676,  0.48181516,  0.48163325,
             0.48144065,  0.4812369,  0.48102155,  0.48079408,  0.48055396,
             0.48030062,  0.48003341,  0.47975169,  0.47945471,  0.47914172,
             0.47881187,  0.47846427,  0.47809794,  0.47771185,  0.47730487,
             0.47687579,  0.47642329,  0.47594595,  0.47544225,  0.47491052,
             0.47434897,  0.47375563,  0.47312839,  0.47246495,  0.47176279,
             0.47101919,  0.47023115,  0.46939543,  0.46850846,  0.46756635,
             0.46656483,  0.4654992,  0.46436431,  0.46315449,  0.46186349,
             0.4604844,  0.45900961,  0.45743067,  0.45573822,  0.45392188,
             0.45197009,  0.44987001,  0.44760729,  0.44516595,  0.44252809,
             0.43967369,  0.43658032,  0.43322283,  0.42957296,  0.42559899,
             0.42126526,  0.41653169,  0.41135325,  0.40567941,  0.3994535,
             0.39261214,  0.38508466,  0.37679261,  0.3676494,  0.35756021,
             0.34642229,  0.33412579,  0.32055543,  0.30559317,  0.28912228,
             0.2710329,  0.25122954,  0.22964031,  0.20622772,  0.18100034,
             0.1540241,  0.12543163,  0.09542742,  0.06428708,  0.03234928])

        self.assertEqual(np.shape(theta_wave), np.shape(test_wave_2))
        np.testing.assert_almost_equal(theta_wave, test_wave_2)
