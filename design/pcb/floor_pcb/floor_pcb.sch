EESchema Schematic File Version 3
LIBS:shock_electrodes
LIBS:floor_pcb
LIBS:Connector
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "8 chamber shock conditioning floor grid"
Date "2017-12-06"
Rev "0.1"
Comp "Hong lab @ Caltech"
Comment1 "github.com/tom-f-oconnell/choice"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Conn_01x10_Male J2
U 1 1 59F76DF3
P 1350 2100
F 0 "J2" H 1456 2678 50  0000 C CNN
F 1 "Conn_01x10_Male" H 1456 2587 50  0000 C CNN
F 2 "footprints:SIP-10_2.54mm_1mm_clearance" H 1350 2100 50  0001 C CNN
F 3 "" H 1350 2100 50  0001 C CNN
	1    1350 2100
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J11
U 1 1 59F778B5
P 4250 1800
F 0 "J11" H 5278 2078 60  0000 L CNN
F 1 "shock_grid" H 5278 1972 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 4250 1800 60  0001 C CNN
F 3 "" H 4250 1800 60  0001 C CNN
	1    4250 1800
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J9
U 1 1 59F779C5
P 4250 3250
F 0 "J9" H 5278 3528 60  0000 L CNN
F 1 "shock_grid" H 5278 3422 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 4250 3250 60  0001 C CNN
F 3 "" H 4250 3250 60  0001 C CNN
	1    4250 3250
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J10
U 1 1 59F77CE3
P 7350 1800
F 0 "J10" H 8378 2078 60  0000 L CNN
F 1 "shock_grid" H 8378 1972 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 7350 1800 60  0001 C CNN
F 3 "" H 7350 1800 60  0001 C CNN
	1    7350 1800
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J8
U 1 1 59F77DC7
P 7350 3250
F 0 "J8" H 8378 3528 60  0000 L CNN
F 1 "shock_grid" H 8378 3422 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 7350 3250 60  0001 C CNN
F 3 "" H 7350 3250 60  0001 C CNN
	1    7350 3250
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J7
U 1 1 59F77FF1
P 4250 4650
F 0 "J7" H 5278 4928 60  0000 L CNN
F 1 "shock_grid" H 5278 4822 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 4250 4650 60  0001 C CNN
F 3 "" H 4250 4650 60  0001 C CNN
	1    4250 4650
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J6
U 1 1 59F780F5
P 7350 4650
F 0 "J6" H 8378 4928 60  0000 L CNN
F 1 "shock_grid" H 8378 4822 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 7350 4650 60  0001 C CNN
F 3 "" H 7350 4650 60  0001 C CNN
	1    7350 4650
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J5
U 1 1 59F78242
P 4250 5800
F 0 "J5" H 5278 6078 60  0000 L CNN
F 1 "shock_grid" H 5278 5972 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 4250 5800 60  0001 C CNN
F 3 "" H 4250 5800 60  0001 C CNN
	1    4250 5800
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J4
U 1 1 59F7866D
P 7350 5800
F 0 "J4" H 8378 6078 60  0000 L CNN
F 1 "shock_grid" H 8378 5972 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_centerflush" H 7350 5800 60  0001 C CNN
F 3 "" H 7350 5800 60  0001 C CNN
	1    7350 5800
	1    0    0    -1  
$EndComp
$Comp
L Conn_01x10_Male J1
U 1 1 59F76D5B
P 1350 3400
F 0 "J1" H 1456 3978 50  0000 C CNN
F 1 "Conn_01x10_Male" H 1456 3887 50  0000 C CNN
F 2 "footprints:SIP-10_2.54mm_1mm_clearance" H 1350 3400 50  0001 C CNN
F 3 "" H 1350 3400 50  0001 C CNN
	1    1350 3400
	1    0    0    -1  
$EndComp
$Comp
L DB25_Male J3
U 1 1 5A2622A3
P 1550 5700
F 0 "J3" H 1470 4208 50  0000 C CNN
F 1 "DB25_Male" H 1470 4299 50  0000 C CNN
F 2 "Connectors_DSub:DSUB-25_Male_Horizontal_Pitch2.77x2.84mm_EdgePinOffset7.70mm_Housed_MountingHolesOffset9.12mm" H 1550 5700 50  0001 C CNN
F 3 "" H 1550 5700 50  0001 C CNN
	1    1550 5700
	-1   0    0    1   
$EndComp
NoConn ~ 1850 5300
NoConn ~ 1850 5400
NoConn ~ 1850 5500
NoConn ~ 1850 5600
NoConn ~ 1850 5800
NoConn ~ 1850 5900
NoConn ~ 1850 6000
NoConn ~ 1850 6100
Text Label 2100 5700 0    60   ~ 0
HV
Text Label 2100 4500 0    60   ~ 0
F16
Text Label 2100 4600 0    60   ~ 0
F14
Text Label 2100 4700 0    60   ~ 0
F12
Text Label 2100 4800 0    60   ~ 0
F10
Text Label 2100 4900 0    60   ~ 0
F8
Text Label 2100 5000 0    60   ~ 0
F6
Text Label 2100 5100 0    60   ~ 0
F4
Text Label 2100 5200 0    60   ~ 0
F2
Text Label 2100 6200 0    60   ~ 0
F15
Text Label 2100 6300 0    60   ~ 0
F13
Text Label 2100 6400 0    60   ~ 0
F11
Text Label 2100 6500 0    60   ~ 0
F9
Text Label 2100 6600 0    60   ~ 0
F7
Text Label 2100 6700 0    60   ~ 0
F5
Text Label 2100 6800 0    60   ~ 0
F3
Text Label 2100 6900 0    60   ~ 0
F1
NoConn ~ 1550 2600
NoConn ~ 1550 3900
Text Label 1850 3400 0    60   ~ 0
HV
Text Label 1850 2100 0    60   ~ 0
HV
Text Label 1850 3000 0    60   ~ 0
F9
Text Label 1850 3100 0    60   ~ 0
F11
Text Label 1850 3200 0    60   ~ 0
F13
Text Label 1850 3300 0    60   ~ 0
F15
Text Label 1850 3500 0    60   ~ 0
F16
Text Label 1850 3600 0    60   ~ 0
F14
Text Label 1850 3700 0    60   ~ 0
F12
Text Label 1850 3800 0    60   ~ 0
F10
Text Label 1850 1700 0    60   ~ 0
F7
Text Label 1850 1800 0    60   ~ 0
F5
Text Label 1850 1900 0    60   ~ 0
F3
Text Label 1850 2000 0    60   ~ 0
F1
Text Label 1850 2200 0    60   ~ 0
F2
Text Label 1850 2300 0    60   ~ 0
F4
Text Label 1850 2400 0    60   ~ 0
F6
Text Label 1850 2500 0    60   ~ 0
F8
Text Label 3750 5400 0    60   ~ 0
HV
Text Label 3750 4250 0    60   ~ 0
HV
Text Label 3750 2850 0    60   ~ 0
HV
Text Label 3750 1300 0    60   ~ 0
HV
Text Label 6850 2850 0    60   ~ 0
HV
Text Label 6850 1400 0    60   ~ 0
HV
Text Label 6850 4250 0    60   ~ 0
HV
Text Label 6850 5400 0    60   ~ 0
HV
Text Label 3250 2300 0    60   ~ 0
F2
Text Label 5250 2300 0    60   ~ 0
F1
Text Label 6350 2300 0    60   ~ 0
F4
Text Label 8350 2300 0    60   ~ 0
F3
Text Label 3250 3750 0    60   ~ 0
F6
Text Label 5250 3750 0    60   ~ 0
F5
Text Label 6350 3750 0    60   ~ 0
F8
Text Label 8350 3750 0    60   ~ 0
F7
Text Label 3250 5150 0    60   ~ 0
F10
Text Label 5250 5150 0    60   ~ 0
F9
Text Label 6350 5150 0    60   ~ 0
F12
Text Label 8350 5150 0    60   ~ 0
F11
Text Label 8350 6300 0    60   ~ 0
F15
Text Label 6350 6300 0    60   ~ 0
F16
Text Label 3250 6300 0    60   ~ 0
F14
Text Label 5250 6300 0    60   ~ 0
F13
Wire Wire Line
	4250 1300 4250 1600
Wire Wire Line
	4250 2850 4250 3050
Wire Wire Line
	7350 2850 7350 3050
Wire Wire Line
	4250 4250 4250 4450
Wire Wire Line
	7350 4250 7350 4450
Wire Wire Line
	4250 5400 4250 5600
Wire Wire Line
	7350 5400 7350 5600
Wire Wire Line
	3750 2300 3750 2000
Wire Wire Line
	3750 3750 3750 3450
Wire Wire Line
	3750 5150 3750 4850
Wire Wire Line
	3750 6300 3750 6000
Wire Wire Line
	6850 2300 6850 2000
Wire Wire Line
	6850 3750 6850 3450
Wire Wire Line
	6850 5150 6850 4850
Wire Wire Line
	6850 6300 6850 6000
Wire Wire Line
	4750 2300 4750 2000
Wire Wire Line
	4750 3750 4750 3450
Wire Wire Line
	4750 5150 4750 4850
Wire Wire Line
	4750 6300 4750 6000
Wire Wire Line
	7850 2300 7850 2000
Wire Wire Line
	7850 3750 7850 3450
Wire Wire Line
	7850 5150 7850 4850
Wire Wire Line
	7850 6300 7850 6000
Wire Wire Line
	7350 1400 7350 1600
Wire Wire Line
	4250 1300 3750 1300
Wire Wire Line
	4250 2850 3750 2850
Wire Wire Line
	4250 5400 3750 5400
Wire Wire Line
	4250 4250 3750 4250
Wire Wire Line
	7350 5400 6850 5400
Wire Wire Line
	7350 4250 6850 4250
Wire Wire Line
	7350 2850 6850 2850
Wire Wire Line
	7350 1400 6850 1400
Wire Wire Line
	6850 2300 6350 2300
Wire Wire Line
	7850 2300 8350 2300
Wire Wire Line
	7850 5150 8350 5150
Wire Wire Line
	6850 5150 6350 5150
Wire Wire Line
	6850 6300 6350 6300
Wire Wire Line
	7850 6300 8350 6300
Wire Wire Line
	3750 6300 3250 6300
Wire Wire Line
	4750 6300 5250 6300
Wire Wire Line
	4750 5150 5250 5150
Wire Wire Line
	3750 5150 3250 5150
Wire Wire Line
	1550 3000 1850 3000
Wire Wire Line
	1550 3100 1850 3100
Wire Wire Line
	1550 3200 1850 3200
Wire Wire Line
	1550 3300 1850 3300
Wire Wire Line
	1550 3400 1850 3400
Wire Wire Line
	1550 3500 1850 3500
Wire Wire Line
	1550 3600 1850 3600
Wire Wire Line
	1550 3700 1850 3700
Wire Wire Line
	1550 3800 1850 3800
Wire Wire Line
	1550 1700 1850 1700
Wire Wire Line
	1550 1800 1850 1800
Wire Wire Line
	1550 1900 1850 1900
Wire Wire Line
	1550 2000 1850 2000
Wire Wire Line
	1550 2100 1850 2100
Wire Wire Line
	1550 2200 1850 2200
Wire Wire Line
	1550 2300 1850 2300
Wire Wire Line
	1550 2400 1850 2400
Wire Wire Line
	1550 2500 1850 2500
Wire Wire Line
	1850 4500 2100 4500
Wire Wire Line
	1850 4600 2100 4600
Wire Wire Line
	1850 4700 2100 4700
Wire Wire Line
	1850 4800 2100 4800
Wire Wire Line
	1850 4900 2100 4900
Wire Wire Line
	1850 5000 2100 5000
Wire Wire Line
	1850 5100 2100 5100
Wire Wire Line
	1850 5200 2100 5200
Wire Wire Line
	1850 5700 2100 5700
Wire Wire Line
	1850 6200 2100 6200
Wire Wire Line
	1850 6300 2100 6300
Wire Wire Line
	1850 6400 2100 6400
Wire Wire Line
	1850 6500 2100 6500
Wire Wire Line
	1850 6600 2100 6600
Wire Wire Line
	1850 6700 2100 6700
Wire Wire Line
	1850 6800 2100 6800
Wire Wire Line
	1850 6900 2100 6900
Wire Wire Line
	6850 3750 6350 3750
Wire Wire Line
	7850 3750 8350 3750
Wire Wire Line
	3750 3750 3250 3750
Wire Wire Line
	4750 3750 5250 3750
Wire Wire Line
	3250 2300 3750 2300
Wire Wire Line
	4750 2300 5250 2300
Text Notes 950  1000 0    60   ~ 0
Lower pin numbers (red) on the 10\npin connectors are to the left.
Text Notes 950  1300 0    60   ~ 0
J2 is currently on top, as seen\nin all design documents.
Text Notes 3550 7550 0    60   ~ 0
TODO change shock_electrodes:shock_grid schematic library part\nso that "left_grid" pin number actually defaults\nto left on footprint. could also change pin numbering\nin footprint.
Text Notes 3550 7000 0    60   ~ 0
TODO edit electrode schematic part to show grids\nalso make it smaller. maybe show fly.
$EndSCHEMATC
