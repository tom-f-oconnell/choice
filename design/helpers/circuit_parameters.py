#!/usr/bin/env python

from __future__ import division
import numpy as np

# digikey lists some (slightly) different parameters for what they call
# Digi-Key PN: CD4051B-DIE-ND, Mfg PN: CD4051B
# and
# Digi-Key PN: 296-2057-5-ND, Mfg PN: CD4051BE
# TODO is this an error? what does the E mean?
# the page for the latter seems to link to a TI datasheet of a part
# w/o an E in the suffix, and the former doesn't have a datasheet link
# might not matter, b/c the former has 0 currently available... ?


# TODO should i add capacitors on the floor pcb to null inductance in the connector wires?
# or would that not make sense because the driver is also off of the floor pcb?

# TODO should i switch to using high side FETs
# (i think i would need to get a consistent voltage relative to variable Vhigh_voltage)
# so that i can measure with small resistors with single ended measurements?

adc_bits = 10
adc_levels = 2**adc_bits
vmin_adc = 0
vmax_adc = 5
v_per_level = (vmax_adc - vmin_adc) / adc_levels

# TODO do i need to worry about MOSFET Rds(off) (i guess it might be ~= Rfly?)?

# TODO measure
min_fly_resistance = 1e6
max_fly_resistance = 1e10
#charge_time_at_min_current = 

# TODO should i use the min resistance to calculate appropriate current limit?
# or maybe use a current source and measure a current that is just barely not 
# lethal to most flies?
max_operation_voltage = 120 # 100?
typical_operation_voltage = 60
# ?
min_operation_voltage = 20


# TODO decide whether to shut off at this current, or maybe some multiple of it?

# assuming shunt + FET Rds(on) + other resistances are negligible
# may need to update calculation if they are not
abs_max_fly_current = max_operation_voltage / min_fly_resistance

# TODO should i make the min voltage at least a few ADC levels?
# (i.e. what will be precision of upstream circuitry + ADC?)
# set in a principled way?
num_levels_for_min = 10
min_voltage_to_detect = num_levels_for_min * v_per_level

# the goal of a minimum voltage when a fly is receiving a shock
# plus the maximum resistance we expect a fly to have
# will determine the minimum value of a shunt resistor
# TODO BUT ONLY IF SENSING DIRECTLY W/ ADC... and we probably won't...
# or with a gain of 1 in amplification leading up to ADC... which might be the case...
# TODO how to determine if it would make sense to use a gain other than 1?

# TODO as a function of?
# TODO include diode # / meaningful name once that subcircuit is finalized
diode_leak_current = 0.001


# TODO TODO compute expected ADC / amp input voltage contributions from various
# switch deviations from the ideal (e.g. voltage created over load via leak current)
# maybe for both cd4051b and max338 / similar

# TODO since the source presumably has a very high resistance, the leakage current
# is probably a bigger deal than Rds(on). compare to max338 / alternatives


# CD4051B properties
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

# TODO check / get from datasheet
uc_clock_rate = 1e10
adc_clock_prescaler = 128
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
