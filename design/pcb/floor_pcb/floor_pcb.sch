EESchema Schematic File Version 3
LIBS:shock_grid
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
LIBS:floor_pcb-cache
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
L Conn_02x10_Top_Bottom J3
U 1 1 59F76C47
P 1150 1800
F 0 "J3" H 1200 2417 50  0000 C CNN
F 1 "Conn_02x10_Top_Bottom" H 1200 2326 50  0000 C CNN
F 2 "footprints:DIP-2x10_2.54mm_1mm_clearance" H 1150 1800 50  0001 C CNN
F 3 "" H 1150 1800 50  0001 C CNN
	1    1150 1800
	1    0    0    -1  
$EndComp
$Comp
L Conn_01x10_Male J2
U 1 1 59F76DF3
P 1100 4500
F 0 "J2" H 1206 5078 50  0000 C CNN
F 1 "Conn_01x10_Male" H 1206 4987 50  0000 C CNN
F 2 "footprints:SIP-10_2.54mm_1mm_clearance" H 1100 4500 50  0001 C CNN
F 3 "" H 1100 4500 50  0001 C CNN
	1    1100 4500
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J4
U 1 1 59F778B5
P 4350 1450
F 0 "J4" H 5378 1728 60  0000 L CNN
F 1 "shock_grid" H 5378 1622 60  0000 L CNN
F 2 "footprints:electrode" H 4350 1450 60  0001 C CNN
F 3 "" H 4350 1450 60  0001 C CNN
	1    4350 1450
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J5
U 1 1 59F779C5
P 4350 2900
F 0 "J5" H 5378 3178 60  0000 L CNN
F 1 "shock_grid" H 5378 3072 60  0000 L CNN
F 2 "footprints:electrode" H 4350 2900 60  0001 C CNN
F 3 "" H 4350 2900 60  0001 C CNN
	1    4350 2900
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J8
U 1 1 59F77CE3
P 7450 1450
F 0 "J8" H 8478 1728 60  0000 L CNN
F 1 "shock_grid" H 8478 1622 60  0000 L CNN
F 2 "footprints:electrode" H 7450 1450 60  0001 C CNN
F 3 "" H 7450 1450 60  0001 C CNN
	1    7450 1450
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J9
U 1 1 59F77DC7
P 7450 2900
F 0 "J9" H 8478 3178 60  0000 L CNN
F 1 "shock_grid" H 8478 3072 60  0000 L CNN
F 2 "footprints:electrode" H 7450 2900 60  0001 C CNN
F 3 "" H 7450 2900 60  0001 C CNN
	1    7450 2900
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J6
U 1 1 59F77FF1
P 4350 4300
F 0 "J6" H 5378 4578 60  0000 L CNN
F 1 "shock_grid" H 5378 4472 60  0000 L CNN
F 2 "footprints:electrode" H 4350 4300 60  0001 C CNN
F 3 "" H 4350 4300 60  0001 C CNN
	1    4350 4300
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J10
U 1 1 59F780F5
P 7450 4300
F 0 "J10" H 8478 4578 60  0000 L CNN
F 1 "shock_grid" H 8478 4472 60  0000 L CNN
F 2 "footprints:electrode" H 7450 4300 60  0001 C CNN
F 3 "" H 7450 4300 60  0001 C CNN
	1    7450 4300
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J7
U 1 1 59F78242
P 4350 5450
F 0 "J7" H 5378 5728 60  0000 L CNN
F 1 "shock_grid" H 5378 5622 60  0000 L CNN
F 2 "footprints:electrode" H 4350 5450 60  0001 C CNN
F 3 "" H 4350 5450 60  0001 C CNN
	1    4350 5450
	1    0    0    -1  
$EndComp
$Comp
L shock_grid J11
U 1 1 59F7866D
P 7450 5450
F 0 "J11" H 8478 5728 60  0000 L CNN
F 1 "shock_grid" H 8478 5622 60  0000 L CNN
F 2 "footprints:electrode" H 7450 5450 60  0001 C CNN
F 3 "" H 7450 5450 60  0001 C CNN
	1    7450 5450
	1    0    0    -1  
$EndComp
$Comp
L Conn_01x10_Male J1
U 1 1 59F76D5B
P 1100 3350
F 0 "J1" H 1206 3928 50  0000 C CNN
F 1 "Conn_01x10_Male" H 1206 3837 50  0000 C CNN
F 2 "footprints:SIP-10_2.54mm_1mm_clearance" H 1100 3350 50  0001 C CNN
F 3 "" H 1100 3350 50  0001 C CNN
	1    1100 3350
	1    0    0    -1  
$EndComp
Wire Wire Line
	950  750  950  1400
Wire Wire Line
	950  750  5850 750 
Wire Wire Line
	5850 750  5850 5100
Wire Wire Line
	4350 950  7450 950 
Wire Wire Line
	4350 950  4350 1250
Wire Wire Line
	7450 950  7450 1250
Connection ~ 5850 950 
Wire Wire Line
	4350 2500 7450 2500
Wire Wire Line
	4350 2500 4350 2700
Wire Wire Line
	7450 2500 7450 2700
Connection ~ 5850 2500
Wire Wire Line
	4350 3900 7450 3900
Wire Wire Line
	4350 3900 4350 4100
Wire Wire Line
	7450 3900 7450 4100
Connection ~ 5850 3900
Wire Wire Line
	4350 5100 7450 5100
Wire Wire Line
	4350 5100 4350 5250
Wire Wire Line
	7450 5100 7450 5250
Connection ~ 5850 5100
Wire Wire Line
	900  1500 950  1500
Wire Wire Line
	900  700  900  1500
Wire Wire Line
	900  700  3300 700 
Wire Wire Line
	3300 700  3300 1800
Wire Wire Line
	3300 1800 3850 1800
Wire Wire Line
	3850 1800 3850 1650
Wire Wire Line
	850  1600 950  1600
Wire Wire Line
	850  650  850  1600
Wire Wire Line
	850  650  3250 650 
Wire Wire Line
	3250 650  3250 3300
Wire Wire Line
	3250 3300 3850 3300
Wire Wire Line
	3850 3300 3850 3100
Wire Wire Line
	800  1700 950  1700
Wire Wire Line
	800  600  800  1700
Wire Wire Line
	800  600  3200 600 
Wire Wire Line
	3200 600  3200 4700
Wire Wire Line
	3200 4700 3850 4700
Wire Wire Line
	3850 4700 3850 4500
Wire Wire Line
	750  1800 950  1800
Wire Wire Line
	750  550  750  1800
Wire Wire Line
	750  550  3150 550 
Wire Wire Line
	3150 550  3150 5900
Wire Wire Line
	3150 5900 3850 5900
Wire Wire Line
	3850 5900 3850 5650
Wire Wire Line
	750  1900 950  1900
Wire Wire Line
	750  1900 750  2550
Wire Wire Line
	2600 2550 2600 1950
Wire Wire Line
	2600 1950 6950 1950
Wire Wire Line
	6950 1950 6950 1650
Wire Wire Line
	950  2000 800  2000
Wire Wire Line
	800  2000 800  2500
Wire Wire Line
	800  2500 2550 2500
Wire Wire Line
	2550 2500 2550 2000
Wire Wire Line
	2550 2000 6350 2000
Wire Wire Line
	6350 2000 6350 3300
Wire Wire Line
	6350 3300 6950 3300
Wire Wire Line
	6950 3300 6950 3100
Wire Wire Line
	950  2100 850  2100
Wire Wire Line
	850  2100 850  2450
Wire Wire Line
	850  2450 2500 2450
Wire Wire Line
	2500 2450 2500 2100
Wire Wire Line
	2500 2100 6250 2100
Wire Wire Line
	6250 2100 6250 4700
Wire Wire Line
	6250 4700 6950 4700
Wire Wire Line
	6950 4700 6950 4500
Wire Wire Line
	950  2200 900  2200
Wire Wire Line
	900  2200 900  2400
Wire Wire Line
	900  2400 2450 2400
Wire Wire Line
	2450 2400 2450 2200
Wire Wire Line
	2450 2200 6150 2200
Wire Wire Line
	6150 2200 6150 5900
Wire Wire Line
	6150 5900 6950 5900
Wire Wire Line
	6950 5900 6950 5650
Wire Wire Line
	1450 1500 2950 1500
Wire Wire Line
	2950 1500 2950 1850
Wire Wire Line
	2950 1850 4850 1850
Wire Wire Line
	4850 1850 4850 1650
Wire Wire Line
	1450 1600 2900 1600
Wire Wire Line
	2900 1600 2900 3450
Wire Wire Line
	2900 3450 4850 3450
Wire Wire Line
	4850 3450 4850 3100
Wire Wire Line
	1450 1700 2800 1700
Wire Wire Line
	2800 1700 2800 4850
Wire Wire Line
	2800 4850 4850 4850
Wire Wire Line
	4850 4850 4850 4500
Wire Wire Line
	1450 1800 2750 1800
Wire Wire Line
	2750 1800 2750 6150
Wire Wire Line
	2750 6150 4850 6150
Wire Wire Line
	4850 6150 4850 5650
Wire Wire Line
	1450 1900 2300 1900
Wire Wire Line
	2300 1900 2300 6950
Wire Wire Line
	2300 6950 9250 6950
Wire Wire Line
	9250 6950 9250 1900
Wire Wire Line
	9250 1900 7950 1900
Wire Wire Line
	7950 1900 7950 1650
Wire Wire Line
	1450 2000 2250 2000
Wire Wire Line
	2250 2000 2250 7000
Wire Wire Line
	2250 7000 9200 7000
Wire Wire Line
	9200 7000 9200 3300
Wire Wire Line
	9200 3300 7950 3300
Wire Wire Line
	7950 3300 7950 3100
Wire Wire Line
	1450 2100 2200 2100
Wire Wire Line
	2200 2100 2200 7050
Wire Wire Line
	2200 7050 9150 7050
Wire Wire Line
	9150 7050 9150 4700
Wire Wire Line
	9150 4700 7950 4700
Wire Wire Line
	7950 4700 7950 4500
Wire Wire Line
	1450 2200 2150 2200
Wire Wire Line
	2150 2200 2150 7100
Wire Wire Line
	2150 7100 9100 7100
Wire Wire Line
	9100 7100 9100 5900
Wire Wire Line
	9100 5900 7950 5900
Wire Wire Line
	7950 5900 7950 5650
Wire Wire Line
	1300 3350 1400 3350
Wire Wire Line
	1400 3350 1400 3300
Wire Wire Line
	1400 3300 550  3300
Wire Wire Line
	550  1350 550  4450
Wire Wire Line
	550  1350 950  1350
Connection ~ 950  1350
Wire Wire Line
	1300 4500 1450 4500
Wire Wire Line
	1450 4500 1450 4450
Wire Wire Line
	1450 4450 550  4450
Connection ~ 550  3300
Wire Wire Line
	700  1400 900  1400
Connection ~ 900  1400
Wire Wire Line
	650  1550 650  3500
Wire Wire Line
	650  1550 850  1550
Connection ~ 850  1550
Wire Wire Line
	600  1600 600  3600
Wire Wire Line
	600  1600 800  1600
Connection ~ 800  1600
Wire Wire Line
	500  1750 500  3700
Wire Wire Line
	500  1750 750  1750
Connection ~ 750  1750
Connection ~ 1500 1500
Connection ~ 1550 1600
Connection ~ 1600 1700
Connection ~ 1650 1800
Connection ~ 2350 2550
Connection ~ 2400 2500
Connection ~ 2450 2450
Connection ~ 2650 2200
Connection ~ 1800 1900
Connection ~ 1850 2000
Connection ~ 1900 2100
Connection ~ 1950 2200
Wire Wire Line
	1300 2950 1500 2950
Wire Wire Line
	1500 2950 1500 1500
Wire Wire Line
	1300 3050 1550 3050
Wire Wire Line
	1550 3050 1550 1600
Wire Wire Line
	1300 3150 1600 3150
Wire Wire Line
	1600 3150 1600 1700
Wire Wire Line
	1300 3250 1650 3250
Wire Wire Line
	1650 3250 1650 1800
Wire Wire Line
	1300 3450 1400 3450
Wire Wire Line
	1400 3450 1400 3400
Wire Wire Line
	1400 3400 700  3400
Wire Wire Line
	700  3400 700  1400
Wire Wire Line
	1300 3550 1400 3550
Wire Wire Line
	1400 3550 1400 3500
Wire Wire Line
	1400 3500 650  3500
Wire Wire Line
	1300 3650 1400 3650
Wire Wire Line
	1400 3650 1400 3600
Wire Wire Line
	1400 3600 600  3600
Wire Wire Line
	1300 3750 1400 3750
Wire Wire Line
	1400 3750 1400 3700
Wire Wire Line
	1400 3700 500  3700
Wire Wire Line
	1300 4100 1800 4100
Wire Wire Line
	1800 4100 1800 1900
Wire Wire Line
	1300 4200 1850 4200
Wire Wire Line
	1850 4200 1850 2000
Wire Wire Line
	1300 4300 1900 4300
Wire Wire Line
	1900 4300 1900 2100
Wire Wire Line
	1300 4400 1950 4400
Wire Wire Line
	1950 4400 1950 2200
Wire Wire Line
	750  2550 2600 2550
Wire Wire Line
	1300 4600 2650 4600
Wire Wire Line
	2650 4600 2650 2200
Wire Wire Line
	1300 4700 2450 4700
Wire Wire Line
	2450 4700 2450 2450
Wire Wire Line
	1300 4800 2400 4800
Wire Wire Line
	2400 4800 2400 2500
Wire Wire Line
	1300 4900 2350 4900
Wire Wire Line
	2350 4900 2350 2550
NoConn ~ 1300 3850
NoConn ~ 1300 5000
NoConn ~ 950  2300
NoConn ~ 1450 2300
NoConn ~ 1450 1400
$EndSCHEMATC
