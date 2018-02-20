EESchema Schematic File Version 4
LIBS:ceiling_pcb-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "8 chamber shock conditioning ceiling grid"
Date "2017-12-06"
Rev "0.1"
Comp "Hong lab @ Caltech"
Comment1 "github.com/tom-f-oconnell/choice"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L shock_electrodes:shock_grid J3
U 1 1 59F778B5
P 4350 1450
F 0 "J3" H 5378 1728 60  0000 L CNN
F 1 "shock_grid" H 5378 1622 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 4350 1450 60  0001 C CNN
F 3 "" H 4350 1450 60  0001 C CNN
	1    4350 1450
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J5
U 1 1 59F779C5
P 4350 2900
F 0 "J5" H 5378 3178 60  0000 L CNN
F 1 "shock_grid" H 5378 3072 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 4350 2900 60  0001 C CNN
F 3 "" H 4350 2900 60  0001 C CNN
	1    4350 2900
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J4
U 1 1 59F77CE3
P 7450 1450
F 0 "J4" H 8478 1728 60  0000 L CNN
F 1 "shock_grid" H 8478 1622 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 7450 1450 60  0001 C CNN
F 3 "" H 7450 1450 60  0001 C CNN
	1    7450 1450
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J6
U 1 1 59F77DC7
P 7450 2900
F 0 "J6" H 8478 3178 60  0000 L CNN
F 1 "shock_grid" H 8478 3072 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 7450 2900 60  0001 C CNN
F 3 "" H 7450 2900 60  0001 C CNN
	1    7450 2900
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J7
U 1 1 59F77FF1
P 4350 4300
F 0 "J7" H 5378 4578 60  0000 L CNN
F 1 "shock_grid" H 5378 4472 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 4350 4300 60  0001 C CNN
F 3 "" H 4350 4300 60  0001 C CNN
	1    4350 4300
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J8
U 1 1 59F780F5
P 7450 4300
F 0 "J8" H 8478 4578 60  0000 L CNN
F 1 "shock_grid" H 8478 4472 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 7450 4300 60  0001 C CNN
F 3 "" H 7450 4300 60  0001 C CNN
	1    7450 4300
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J9
U 1 1 59F78242
P 4350 5450
F 0 "J9" H 5378 5728 60  0000 L CNN
F 1 "shock_grid" H 5378 5622 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 4350 5450 60  0001 C CNN
F 3 "" H 4350 5450 60  0001 C CNN
	1    4350 5450
	1    0    0    -1  
$EndComp
$Comp
L shock_electrodes:shock_grid J10
U 1 1 59F7866D
P 7450 5450
F 0 "J10" H 8478 5728 60  0000 L CNN
F 1 "shock_grid" H 8478 5622 60  0000 L CNN
F 2 "footprints:electrodes_clearance0.6mm_W0.4mm_lengthwise" H 7450 5450 60  0001 C CNN
F 3 "" H 7450 5450 60  0001 C CNN
	1    7450 5450
	1    0    0    -1  
$EndComp
$Comp
L ceiling_pcb:Conn_01x09 J1
U 1 1 59F76D5B
P 1750 3150
F 0 "J1" H 1750 2450 50  0000 C CNN
F 1 "Conn_01x09" H 1750 2550 50  0000 C CNN
F 2 "footprints:contacts_9_P2.54mm_L6mm_W1.94mm" H 1750 3150 50  0001 C CNN
F 3 "" H 1750 3150 50  0001 C CNN
	1    1750 3150
	-1   0    0    1   
$EndComp
Text Label 2250 3150 0    60   ~ 0
HV
Text Label 3850 5050 0    60   ~ 0
HV
Text Label 3850 3900 0    60   ~ 0
HV
Text Label 3850 2500 0    60   ~ 0
HV
Text Label 3850 950  0    60   ~ 0
HV
Text Label 6950 2500 0    60   ~ 0
HV
Text Label 6950 1050 0    60   ~ 0
HV
Text Label 6950 3900 0    60   ~ 0
HV
Text Label 6950 5050 0    60   ~ 0
HV
Wire Wire Line
	4350 950  4350 1250
Wire Wire Line
	4350 2500 4350 2700
Wire Wire Line
	7450 2500 7450 2700
Wire Wire Line
	4350 3900 4350 4100
Wire Wire Line
	7450 3900 7450 4100
Wire Wire Line
	4350 5050 4350 5250
Wire Wire Line
	7450 5050 7450 5250
Wire Wire Line
	3850 1950 3850 1650
Wire Wire Line
	3850 3400 3850 3100
Wire Wire Line
	3850 4800 3850 4500
Wire Wire Line
	3850 5950 3850 5650
Wire Wire Line
	6950 1950 6950 1650
Wire Wire Line
	6950 3400 6950 3100
Wire Wire Line
	6950 4800 6950 4500
Wire Wire Line
	6950 5950 6950 5650
Wire Wire Line
	4850 1950 4850 1650
Wire Wire Line
	4850 3400 4850 3100
Wire Wire Line
	4850 4800 4850 4500
Wire Wire Line
	4850 5950 4850 5650
Wire Wire Line
	7950 1950 7950 1650
Wire Wire Line
	7950 3400 7950 3100
Wire Wire Line
	7950 4800 7950 4500
Wire Wire Line
	7950 5950 7950 5650
Wire Wire Line
	7450 1050 7450 1250
Wire Wire Line
	4350 950  3850 950 
Wire Wire Line
	4350 2500 3850 2500
Wire Wire Line
	4350 5050 3850 5050
Wire Wire Line
	4350 3900 3850 3900
Wire Wire Line
	7450 5050 6950 5050
Wire Wire Line
	7450 3900 6950 3900
Wire Wire Line
	7450 2500 6950 2500
Wire Wire Line
	7450 1050 6950 1050
Wire Wire Line
	6950 1950 6450 1950
Wire Wire Line
	7950 1950 8450 1950
Wire Wire Line
	7950 4800 8450 4800
Wire Wire Line
	6950 4800 6450 4800
Wire Wire Line
	6950 5950 6450 5950
Wire Wire Line
	7950 5950 8450 5950
Wire Wire Line
	3850 5950 3350 5950
Wire Wire Line
	4850 5950 5350 5950
Wire Wire Line
	4850 4800 5350 4800
Wire Wire Line
	3850 4800 3350 4800
Wire Wire Line
	1950 2750 2250 2750
Wire Wire Line
	1950 2850 2250 2850
Wire Wire Line
	1950 2950 2250 2950
Wire Wire Line
	1950 3050 2250 3050
Wire Wire Line
	1950 3150 2250 3150
Wire Wire Line
	1950 3250 2250 3250
Wire Wire Line
	1950 3350 2250 3350
Wire Wire Line
	1950 3450 2250 3450
Wire Wire Line
	1950 3550 2250 3550
Wire Wire Line
	1950 4200 2250 4200
Wire Wire Line
	1950 4300 2250 4300
Wire Wire Line
	1950 4400 2250 4400
Wire Wire Line
	1950 4500 2250 4500
Wire Wire Line
	1950 4600 2250 4600
Wire Wire Line
	1950 4700 2250 4700
Wire Wire Line
	1950 4800 2250 4800
Wire Wire Line
	1950 4900 2250 4900
Wire Wire Line
	1950 5000 2250 5000
Wire Wire Line
	6950 3400 6450 3400
Wire Wire Line
	7950 3400 8450 3400
Wire Wire Line
	3850 3400 3350 3400
Wire Wire Line
	4850 3400 5350 3400
Wire Wire Line
	3350 1950 3850 1950
Wire Wire Line
	4850 1950 5350 1950
$Comp
L ceiling_pcb:Conn_01x09 J2
U 1 1 5A268DBE
P 1750 4600
F 0 "J2" H 1750 3900 50  0000 C CNN
F 1 "Conn_01x09" H 1750 4000 50  0000 C CNN
F 2 "footprints:contacts_9_P2.54mm_L6mm_W1.94mm" H 1750 4600 50  0001 C CNN
F 3 "" H 1750 4600 50  0001 C CNN
	1    1750 4600
	-1   0    0    1   
$EndComp
Text Label 2250 4600 0    60   ~ 0
HV
Wire Wire Line
	2250 3250 2250 3350
Wire Wire Line
	2250 3350 2250 3400
Connection ~ 2250 3350
Wire Wire Line
	2250 3450 2250 3550
Connection ~ 2250 3450
Wire Wire Line
	2250 4700 2250 4800
Wire Wire Line
	2250 4800 2250 4850
Connection ~ 2250 4800
Wire Wire Line
	2250 4900 2250 5000
Connection ~ 2250 4900
Text Label 2350 4850 0    60   ~ 0
right
Text Label 2350 3400 0    60   ~ 0
right
Wire Wire Line
	2250 2750 2250 2850
Wire Wire Line
	2250 2850 2250 2900
Connection ~ 2250 2850
Wire Wire Line
	2250 2950 2250 3050
Connection ~ 2250 2950
Text Label 2350 2900 0    60   ~ 0
left
Text Label 2350 4350 0    60   ~ 0
left
Wire Wire Line
	2250 4200 2250 4300
Wire Wire Line
	2250 4300 2250 4350
Connection ~ 2250 4300
Wire Wire Line
	2250 4500 2250 4400
Connection ~ 2250 4400
Wire Wire Line
	2250 4350 2350 4350
Connection ~ 2250 4350
Wire Wire Line
	2250 4350 2250 4400
Wire Wire Line
	2250 4850 2350 4850
Connection ~ 2250 4850
Wire Wire Line
	2250 4850 2250 4900
Wire Wire Line
	2250 2900 2350 2900
Connection ~ 2250 2900
Wire Wire Line
	2250 2900 2250 2950
Wire Wire Line
	2250 3400 2350 3400
Connection ~ 2250 3400
Wire Wire Line
	2250 3400 2250 3450
Text Label 3350 1950 0    60   ~ 0
right
Text Label 3350 3400 0    60   ~ 0
right
Text Label 3350 4800 0    60   ~ 0
right
Text Label 3350 5950 0    60   ~ 0
right
Text Label 6450 5950 0    60   ~ 0
right
Text Label 6450 4800 0    60   ~ 0
right
Text Label 6450 3400 0    60   ~ 0
right
Text Label 6450 1950 0    60   ~ 0
right
Text Label 5350 1950 0    60   ~ 0
left
Text Label 5350 3400 0    60   ~ 0
left
Text Label 5350 4800 0    60   ~ 0
left
Text Label 5350 5950 0    60   ~ 0
left
Text Label 8450 5950 0    60   ~ 0
left
Text Label 8450 4800 0    60   ~ 0
left
Text Label 8450 3400 0    60   ~ 0
left
Text Label 8450 1950 0    60   ~ 0
left
$EndSCHEMATC
