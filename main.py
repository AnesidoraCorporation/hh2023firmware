import machine
from machine import Pin, SoftI2C, SoftSPI, UART
import time
import random

from hh2022 import *
import challenges
import memory
import game
import common

import sys
import uselect

initRGB(not runningonbattery)
set_state(0,0,0,0,0)

#ledRGB([65000,0,0], not runningonbattery)

#time.sleep_ms(1000)

ledRGB([0,0,0], not runningonbattery)

# OK, we're running on USB, so let's go!
btns            = [0,0,0,0,0]
mem             = [0]*256
datamem         = [0]*256
datapointer     = 0
address         = 0
loopcounter     = 0
running         = False
debug           = False
extradebug      = False
productionhw    = True

if productionhw == True:
    eepromsize = 8
else:
    eepromsize = 16

if extradebug == True:
    for i in range(43):
        shiftregister(eeprom.readfrom_mem(80, i, 1, addrsize=eepromsize)[0])
        set_state(i,0,0,0,0)
        time.sleep_ms(200)

statusled = True

btns = get_buttons()

if debug == True:
    print(btns)

adventuremem = eeprom.readfrom_mem(80, 64, 32, addrsize=eepromsize)
adventureinit = False
for i in adventuremem:
    if i != 255:
        adventureinit = True
        break

if adventureinit == False:
    for i in range(32):
        time.sleep_ms(10)
        eeprom.writeto_mem(80, i+64, b'\x00',addrsize=eepromsize)


if btns[4] == 1 or eeprom.readfrom_mem(80, 1, 1, addrsize=eepromsize)[0] == 255:
    time.sleep_ms(10)
    eeprom.writeto_mem(80, 0, b'\xFF',addrsize=eepromsize)
    time.sleep_ms(10)
    eeprom.writeto_mem(80, 1, b'\x00',addrsize=eepromsize)
    time.sleep_ms(10)
    eeprom.writeto_mem(80, 42, b'\xFF',addrsize=eepromsize)
    time.sleep_ms(10)
    eeprom.writeto_mem(80, 43, b'\xFF',addrsize=eepromsize)
    for i in range(32):
        time.sleep_ms(10)
        eeprom.writeto_mem(80, i+64, b'\x00',addrsize=eepromsize)
    
    ledRGB([0,65500,0], not runningonbattery)
    time.sleep_ms(1000)
    print("Config reset")

if btns[3] == 1:
    time.sleep_ms(10)
    eeprom.writeto_mem(80, 43, b'\xFF',addrsize=eepromsize)
    for i in range(32):
        time.sleep_ms(10)
        eeprom.writeto_mem(80, i+64, b'\x00',addrsize=eepromsize)
    
    ledRGB([0,0,65500], not runningonbattery)
    time.sleep_ms(1000)
    print("Adventure reset")

if btns[2] == 1:
    ledRGB([65500,65500,65500], not runningonbattery)
    for i in range(256):
        time.sleep_ms(10)
        eeprom.writeto_mem(80, i, b'\xFF',addrsize=eepromsize)
    
    
    time.sleep_ms(10000)
    print("Total reset")
    machine.soft_reset()

common.read_state(eeprom)

bootstate = eeprom.readfrom_mem(80,42,1,addrsize=eepromsize)
bootstate = bootstate[0]
if debug == True:
    print(f"Bootstate = {bootstate}")

print("Woke up, booting system using state {}".format(bootstate))


errorstate = eeprom.readfrom_mem(80,0,1,addrsize=eepromsize)[0]
olderrorstate = errorstate


if bootstate == 0xFF or errorstate > 0:

    if errorstate > 0:
        print(f"Missing values in configuration memory, locations to be cleared are: {errorstate:08b}")
        print("To enter a value, hold LOAD during boot and use the SER and CLK buttons to set the I/O leds. Then press load again")
        set_state(errorstate,0,0,0,1)

        set_state(0,0,0,0,1)

        if load.value() == 1:
            print("Entering value load stage. Use the SER and CLK buttons to set the I/O leds. Then press load again")
            ledtimer = time.ticks_add(time.ticks_ms(), 500)
            loadtimer = time.ticks_add(time.ticks_ms(), 120000)
            loadstate = True
            while time.ticks_diff(time.ticks_ms(), loadtimer) < 0:

                if time.ticks_diff(time.ticks_ms(), ledtimer) > 0:
                    if statusled == True:
                        if runningonbattery == False:
                            ledRGB('GREEN', not runningonbattery)
                            ledtimer = time.ticks_add(time.ticks_ms(), 500)
                        else:
                            ledRGB('GREEN', not runningonbattery)
                            ledtimer = time.ticks_add(time.ticks_ms(), 100)
                        statusled = False
                    else:
                        ledRGB('OFF', not runningonbattery)
                        statusled = True

                        if runningonbattery == False:
                            ledtimer = time.ticks_add(time.ticks_ms(), 500)
                        else:
                            ledtimer = time.ticks_add(time.ticks_ms(), 1900)

                if loadstate == True and load.value() == 0:
                    loadstate = False
                
                if loadstate == False and load.value() == 1:
                    break
        else:
            for i in range(10):
                ledRGB('OFF', not runningonbattery)
                set_state(errorstate,0,0,0,1)
                time.sleep_ms(100)
                ledRGB('RED', not runningonbattery)
                set_state(errorstate,0,0,0,0)
                time.sleep_ms(100)

            ledRGB([65000,0,0], not runningonbattery)
                



    errorcode = shiftregister(0)
    shiftregister(errorcode)

    if errorcode == 0b10000000:
        errorstate = errorstate & 0b11111110
    elif errorcode == 0b10110100:
        errorstate = errorstate & 0b11111101
    elif errorcode == 0b11101010:
        errorstate = errorstate & 0b11111011
    elif errorcode == 0b01101101:
        errorstate = errorstate & 0b11110111
    elif errorcode == 0b11011101:
        errorstate = errorstate & 0b11101111
    elif errorcode == 0b11010011:
        errorstate = errorstate & 0b11011111
    elif errorcode == 0b10011001:
        errorstate = errorstate & 0b10111111
    elif errorcode == 0b11100010:
        errorstate = errorstate & 0b01111111

    if errorstate != olderrorstate:
        print("Entered correct value into configuration memory")
        ledRGB('GREEN', not runningonbattery)
        if errorstate > 0:
            print(f"More locations have to be found: {errorstate:08b}")
            ledRGB([65000,65000,0], not runningonbattery)    
    else:
        print("Entered incorrect value.")
        ledRGB('RED', not runningonbattery)

    for i in range(2):
        set_state(errorstate,0b0001,0,0,1)
        time.sleep_ms(200)
        set_state(olderrorstate,0b0010,0,0,0)
        time.sleep_ms(200)
        set_state(errorstate,0b0100,0,0,1)
        time.sleep_ms(200)
        set_state(olderrorstate,0b1000,0,0,0)
        time.sleep_ms(200)
        set_state(errorstate,0b0100,0,0,1)
        time.sleep_ms(200)
        set_state(olderrorstate,0b0010,0,0,0)
        time.sleep_ms(200)
        set_state(errorstate,0b0001,0,0,1)
        time.sleep_ms(200)


    writebuffer = bytearray(1)
    writebuffer[0] = errorstate

    eeprom.writeto_mem(80, 0, writebuffer,addrsize=eepromsize)

    time.sleep_ms(1000)

if errorstate == 0 and common.get_state(123) == False:
    common.update_state(123,eeprom)


username = eeprom.readfrom_mem(80,2,32,addrsize=eepromsize)
set_state(0,0,0,0,0)

shiftregister(0)
time.sleep_ms(500)

if username[0] != 0xff:
    for i in range(32):
        if username[i] != 0xff:
            print(f"{username[i]:c}",end="")
            shiftregister(username[i])
            time.sleep_ms(500)
    print("")

shiftregister(0)


ledRGB('GREEN', not runningonbattery)

#if debug == True:
#    errorstate = 0

if errorstate == 0:
    print("Cleared configuration memory errors, starting boot sequence")

ledtimer        = time.ticks_add(time.ticks_ms(), 500)

if runningonbattery == False:
    buttontimer = time.ticks_add(time.ticks_ms(), 100)
else:
    buttontimer = time.ticks_add(time.ticks_ms(), 500)


if runningonbattery == False:
    idletimer = time.ticks_add(time.ticks_ms(), 30000)
else:
    idletimer = time.ticks_add(time.ticks_ms(), 15000)
idle = True

if bootstate == 5 or (bootstate == 7 and runningonbattery):
    uart = UART(0, baudrate=300, bits=8, parity=None, stop=1, tx=Pin(28), rx=Pin(29))

inputstring = ""

uarttimer = time.ticks_add(time.ticks_ms(), 10000)

if errorstate > 0 or bootstate == 5 or (bootstate == 7 and runningonbattery):
    
    randno = 0
    challengecounter = 0
    challengecounter = eeprom.readfrom_mem(80,1,1,addrsize=eepromsize)[0]

    if challengecounter > 16:
        challengecounter = 0

    attemptcounter = -1
    address = 0

    attemptleds = [0,0,0]

    while True:

        stdinstatus = uselect.select([sys.stdin], [], [], 0.01)
        if stdinstatus[0]:
            inputstring = sys.stdin.read(1)
            if inputstring == "?":
                print("The challenge-response game. The challenge is in the bottom row")
                print("Put in your answer using the A0 to A7, the game continues when you get it right")
                print("If you require a hint, press h\n")
                if bootstate == 5:
                    print("To return to the bootmenu, press q\n")
            elif inputstring == "h":
                pass
            elif inputstring == "q" and bootstate == 5:
                print("Resetting bootstate")
                eeprom.writeto_mem(80, 42, b'\x2A',addrsize=eepromsize)
                break
            else:
                print("The challenge-response game. The challenge is in the bottom row")
                print("Put in your answer using the A0 to A7, the game continues when you get it right")
                print("If you require a hint, press h\n")
                if bootstate == 5:
                    print("To return to the bootmenu, press q\n")
                print(f"Challenge No: {challengecounter+1}, Attempt: {attemptcounter}, Challenge: {randno:08b}\n")


        if time.ticks_diff(time.ticks_ms(), ledtimer) > 0:
            if statusled == True:
                if runningonbattery == False:
                    ledRGB('GREEN', not runningonbattery)
                    ledtimer = time.ticks_add(time.ticks_ms(), 300)
                else:
                    ledRGB('GREEN', not runningonbattery)
                    ledtimer = time.ticks_add(time.ticks_ms(), 100)
                statusled = False
            else:
                ledRGB('OFF', not runningonbattery)
                #print("Idle")
                statusled = True

                if runningonbattery == False:
                    ledtimer = time.ticks_add(time.ticks_ms(), 700)
                else:
                    ledtimer = time.ticks_add(time.ticks_ms(), 1900)
            #print("Led triggered")




        if time.ticks_diff(time.ticks_ms(), buttontimer) > 0:
            #print("Buttontrigger")

            btns = buttonstate(address, challengecounter+1, attemptleds[2], attemptleds[1], attemptleds[0])
            address = btns[0]
            if runningonbattery == False:
                buttontimer = time.ticks_add(time.ticks_ms(), 100)
            else:
                buttontimer = time.ticks_add(time.ticks_ms(), 200)
            if btns[5] == 1:
                buttontimer = time.ticks_add(time.ticks_ms(), 500)
                if runningonbattery == False:
                    idle = False
                else:
                    idletimer = time.ticks_add(time.ticks_ms(), 60000)


                
            if randno == 0:
                if attemptcounter < 2:
                    attemptcounter +=1
                else:
                    attemptcounter = 0
                    challengecounter +=1

                    writebuffer = bytearray(1)
                    writebuffer[0] = challengecounter

                    eeprom.writeto_mem(80, 1, writebuffer,addrsize=eepromsize)

                randno = challenges.games[challengecounter][0](0)
                if debug == True:
                    print(f"Challenge is {challenges.games[challengecounter][2]}")
                shiftregister(randno)
                print(f"Challenge No: {challengecounter+1}, Attempt: {attemptcounter}, Challenge: {randno:08b}")
                if debug == True:
                    print(f"Expected response: {challenges.games[challengecounter][0](randno):08b}")

                if attemptcounter == 0:
                    attemptleds = [0,0,1]
                elif attemptcounter == 1:
                    attemptleds = [0,1,0]
                elif attemptcounter == 2:
                    attemptleds = [1,0,0]
                else:
                    attemptleds = [0,0,0]

            if load.value() == 1 or inputstring == "h":
                inputstring = ""
                ledRGB('RED', not runningonbattery)
                print("The challenge was:             {:08b}".format(randno))
                print("The response should have been: {:08b}\n".format(challenges.games[challengecounter][0](randno)))
                shiftregister(randno)
                set_state(challenges.games[challengecounter][0](randno),challengecounter+1, attemptleds[2], attemptleds[1], attemptleds[0])
                time.sleep_ms(7000)
                randno = challenges.games[challengecounter][0](0)
                ledRGB('GREEN', not runningonbattery)
                shiftregister(randno)
                address = 0
                print(f"Challenge No: {challengecounter+1}, Attempt: {attemptcounter}, Challenge: {randno:08b}")
                if runningonbattery == True:
                    idletimer = time.ticks_add(time.ticks_ms(), 60000)
                

            if address != 0:
                if debug == True:
                    print(f"Expected response: {challenges.games[challengecounter][0](randno):08b} Current response {address:08b} {challenges.games[challengecounter][0](randno)} {address}\n")
                if address == challenges.games[challengecounter][0](randno):
                    print("Found challenge")
                    address = 0
                    

                    randno = 0
                    shiftregister(randno)

            if challengecounter > 14:
                #time.sleep_ms(1000)
                shiftregister(0)
                ledRGB('OFF', not runningonbattery)
                set_state(0,0,0,0,0)
                if common.get_state(122) == False:
                    common.update_state(122, eeprom)
                #Pin(BAT_ENPIN, Pin.IN) 
                break
        
        if idle == True and time.ticks_diff(time.ticks_ms(), idletimer) > 0:
            if runningonbattery or bootstate == 5:
                shiftregister(0)
                ledRGB('OFF', not runningonbattery)
                set_state(0,0,0,0,0)
                Pin(BAT_ENPIN, Pin.IN) 
                break

        if time.ticks_diff(time.ticks_ms(), uarttimer) > 0 and (bootstate == 5 or bootstate == 7):
            uarttimer = time.ticks_add(time.ticks_ms(), 10000)

            crocodileinput = uart.readline()
            #print(crocodileinput) 

            if common.get_state(13):

                if common.get_state(114) == False and crocodileinput == b"This is badge type 0\n":
                    common.update_state(114, eeprom)
                    print("Found type 0")
                elif common.get_state(115) == False and crocodileinput == b"This is badge type 1\n":
                    common.update_state(115, eeprom)
                    print("Found type 1")
                elif common.get_state(116) == False and crocodileinput == b"This is badge type 2\n":
                    common.update_state(116, eeprom)
                    print("Found type 2")
                elif common.get_state(117) == False and crocodileinput == b"This is badge type 3\n":
                    common.update_state(117, eeprom)
                    print("Found type 3")


            if common.get_state(110):
                uart.write(b"This is badge type 0\n")
            elif common.get_state(111):
                uart.write(b"This is badge type 1\n")
            elif common.get_state(112):
                uart.write(b"This is badge type 2\n")
            elif common.get_state(113):
                uart.write(b"This is badge type 3\n")

    
ledRGB([65000,0,0], not runningonbattery)

    


if bootstate == 0xFF:

    print("Starting BFSP, use frontpanel to input code. Press ? for help.")

    inputstring = ""
    halted = False
    ledoverride = False

    while 1:
        stdinstatus = uselect.select([sys.stdin], [], [], 0.01)
        if stdinstatus[0]:
            inputstring = sys.stdin.read(1)
            if inputstring == "?":
                print("""Welcome to the BFSP. 
Using this service processor you can execute rudimentary programs to perform system actions
                
D3 to D0 indicate the corrent instruction. 
A7 to A0 the current address. 
The address can be increased with STEP.
RUN will start the program.

The instructions are:
0b0000: NOP
0b0010: > Increment data pointer
0b0011: < Decrement data pointer
0b0100: + Increment data at data pointer
0b0101: - Decrement data at data pointer
0b0110: . Output data at data pointer
0b0111: , Input data at data pointer
0b1000: [ If data is zero, jump to ], else move to next instruction
0b1001: ] If data is zero, move to next instruction, else jump to previous [
0b1100: Reset
0b1110: Breakpoint, halts and increases address
0b1111: Stop

                """)
            else:
                print("Welcome to the BFSP. Press ? for help.\n")

        if time.ticks_diff(time.ticks_ms(), ledtimer) > 0 and ledoverride == False:
            if statusled == True:
                if runningonbattery == False and mem[address] != 0b1111:
                    ledRGB('BLUE', not runningonbattery)
                    ledtimer = time.ticks_add(time.ticks_ms(), 500)
                elif datamem[255] == 42 and mem[address] == 0b1111:
                    ledRGB('GREEN', not runningonbattery)
                    ledtimer = time.ticks_add(time.ticks_ms(), 100)
                else:
                    ledRGB('RED', not runningonbattery)
                    ledtimer = time.ticks_add(time.ticks_ms(), 100)
                statusled = False
            else:
                ledRGB('OFF', not runningonbattery)
                #print("Idle")
                statusled = True

            if runningonbattery == False:
                ledtimer = time.ticks_add(time.ticks_ms(), 500)
            else:
                ledtimer = time.ticks_add(time.ticks_ms(), 1900)
            #print("Led triggered")

        if datamem[254] > 0 or datamem[253] > 0 or datamem[252] > 0:
            ledRGB([datamem[252]*256,datamem[253]*256,datamem[254]*256], not runningonbattery)
            ledoverride = True
        else:
            ledoverride = False

        if time.ticks_diff(time.ticks_ms(), buttontimer) > 0:
            btns = buttonstate(address,mem[address],running,btns[3],btns[4])
            mem[address] = btns[1]
            address = btns[0]

            if running == False and btns[2] == True:
                running = True
                if halted == False:
                    address = 0
                    datapointer = 0
                else:
                    halted = False
                print("Switch to running")
            elif running == True and btns[2] == True:
                running = False
                print("Stopping")

            if btns[3]:
                address +=1
                if address > 255:
                    address = 0

            if btns[4]:
                mem = [0]*256
                datamem = [0]*256
                datapointer = 0
                address = 0
                loopcounter = 0
                running = False

                mem = memory.memory

                #f = open("mem.b", "rt")

                #i=0
                #for line in f:
                #    if i < 256:
                #        mem[i] = int(line)
                #    i+=1


            #if load.value() == 1:
            #    shiftdata = shiftregister(0b01011011)
            #    print("{:08b}".format(shiftdata))
            #    btns[5] == True

            #print(btns)
            if btns[5] == False and running == False:
                if runningonbattery == False:    
                    buttontimer = time.ticks_add(time.ticks_ms(), 100)
                else:
                    buttontimer = time.ticks_add(time.ticks_ms(), 500)
            elif btns[5] == False and running == True:
                if runningonbattery == False:    
                    buttontimer = time.ticks_add(time.ticks_ms(), 20)
                else:
                    buttontimer = time.ticks_add(time.ticks_ms(), 200)
                buttonstate(address,mem[address],running,btns[3],btns[4])

                #b0000: NOP
                if mem[address] == 0b0000:
                    address +=1

                #0b0010: > Increment data pointer
                elif mem[address] == 0b0010:
                    datapointer +=1
                    address +=1

                #0b0011: < Decrement data pointer
                elif mem[address] == 0b0011:
                    datapointer -=1
                    address +=1

                #0b0100: + Increment data at data pointer
                elif mem[address] == 0b0100:
                    datamem[datapointer] +=1
                    address +=1

                #0b0101: - Decrement data at data pointer
                elif mem[address] == 0b0101:
                    datamem[datapointer] -=1
                    address +=1

                #0b0110: . Output data at data pointer
                elif mem[address] == 0b0110:
                    shiftregister(datamem[datapointer])
                    buttontimer = time.ticks_add(time.ticks_ms(), 1000)
                    address +=1

                #0b0111: , Input data at data pointer
                elif mem[address] == 0b0111:
                    loadpressed = False
                    while loadpressed == False:
                        if load.value() == 1:
                            loadpressed = True
                        ledRGB('RED', not runningonbattery)
                        time.sleep(0.1)
                        ledRGB('OFF', not runningonbattery)
                        time.sleep(0.2)
                    
                    datamem[datapointer] = shiftregister()
                    address+=1

                #0b1000: [ If data is zero, jump to ], else move to next instruction
                elif mem[address] == 0b1000:
                    if datamem[datapointer] != 0:
                        address +=1
                    else:
                        foundloop = False
                        while foundloop == False:
                            address += 1
                            buttonstate(address,mem[address],running,btns[3],btns[4])
                            print("Address: {:08b} mem: {:08b} loopcounter: {}".format(address, mem[address], loopcounter))
                            if mem[address] == 0b1001 and loopcounter == 0:
                                foundloop = True
                            elif mem[address] == 0b1001 and loopcounter != 0:
                                loopcounter -=1
                            elif mem[address] == 0b1000:
                                loopcounter +=1

                #0b1001: ] If data is zero, move to next instruction, else jump to previous [
                elif mem[address] == 0b1001:
                    if datamem[datapointer] == 0:
                        address +=1
                    else:
                        foundloop = False
                        while foundloop == False:
                            address -=1
                            if mem[address] == 0b1000 and loopcounter == 0:
                                foundloop = True
                            elif mem[address] == 0b1000 and loopcounter != 0:
                                loopcounter -=1
                            elif mem[address] == 0b1001:
                                loopcounter +=1

                #0b1100: Reset
                elif mem[address] == 0b1100:
                    mem = [0]*256
                    datamem = [0]*256
                    datapointer = 0
                    address = 0
                    loopcounter = 0
                    running = False


                #0b1110: Breakpoint, halts and increases address
                elif mem[address] == 0b1110:
                    address +=1
                    running = False
                    halted = True
                    
                #0b1111:   Stop
                elif mem[address] == 0b1111:
                    running = False
                    if runningonbattery == True:
                        set_state(0,0,0,0,0)
                        Pin(BAT_ENPIN, Pin.IN)
                    
                    if datamem[255] == 42:
                        eeprom.writeto_mem(80, 42, b'\x2A',addrsize=eepromsize)
                        time.sleep_ms(1000)
                        if common.get_state(124) == False:
                            common.update_state(124, eeprom)
                        break

                if address > 255:
                    address = 0
                elif address < 0:
                    address = 255

                if datapointer > 255:
                    datapointer = 0
                elif datapointer < 0:
                    datapointer = 255

                if datamem[datapointer] > 255:
                    datamem[datapointer] -= 256
                elif datamem[datapointer] < 0:
                    datamem[datapointer] += 256
                
            else:
                buttontimer = time.ticks_add(time.ticks_ms(), 500)

        #ledG.value(-btns[2])

if bootstate == 7:
    if runningonbattery:
        ledRGB([65000,0,0], not runningonbattery)
        for i in range(50):
            set_state(0,0,0,0,1)
            time.sleep_ms(100)
            set_state(0,0,0,0,0)
            time.sleep_ms(100)
    else:
        if eeprom.readfrom_mem(80, 43, 1, addrsize=eepromsize)[0] == 255:
            print("Initializing")
            random.seed()
            badge = random.randint(1, 254)
            eeprom.writeto_mem(80, 43, b'\x00',addrsize=eepromsize)
            time.sleep_ms(1000)
        else:
            badge = 0

        ledRGB([10000,0,10000], not runningonbattery)
        game.game(eeprom,badge)
        eeprom.writeto_mem(80, 42, b'\x2A',addrsize=eepromsize)

if bootstate == 42 or bootstate == 5:
    if runningonbattery != True:

        ledRGB([65000,10000,0], not runningonbattery)
        set_state(0,0,0,0,1)

        validcommand = False


        while validcommand == False:
            print("""Boot menu
        1. Factory reset
        2. Set name
        3. Boot into BFSP
        4. Start Adventure\n
        5. Return to Challenge Response game\n""")

            command = input("?>")
            if command == "1":
                print("Resetting configuration memory\n")
                validcommand = True
                eeprom.writeto_mem(80, 0, b'\xFF',addrsize=eepromsize)
                time.sleep_ms(10)
                eeprom.writeto_mem(80, 1, b'\x00',addrsize=eepromsize)
                time.sleep_ms(10)
                for i in range(32):
                    eeprom.writeto_mem(80, i+2, b'\xFF',addrsize=eepromsize)
                    time.sleep_ms(10)
                eeprom.writeto_mem(80, 42, b'\xFF',addrsize=eepromsize)

            elif command == '2':
                while validcommand == False:
                    username = input("Input name > ")
                    if len(username) > 32:
                        print("Name is too long")
                    elif len(username) == 0:
                        print("Clearing name")
                        for i in range(32):
                            eeprom.writeto_mem(80, i+2, b'\xFF',addrsize=eepromsize)
                            time.sleep_ms(10)
                        time.sleep_ms(10)
                        validcommand = True
                    else:
                        print(f"Name is: {username}")
                        tmp = bytearray(1)
                        for i in range(32):
                            eeprom.writeto_mem(80, i+2, b'\xFF',addrsize=eepromsize)
                            time.sleep_ms(10)
                        for i in range(len(username)):
                            username = bytes(username, 'ascii')
                            tmp[0] = username[i]
                            eeprom.writeto_mem(80,i+2,tmp,addrsize=eepromsize)
                            time.sleep_ms(10)
                        validcommand = True
                        time.sleep_ms(10)

            elif command == '3':
                print("Setting bootoption for BFSP\n")
                eeprom.writeto_mem(80, 42, b'\xFF',addrsize=eepromsize)
                validcommand = True
            elif command == '4':
                print("Setting bootoption for Adventure\n")
                eeprom.writeto_mem(80, 42, b'\x07',addrsize=eepromsize)
                validcommand = True
            elif command == '5':
                print("Rebooting into guessing game. Leave idle for 30 seconds to return to this menu\n")
                eeprom.writeto_mem(80, 42, b'\x05',addrsize=eepromsize)
                validcommand = True
            else:
                print("Invalid command\n")

    else:
        ledRGB([65000,0,0], not runningonbattery)
        for i in range(50):
            set_state(0,0,0,0,1)
            time.sleep_ms(50)
            set_state(0,0,0,0,0)
            time.sleep_ms(50)


print("Resetting in 2 seconds, Bye")
time.sleep_ms(2000)        

machine.soft_reset()
