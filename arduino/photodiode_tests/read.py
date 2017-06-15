
import serial

with serial.Serial('/dev/ttyACM0', 9600) as s:
   with open('data.txt', 'w') as f:
       while True:
           print(s.readline(), file=f)
