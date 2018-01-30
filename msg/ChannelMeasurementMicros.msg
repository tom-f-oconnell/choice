# high 6 bits allocated for the channel number
# low (least significant, rightmost) 10 bits are the ADC reading
uint16 channel_measurement

# an Arduino "unsigned long," the return type of micros()
# 4us resolution on 16MHz boards (not sure about higher frequency boards)
# see https://electronics.stackexchange.com/questions/22584/
# arduino-better-microsecond-resolution-than-micros
uint32 micros
