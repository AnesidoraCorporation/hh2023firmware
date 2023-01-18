import machine
from machine import Pin, PWM, SoftI2C, SoftSPI
import time

ADDRESSPINS     = [0, 1, 2, 3, 4, 5, 6, 7]
DATAPINS        = [8, 9, 10, 11]
RUNPIN          = 12
STEPPIN         = 13
BTN_ENABLEPIN   = 14
LEDRPIN         = 15
LEDGPIN         = 16
LEDBPIN         = 17
ERRORPIN        = 18
BAT_ENPIN       = 19
EEPROMSDAPIN    = 20
EEPROMSCLPIN    = 21
OUTCLKPIN       = 22
OUTSERPIN       = 23
OUTINPIN        = 24
OUTLOADPIN      = 25

SAOSDAPIN       = 26
SAOSCLPIN       = 27
SAOTX           = 28
SAORT           = 29


# Enable running on battery when started by SW3 press
runningonbattery = False

BAT = Pin(BAT_ENPIN, Pin.IN)
if BAT.value() == False:
    machine.freq(12000000)
    BAT = Pin(BAT_ENPIN, Pin.OUT)
    BAT.off()
    runningonbattery = True

# Initialize the PINs
load = Pin(OUTLOADPIN, Pin.IN)

for pinno in ADDRESSPINS:
    Pin(pinno, Pin.OUT, value=1)

for pinno in DATAPINS:
    Pin(pinno, Pin.OUT, value=1)

run     = Pin(RUNPIN,   Pin.OUT, value=1)
step    = Pin(STEPPIN,  Pin.OUT, value=1)
error   = Pin(ERRORPIN, Pin.OUT, value=1)

LEDR    = Pin(LEDRPIN, Pin.OUT, value=1)
LEDG    = Pin(LEDGPIN, Pin.OUT, value=1)
LEDB    = Pin(LEDBPIN, Pin.OUT, value=1)

def initRGB(RGBpwm = True):
    global LEDR
    global LEDG
    global LEDB

    if RGBpwm == True:

        LEDR    = PWM(Pin(LEDRPIN))
        LEDG    = PWM(Pin(LEDGPIN))
        LEDB    = PWM(Pin(LEDBPIN))

        LEDR.freq(1000)
        LEDG.freq(1000)
        LEDB.freq(1000)

        LEDR.duty_u16(65535)
        LEDG.duty_u16(0)
        LEDB.duty_u16(65535)


def ledRGB(color, RGBpwm = True):
    palette = {'BLACK':     [0,0,0],
            'DARKGREY':  [16384,16384,16384],
            'GREY':      [32768,32768,32768],
            'LIGHTGREY': [49152,49152,49152],
            'WHITE':     [65535,65535,65535],
            'RED':       [65535,0,0],
            'GREEN':     [0,65535,0],
            'BLUE':      [0,0,65535],
            'OFF':       [0,0,0],
            'ON':        [65535,65535,65535]}

    if type(color) is str:
        if color in palette:
            color = palette[color]
        else:
            color = [0,0,0]

    if len(color) != 3:
        color = [0,0,0]

    if RGBpwm == True:
        LEDR.duty_u16(65535-color[0])
        LEDG.duty_u16(65535-color[1])
        LEDB.duty_u16(65535-color[2])

    else:
        if color[0] > 65535/2:
            LEDR.value(0)
        else:
            LEDR.value(1)

        if color[1] > 65535/2:
            LEDG.value(0)
        else:
            LEDG.value(1)

        if color[2] > 65535/2:
            LEDB.value(0)
        else:
            LEDB.value(1)

    


# Initialize the EEPROM
eeprom = SoftI2C(scl=Pin(EEPROMSCLPIN), sda=Pin(EEPROMSDAPIN), freq=100000)


#def get_state():
#    addressstate = 0
#    for i in range(8):
#        addressstate = addressstate | (Pin(ADDRESSPINS[i]).value() << i)#

#    datastate = 0
#    for i in range(4):
#        datastate = datastate | (Pin(DATAPINS[i]).value() << i)

#    run = Pin(RUNPIN).value()
#    step = Pin(STEPPIN).value()
#    error = Pin(ERRORPIN).value()

#    return [addressstate, datastate, run, step, error]


#def set_state(addressstate, datastate, runstate, stepstate, errorstate):
#    for i in range(8):
#        if runningonbattery == False:
#            Pin(ADDRESSPINS[i], Pin.OUT, value=(addressstate >> i)&1)
#        elif runningonbattery == True:
#            PWM(Pin(ADDRESSPINS[i])).duty_u16(((addressstate >> i)&1)*10000)



#    for i in range(4):
#        if runningonbattery == False:
#            Pin(DATAPINS[i], Pin.OUT, value=(datastate >> i)&1)
#        elif runningonbattery == True:
#            PWM(Pin(DATAPINS[i])).duty_u16(((datastate >> i)&1)*10000)


#    if runningonbattery == False:
#        Pin(RUNPIN, Pin.OUT, value=runstate)
#        Pin(STEPPIN, Pin.OUT, value=stepstate)
#        Pin(ERRORPIN, Pin.OUT, value=errorstate)
#    elif runningonbattery == True:
#        PWM(Pin(RUNPIN)).duty_u16(runstate*10000)
#        PWM(Pin(STEPPIN)).duty_u16(stepstate*10000)
#        PWM(Pin(ERRORPIN)).duty_u16(errorstate*10000)

def set_state(addressstate, datastate, runstate, stepstate, errorstate):
    for i in range(8):
        Pin(ADDRESSPINS[i], Pin.OUT, value=(addressstate >> i)&1)

    for i in range(4):
        Pin(DATAPINS[i], Pin.OUT, value=(datastate >> i)&1)


    Pin(RUNPIN, Pin.OUT, value=runstate)
    Pin(STEPPIN, Pin.OUT, value=stepstate)
    Pin(ERRORPIN, Pin.OUT, value=errorstate)



def get_buttons():
    for pinno in ADDRESSPINS:
        Pin(pinno, Pin.OUT, value=0)
    
    for pinno in DATAPINS:
        Pin(pinno, Pin.OUT, value=0)

    Pin(RUNPIN, Pin.OUT, value=0)
    Pin(STEPPIN, Pin.OUT, value=0)
    Pin(ERRORPIN, Pin.OUT, value=0)

    btn = Pin(BTN_ENABLEPIN, Pin.OUT, value=1)

    address = 0
    for i in range(8):
        address = address | (Pin(ADDRESSPINS[i], Pin.IN).value() << i)

    data = 0
    for i in range(4):
        data = data | (Pin(DATAPINS[i], Pin.IN).value() << i)

    run = Pin(RUNPIN, Pin.IN).value()
    step = Pin(STEPPIN, Pin.IN).value()
    error = Pin(ERRORPIN, Pin.IN).value()

    btn = Pin(BTN_ENABLEPIN, Pin.IN)

    if address > 0 or data > 0 or run > 0 or step > 0 or error > 0:
        buttonpressed = True
    else:
        buttonpressed = False

    return [address, data, run, step, error, buttonpressed]

    
def buttonstate(addressstate, datastate, runstate, stepstate, errorstate):
    [address, data, run, step, error, buttonpressed] = get_buttons()
    addressstate = addressstate ^ address
    datastate = datastate ^ data
    set_state(addressstate, datastate, runstate, stepstate, errorstate)
    return [addressstate, datastate, run, step, error, buttonpressed]


def shiftregister(dataout=0, delay=20):
    outclk = Pin(OUTCLKPIN, Pin.OUT, value=1)
    outser = Pin(OUTSERPIN, Pin.OUT, value=0)
    outin = Pin(OUTINPIN, Pin.IN)
    datain = 0
    time.sleep_ms(delay)

    for i in range(8):
        datain = (datain << 1) + outin.value()
        outser.value(dataout >> (7-i) & 1)
        time.sleep_ms(delay)
        outclk.off()
        time.sleep_ms(delay)
        outclk.on()

    Pin(OUTCLKPIN, Pin.IN)
    Pin(OUTSERPIN, Pin.IN)
    Pin(OUTINPIN, Pin.IN)

    return datain
