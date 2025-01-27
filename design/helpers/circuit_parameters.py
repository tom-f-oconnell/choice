#!/usr/bin/env python

from __future__ import division
import numpy as np

###############################################################################
# Assumptions
###############################################################################
# TODO measure
# maybe w/ oscilloscope? i wasn't really getting readings fast enough w/ a DMM 
# on 20M resistance range
'''
min_fly_resistance = 1e6
# could try 1e7-1e9. previously suspected typical was ~29Mohm, which is 2.9e7
max_fly_resistance = 1e9 # 1Gohm
'''
min_fly_resistance = 5e7 / 5
max_fly_resistance = 5e7 * 5


###############################################################################
# Requirements
###############################################################################
max_operation_voltage = 120 # 100?
typ_operation_voltage = 60
# ?
min_operation_voltage = 20

# error relative to nominal value. x100 to get a percentage.
#max_fractional_voltage_change = 0.01
max_fractional_voltage_change = 0.02


###############################################################################
# Overvoltage protection
###############################################################################

# TODO still reasonable at lower operating voltages? probably?
max_safe_voltage = 200
zener_drop = 5.1 # V
# 1 W = 1 V * 1 A
zener_power_dissipation = 0.5 # W (500mW)
# it may get harder to find (small / cheap) resistors to dissipate
# more power than this
max_resistor_power = 1 # W
limit_resistor_voltage = max_safe_voltage - zener_drop

# TODO is this correct?
max_fault_current = min(zener_power_dissipation / zener_drop, \
    max_resistor_power / limit_resistor_voltage)

# V = I*R, I=V/R
min_limit_resistor = max_safe_voltage / max_fault_current

# P = I*V
limit_resistor_power = limit_resistor_voltage * max_fault_current

print 'for protection against at most {:,}V'.format(max_safe_voltage)
print 'using a Zener with Vz={} and capable of dissipating {}W of power'.format(\
    zener_drop, zener_power_dissipation)
print 'maximum overvoltage current of {}A'.format(max_fault_current)
print 'minimum limit resistance of {:,} ohms'.format(min_limit_resistor)
print 'this resistor will dissipate {}W of power\n'.format(limit_resistor_power)


###############################################################################
# Digital optoisolators
###############################################################################

# TODO revisit. see notes in sheet w/ this part.
'''
logic_level = 5 # volts

# parameters for TLP2531
max_led_current = 0.025 # 25mA
led_current_goal_over_max = 0.8

led_limit_resistor = logic_level / (0.8 * max_led_current)

# current-transfer-ratio (on [0,1])
ctr_typ = 0.3
# see https://www.vishay.com/docs/83741/83741.pdf
extra_ctr_tolerance = 0.8 * 0.75
# different from min CTR in datasheet (probably more optimistic, too)
min_expected_ctr = ctr_typ * extra_ctr_tolerance

# from SN74HC595 datasheet
# actually specified at Vcc=4.5v, so real values are probably a little higher
# for Vcc=5v (I adjusted a little)
min_logic_high_voltage = 3.5
max_logic_low_voltage = 1.5

print 'resistor to limit optoisolator LED current: {:,} ohms\n'.format(\
    led_limit_resistor)
'''

#charge_time_at_min_current = 
# digikey lists some (slightly) different parameters for what they call
# Digi-Key PN: CD4051B-DIE-ND, Mfg PN: CD4051B
# and
# Digi-Key PN: 296-2057-5-ND, Mfg PN: CD4051BE
# TODO is this an error? what does the E mean?
# the page for the latter seems to link to a TI datasheet of a part
# w/o an E in the suffix, and the former doesn't have a datasheet link
# might not matter, b/c the former has 0 currently available... ?

# TODO worth building in alternate route for a current reference to be passed
# over the sense resistor, for calibration?
# http://www.resistorguide.com/applications/shunt-resistor/
# I'm thinking no, for now...

# TODO should i add capacitors on the floor pcb to null inductance in the connector wires?
# or would that not make sense because the driver is also off of the floor pcb?

# TODO should i switch to using high side FETs
# (i think i would need to get a consistent voltage relative to variable Vhigh_voltage)
# so that i can measure with small resistors with single ended measurements?

adc_bits = 10
adc_levels = 2**adc_bits
vmin_adc = 0
vmax_adc = 5
# a.k.a. least significant bit (LSB)
v_per_level = (vmax_adc - vmin_adc) / adc_levels
# TODO also take in to account errors reported in datasheet (should be in terms of LSB)
# TODO and are those reported values w/ internal references? could be improved
# w/ external reference?

# TODO decide whether to shut off at this current, or maybe some multiple of it?

# IRL620 properties
# at Vgs=5V

# may depend somewhat on Ids, and thus not really be tested at
# low currents it will see here?
fet_rds_on = 1

fet_gate_source_leakage = 1e-7  # +/- 100 nA
# TODO do i need to worry about MOSFET zero gate voltage drain current?
# FETs do not behave much like resistors when off, so there is no Rds(off)
# NOTE this value is measured at Vds=200V, though not a linear relationship
fet_zero_gate_voltage_drain_current = 2.5e-5 # 25 uA
# end IRL620 properties

# resistance of resistor used to convert the current through the fly to
# a voltage to be measured
# should be small enough to not drop a significant fraction of the voltage
# the fly would be receiving, and large enough to get enough of a voltage
# to measure
# TODO set this to have max expected resistance lead to max of range of ADC (5v)
# (or at least <= 5, assuming we don't want to need an amplifier w/ gain < 1)

# TODO TODO or should i just set this to have an acceptable maximum change in voltage,
# and then set the amplifier gain appropriately to expand the shunt voltage into
# the full scale range of the ADC?
# TODO i guess one reason to go with the former approach is that i may have overestimated
# the minimum resistance of the flies, but not the maximum, and i stand a chance
# of detecting them (IF i have more ADC bits than i need...) 

# solving:
# (1 - (min_fly_resistance / (min_fly_resistance + fet_rds_on + shunt_resistance + \
#    min_limit_resistor)) = max_fractional_voltage_change
# for shunt_resistance

# TODO way to round to nearest available / common (precision?) resistor value?
# (in python?)
shunt_resistance = (min_fly_resistance / (1 - max_fractional_voltage_change)) - \
    min_fly_resistance - fet_rds_on - min_limit_resistor
#shunt_resistance = 1.5e5  # (150K ohms)

assert shunt_resistance > 0, \
    'other resistances too large to meet max voltage drop requirement'

# expressed as (max deviation within tolerance - nominal value) / (nominal value)
shunt_resistor_precision = 0.01 # 1%


# TODO should i use the min resistance to calculate appropriate current limit?
# or maybe use a current source and measure a current that is just barely not 
# lethal to most flies?

# TODO check assumption that resistances connected to shunt through to ADC
# are negligible b/c high amp input resitance
other_series_resistance = shunt_resistance + fet_rds_on + min_limit_resistor
max_series_resistance = max_fly_resistance + other_series_resistance

min_current = min_operation_voltage / max_series_resistance
min_shunt_voltage = min_current * shunt_resistance

# still using max series resistance, but with likely operating voltage
typ_current = typ_operation_voltage / max_series_resistance
typ_shunt_voltage = typ_current * shunt_resistance

print 'for a shunt (sense) resistance of {:,} ohms...'.format(shunt_resistance)

print '\nassuming min fly resistance of {:,} ohms'.format(min_fly_resistance)
print ('and with other series resistances totalling {:,} ' + \
    'ohms').format(other_series_resistance)
print 'worst case change in fly voltage drop due to other resistances: ' + \
    '{} %'.format(100 * (1 - min_fly_resistance / \
    (min_fly_resistance + other_series_resistance)))


print '\nsmallest voltages generated that should be detectable:'
print 'assuming max fly resistance of {:,} ohms'.format(max_fly_resistance)
print '  @ {}V'.format(min_operation_voltage)
print '  {:,}'.format(min_shunt_voltage)
print '  @ {}V'.format(typ_operation_voltage)
print '  {:,}'.format(typ_shunt_voltage)


max_current = max_operation_voltage / \
    (min_fly_resistance + other_series_resistance)
max_shunt_voltage = max_current * shunt_resistance

print '\nlargest voltages generated that should be detectable:'
print 'assuming min fly resistance of {:,} ohms'.format(min_fly_resistance)
print '  @ {}V'.format(max_operation_voltage)
print '  {:,}'.format(max_shunt_voltage)


# shouldn't be relevant if zener overvoltage protection is working correctly
'''
# assumes that the shunt, FET (D->S), and fly are only important resistances
# because that's what's in other_series_resistance
shunt_fraction_in_short = shunt_resistance / other_series_resistance
fet_fraction_in_short = fet_rds_on / other_series_resistance
# TODO power dissipated as well? check that shunt isn't going to fail?
print '\nvoltages across other resistances if electrodes are shorted:'
print '  @ {}V'.format(typ_operation_voltage)
print '    across shunt {:,}'.format(shunt_fraction_in_short * \
    typ_operation_voltage)
print '    across FET Rds(on) {:,}'.format(fet_fraction_in_short * \
    typ_operation_voltage)

print '  @ {}V'.format(max_operation_voltage)
print '    across shunt {:,}'.format(shunt_fraction_in_short * \
    max_operation_voltage)
print '    across FET Rds(on) {:,}'.format(fet_fraction_in_short * \
    max_operation_voltage)
'''


def voltage_dynamic_range(max_detectable, min_detectable):
    dr = max_detectable / min_detectable
    # for "field quantities" like voltage, the prefactor of 20 is normal,
    # rather than the 10 used for "power quantities"
    dr_db = 20 * np.log10(dr)
    return dr, dr_db

required_dynamic_range, required_dynamic_range_db = \
    voltage_dynamic_range(max_shunt_voltage, min_shunt_voltage)

print '\n***Required ADC***'
print 'from range of operation voltages and expected range of fly resistances...'
print 'required dynamic range: {:,} ({}dB)'.format(required_dynamic_range, \
    required_dynamic_range_db)
# TODO which is likely easier to implement: invertible compression or external ADC?
min_bits = int(np.ceil(np.log2(required_dynamic_range)))
print 'minimum bits of ADC to cover this range w/o compression {}'.format( \
    min_bits)
print 5.0 / 2**min_bits, min_shunt_voltage
shunt_voltage_range = max_shunt_voltage - min_shunt_voltage
# TODO calculate w/ actual (likely 5v) Vdd, not just desired range
lsb_of_required_adc = shunt_voltage_range / 2**min_bits
print max_shunt_voltage, shunt_voltage_range, lsb_of_required_adc

# we calculated something wrong if the minimum shunt voltage is not at least
# one LSB of the minimum resolution ADC that should work
assert lsb_of_required_adc <= min_shunt_voltage


print '\n***Arduino ADC***'
# TODO should i make the min voltage at least a few ADC levels?
# (i.e. what will be precision of upstream circuitry + ADC?)
# set in a principled way?
# TODO TODO
#num_levels_for_min = 10
#min_voltage_to_detect = num_levels_for_min * v_per_level
print 'minimum detectable voltage difference @ ADC: {}'.format(v_per_level)

# because v_per_level is minimum nonzero voltage
# (0 would be interpreted as no fly / no shock)
adc_dr, adc_dr_db = voltage_dynamic_range(vmax_adc, v_per_level)
print '\nassuming the lowest nonzero level (LSB) is above the noise floor'
print 'the Arduino\'s ADC dynamic range would be: {:,} ({}dB)'.format(adc_dr, \
    adc_dr_db)

# TODO maybe easiest way around this is just using an external ADC with
# a higher resolution?

# the goal of a minimum voltage when a fly is receiving a shock
# plus the maximum resistance we expect a fly to have
# will determine the minimum value of a shunt resistor
# TODO BUT ONLY IF SENSING DIRECTLY W/ ADC... and we probably won't...
# or with a gain of 1 in amplification leading up to ADC... which might be the case...
# TODO how to determine if it would make sense to use a gain other than 1?

# TODO as a function of?
# TODO include diode # / meaningful name once that subcircuit is finalized
# TODO matched diodes in same package for symmetric leakage about shunt resistor?
diode_leak_current = 0.001


# TODO TODO compute expected ADC / amp input voltage contributions from various
# switch deviations from the ideal (e.g. voltage created over load via leak current)
# maybe for both cd4051b and max338 / similar

# TODO since the source presumably has a very high resistance, the leakage current
# is probably a bigger deal than Rds(on). compare to max338 / alternatives


# CD4052B properties
# taken from http://www.ti.com/lit/ds/symlink/cd4051b.pdf
# see copy in design/pcb/datasheets
# all properties taken from measurements w/ Vdd = 5v, where Vdd dependent
# and 25C where temperature dependent
# TODO test whether switch gets hot (close enough to 85C) to matter
# during normal operation

# (though it can be between -0.5 and 20V)
switch_Vdd = 5
switch_I_single_channel_max = 0.010
switch_I_single_channel_min = -0.010

# NOTE both of these could be improved if operating with a higher Vdd
# which may be an option if i am going to have an opamp between this switch
# and the ADC anyway...
switch_Rds_on_max = 1050
switch_Rds_on_typ = 470
max_diff_Ron_channel_i_j = 15

# TODO what do they mean in the datasheet with
# "Any Channel OFF (Max) or ALL Channels OFF (Common OUT/IN) (Max)"?
# why are these necessarily the same? if they aren't the same, how was it measured?

# TODO why was this only measured with Vdd = 18V? curve below?
# if this max value isn't acceptable, may want to pick a different device
# b/c they say that test equipment can not necessarily do better than +/-100nA
# https://e2e.ti.com/support/switches_multiplexers/f/388/t/569731
# TODO may need to consider +/- effects on errors
switch_off_leak_max = 100 * 1e-9 # +/-
switch_off_leak_typ = 0.01 * 1e-9 # +/-

# NOTE only determined at Vdd=18V, T=85C
switch_on_leak_max = 300 * 1e-9 # +/i

switch_C_in = 5 * 1e-12
# NOTE CD405[2/3] have lower C_out
switch_C_out = 30 * 1e-12
# TODO ?
switch_C_feedthrough = 0.2 * 1e-12

# end CD4051B properties


# TODO make sure analog switch / any voltage follower / anything preceding ADC
# can all operate in the low

# both Arduino MEGA2560 (ATmega1280) and Arduino Uno (ATmega328/P) have their
# clock speed set to 16MHz by an onboard crystal oscillator
# NOTE that the Arduino Due has a higher clock speed
uc_clock_rate = 1.6e7
# recommended ADC prescaler. used by analogRead.
# TODO also the one used on mega?
# TODO check / get from datasheet
adc_clock_prescaler = 128
# TODO that is not for mega though!
# should be 125kHz ADC clock frequency w/ prescaler of 128
adc_clock_rate = uc_clock_rate / adc_clock_prescaler

# though it is ~24 on first conversion, for unclear reasons
adc_samples_per_conversion = 12

sample_and_hold_capacitance = 2.5e-9
sample_time_at_adc_clock_rate = (1.0 / adc_clock_rate) * adc_samples_per_conversion

# TODO take in to account minimum timescale on which you want to detect an event?
# if i only want to know by the end of the 0.1 - 1 second pulse, then maybe it doesnt matter?

# TODO but it might still matter because of analog switching...
# (possible cross talk if switching too fast)
# but i could also maybe just set the analog switching rate to be sufficiently low?


# calculations re: effect of FET resistance on shunt current measurement accuracy?
# irl620 has pretty low Rdson (~1 ohm @ RT). acceptable?
# -> could do single ended measurements then?

# TODO power dissipation w/ R in line w/ OVP diode?
