EESchema Schematic File Version 3
LIBS:choice_shield
LIBS:power
LIBS:device
LIBS:linear
LIBS:regul
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:Connector
LIBS:Valve
LIBS:Diode
LIBS:Display
LIBS:Transistor
LIBS:Logic_CMOS_4000
LIBS:Logic_74xx
LIBS:shield_pcb-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L R R?
U 1 1 5A020264
P 2550 2850
AR Path="/5A04F7C4/5A020264" Ref="R?"  Part="1" 
AR Path="/5A04FF59/5A020264" Ref="R?"  Part="1" 
F 0 "R?" V 2350 2750 50  0000 L CNN
F 1 "150" V 2450 2750 50  0000 L CNN
F 2 "" V 2480 2850 50  0001 C CNN
F 3 "" H 2550 2850 50  0001 C CNN
	1    2550 2850
	0    1    1    0   
$EndComp
$Comp
L R R?
U 1 1 5A0202C8
P 3050 3200
AR Path="/5A04F7C4/5A0202C8" Ref="R?"  Part="1" 
AR Path="/5A04FF59/5A0202C8" Ref="R?"  Part="1" 
F 0 "R?" H 3120 3246 50  0000 L CNN
F 1 "100K" H 3120 3155 50  0000 L CNN
F 2 "" V 2980 3200 50  0001 C CNN
F 3 "" H 3050 3200 50  0001 C CNN
	1    3050 3200
	1    0    0    -1  
$EndComp
$Comp
L R R?
U 1 1 5A020329
P 3650 1950
AR Path="/5A04F7C4/5A020329" Ref="R?"  Part="1" 
AR Path="/5A04FF59/5A020329" Ref="R?"  Part="1" 
F 0 "R?" H 3720 1996 50  0000 L CNN
F 1 "150K" H 3720 1905 50  0000 L CNN
F 2 "" V 3580 1950 50  0001 C CNN
F 3 "" H 3650 1950 50  0001 C CNN
	1    3650 1950
	1    0    0    -1  
$EndComp
$Comp
L R R?
U 1 1 5A020365
P 4150 1600
AR Path="/5A04F7C4/5A020365" Ref="R?"  Part="1" 
AR Path="/5A04FF59/5A020365" Ref="R?"  Part="1" 
F 0 "R?" V 3950 1500 50  0000 L CNN
F 1 "160K,0.25W" V 4050 1500 50  0000 L CNN
F 2 "" V 4080 1600 50  0001 C CNN
F 3 "" H 4150 1600 50  0001 C CNN
	1    4150 1600
	0    1    1    0   
$EndComp
$Comp
L R R?
U 1 1 5A0203AA
P 4150 2250
AR Path="/5A04F7C4/5A0203AA" Ref="R?"  Part="1" 
AR Path="/5A04FF59/5A0203AA" Ref="R?"  Part="1" 
F 0 "R?" V 3950 2150 50  0000 L CNN
F 1 "160K,0.25W" V 4050 2150 50  0000 L CNN
F 2 "" V 4080 2250 50  0001 C CNN
F 3 "" H 4150 2250 50  0001 C CNN
	1    4150 2250
	0    1    1    0   
$EndComp
$Comp
L D D?
U 1 1 5A020460
P 4650 1450
AR Path="/5A04F7C4/5A020460" Ref="D?"  Part="1" 
AR Path="/5A04FF59/5A020460" Ref="D?"  Part="1" 
F 0 "D?" V 4600 1600 50  0000 C CNN
F 1 "D" V 4700 1550 50  0000 C CNN
F 2 "" H 4650 1450 50  0001 C CNN
F 3 "" H 4650 1450 50  0001 C CNN
	1    4650 1450
	0    1    1    0   
$EndComp
$Comp
L D D?
U 1 1 5A020509
P 4650 2100
AR Path="/5A04F7C4/5A020509" Ref="D?"  Part="1" 
AR Path="/5A04FF59/5A020509" Ref="D?"  Part="1" 
F 0 "D?" V 4600 2250 50  0000 C CNN
F 1 "D" V 4700 2200 50  0000 C CNN
F 2 "" H 4650 2100 50  0001 C CNN
F 3 "" H 4650 2100 50  0001 C CNN
	1    4650 2100
	0    1    1    0   
$EndComp
$Comp
L IRL620 Q?
U 1 1 5A04EA8A
P 3550 2850
AR Path="/5A04F7C4/5A04EA8A" Ref="Q?"  Part="1" 
AR Path="/5A04FF59/5A04EA8A" Ref="Q?"  Part="1" 
F 0 "Q?" H 3756 2896 50  0000 L CNN
F 1 "IRL620" H 3756 2805 50  0000 L CNN
F 2 "TO_SOT_Packages_THT:TO-220-3_Vertical" H 3750 2775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/BS/BSS138.pdf" H 3550 2850 50  0001 L CNN
	1    3550 2850
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 5A04F122
P 3350 3650
AR Path="/5A04F7C4/5A04F122" Ref="#PWR?"  Part="1" 
AR Path="/5A04FF59/5A04F122" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 3350 3400 50  0001 C CNN
F 1 "GND" H 3355 3477 50  0000 C CNN
F 2 "" H 3350 3650 50  0001 C CNN
F 3 "" H 3350 3650 50  0001 C CNN
	1    3350 3650
	1    0    0    -1  
$EndComp
$Comp
L VCC #PWR?
U 1 1 5A04FCD5
P 4650 1900
AR Path="/5A04F7C4/5A04FCD5" Ref="#PWR?"  Part="1" 
AR Path="/5A04FF59/5A04FCD5" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 4650 1750 50  0001 C CNN
F 1 "VCC" H 4667 2073 50  0000 C CNN
F 2 "" H 4650 1900 50  0001 C CNN
F 3 "" H 4650 1900 50  0001 C CNN
	1    4650 1900
	1    0    0    -1  
$EndComp
$Comp
L VCC #PWR?
U 1 1 5A04FD15
P 4650 1250
AR Path="/5A04F7C4/5A04FD15" Ref="#PWR?"  Part="1" 
AR Path="/5A04FF59/5A04FD15" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 4650 1100 50  0001 C CNN
F 1 "VCC" H 4667 1423 50  0000 C CNN
F 2 "" H 4650 1250 50  0001 C CNN
F 3 "" H 4650 1250 50  0001 C CNN
	1    4650 1250
	1    0    0    -1  
$EndComp
Wire Wire Line
	2700 2850 3350 2850
Wire Wire Line
	3050 3050 3050 2850
Connection ~ 3050 2850
Wire Wire Line
	3050 3350 3050 3550
Wire Wire Line
	3050 3550 3650 3550
Wire Wire Line
	3650 3550 3650 3050
Wire Wire Line
	3350 3650 3350 3550
Connection ~ 3350 3550
Wire Wire Line
	4300 2250 4950 2250
Wire Wire Line
	4000 1600 3650 1600
Wire Wire Line
	3650 1350 3650 1800
Wire Wire Line
	4300 1600 4950 1600
Wire Wire Line
	4650 1300 4650 1250
Wire Wire Line
	4650 1950 4650 1900
Wire Wire Line
	3650 2100 3650 2650
Text HLabel 1900 2850 0    60   Input ~ 0
logic_input
Wire Wire Line
	1900 2850 2400 2850
Text HLabel 3650 1350 1    60   Input ~ 0
after_fly
Connection ~ 3650 1600
Text HLabel 4950 1600 2    60   Input ~ 0
ADC+
Text HLabel 4950 2250 2    60   Input ~ 0
ADC-
Connection ~ 4650 1600
Connection ~ 4650 2250
Wire Wire Line
	4000 2250 3650 2250
Connection ~ 3650 2250
$EndSCHEMATC
