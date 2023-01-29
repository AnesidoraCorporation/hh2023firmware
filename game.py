#!/usr/bin/env python3

from common import *
#from literals import *
#import argparse

#import pkg_resources
import gamedata
import ubinascii
import uselect
import sys
import time

from hh2022 import set_state, ledRGB, shiftregister
from machine import Pin, UART

SAOSDAPIN       = 26
SAOSCLPIN       = 27

global inventory
global current_effects

def game(eepromstate, badge):

    DEBUG = False

    read_state(eepromstate)

    if badge != 0:
        if badge % 4 == 0:
            update_state(110,eepromstate)
        elif badge % 4 == 1:
            update_state(111,eepromstate)
        elif badge % 4 == 2:
            update_state(112,eepromstate)
        elif badge % 4 == 3:
            update_state(113,eepromstate)

    GOOD = Pin(SAOSDAPIN, Pin.IN)
    EVIL = Pin(SAOSCLPIN, Pin.IN)

    uart = UART(0, baudrate=300, bits=8, parity=None, stop=1, tx=Pin(28), rx=Pin(29))

    ### Read the EEPROM data
    #f = pkg_resources.resource_stream(__name__, "hotel.bin")
    #with open('hotel.bin', 'rb') as f:
    #eeprom = f.read()
    eeprom = ubinascii.a2b_base64(gamedata.gamedata)

    ### Start of the game
    loc             = []
    loc_offset,loc_action_mask,loc_children,loc_parent = loc2offset(eeprom,loc)
    current_effects = read_byte_field(eeprom,loc_offset,'effects')
    inventory = []

    inputstring = ""
    initgame = True
    victorytimer = time.ticks_add(time.ticks_ms(), 100)
    victorycounter = 0
    victoryeffect = 0
    effecttimer = time.ticks_add(time.ticks_ms(), 500)
    effectcounter = 0
    uarttimer = time.ticks_add(time.ticks_ms(), 10000)
    iostate_old = 0
    iotimer = time.ticks_add(time.ticks_ms(), 1000)
    tmp = 0

    while True:

        # Some LED effects for finishing the adventure :-)
        if time.ticks_diff(time.ticks_ms(), victorytimer) > 0 and get_state(127):
            victorytimer = time.ticks_add(time.ticks_ms(), 100)
            victorycounter += 1
            if victorycounter % 50 == 0:
                victoryeffect += 1
                if victoryeffect > 2:
                    victoryeffect = 0
                
            if victoryeffect == 0:
                # circle
                x = 3 << (victorycounter % 15)
                x = (x & 32767) + (x >> 15)

                tmp = x >> 8
                x = x & 255
                for i in range(7):
                    if i<4:
                        x = x + ((tmp & 1) << (15 - i))
                    else:
                        x = x + ((tmp & 1) << (14 - i))
                    tmp = tmp >> 1

            elif victoryeffect == 1:
                # flash
                x = 0xffff * ((victorycounter >> 2) & 1)

            elif victoryeffect == 2:
                # rotate right
                x = 0x8080 >> ( victorycounter % 8 ) 

            set_state(x&255,x>>12,(x>>10)&1,(x>>9)&1,(x>>8)&1)


        if get_state(114) and get_state(115) and get_state(116) and get_state(117) and get_state(125) == False:
            update_state(125, eepromstate)

        if time.ticks_diff(time.ticks_ms(), uarttimer) > 0:
            uarttimer = time.ticks_add(time.ticks_ms(), 10000)

            crocodileinput = uart.readline()
            #print(crocodileinput) 

            if get_state(13):
                if get_state(114) == False and crocodileinput == b"This is badge type 0\n":
                    update_state(114, eepromstate)
                elif get_state(115) == False and crocodileinput == b"This is badge type 1\n":
                    update_state(115, eepromstate)
                elif get_state(116) == False and crocodileinput == b"This is badge type 2\n":
                    update_state(116, eepromstate)
                elif get_state(117) == False and crocodileinput == b"This is badge type 3\n":
                    update_state(117, eepromstate)


            if get_state(110):
                uart.write(b"This is badge type 0\n")
            elif get_state(111):
                uart.write(b"This is badge type 1\n")
            elif get_state(112):
                uart.write(b"This is badge type 2\n")
            elif get_state(113):
                uart.write(b"This is badge type 3\n")

        if time.ticks_diff(time.ticks_ms(), iotimer) > 0 and get_state(127) == False:

            if get_state(18):

                if get_state(120) == False and EVIL.value() == True:
                    update_state(120, eepromstate)

                if get_state(121) == False and GOOD.value() == True:
                    update_state(121, eepromstate)

                if get_state(127) == False:
                    # Set state 118 if the evil spirit was released first
                    if get_state(118) == False and get_state(119) == False and get_state(120):
                        update_state(118, eepromstate)
                    
                    # Set state 119 if the evil spirit was released first
                    if get_state(118) == False and get_state(119) == False and get_state(121):
                        update_state(119, eepromstate)

                    # When both lines are cut in the right order, set the winner state
                    # Also clear state 119 to make the good spirit disappear again :-)
                    if get_state(119) and get_state(120):
                        update_state(128+119, eepromstate)
                        update_state(127, eepromstate)


            iostate = 0
            if get_state(120):
                iostate = iostate | 0b10000000 # Evil trace cut
            if get_state(121):
                iostate = iostate | 0b01000000 # Good trace cut
            if get_state(122):
                iostate = iostate | 0b00100000 # Challenge Response game
            if get_state(123):
                iostate = iostate | 0b00010000 # Location Game

            if get_state(124):
                iostate = iostate | 0b00001000 # Punch tape entered
            if get_state(125):
                iostate = iostate | 0b00000100 # 4 badges connected
            if get_state(126):
                iostate = iostate | 0b00000010 # Part 1 done
            if get_state(127):
                iostate = iostate | 0b00000001 # Part 2 done

            if iostate != iostate_old:
                shiftregister(iostate)
                iostate_old = iostate

            badgestate = 0
            if get_state(117):
                badgestate = badgestate | 0b00001000 # Seen badge 3
            if get_state(116):
                badgestate = badgestate | 0b00000100 # Seen badge 2
            if get_state(115):
                badgestate = badgestate | 0b00000010 # Seen badge 1
            if get_state(114):
                badgestate = badgestate | 0b00000001 # Seen badge 0

            set_state(0,badgestate,0,0,0)


            
            iotimer = time.ticks_add(time.ticks_ms(), 1000)

        # The effects should be triggered, so no need to print them I think, unless we want to
        # maybe print the sound effect for those that do not use earplugs ;-)
        #if current_effects != 0:
            #print("There is an effect:")
        #    print(s(eeprom,'SPACE') + "{}".format(effects(current_effects)))
        #    if time.ticks_diff(time.ticks_ms(), effecttimer) > 0:
        #        effecttimer = time.ticks_add(time.ticks_ms(), 500)
        #        if current_effects[1] == "<none>":
        #            effectcounter += 1

        #            if effectcounter % 1:
        #                ledRGB([65500,65500,65500])
        #            else:
        #                ledRGB("OFF")

        #else:
        #    effectcounter = 0
        #    set_state(0,0,1,0,0)
        #    ledRGB("OFF")

        # Start with getting user input

        #inp = input(s(eeprom,'PROMPT'))
        stdinstatus = uselect.select([sys.stdin], [], [], 0.01)
        if stdinstatus[0]:
            inputstring += sys.stdin.read(1)
            print(inputstring[-1], end="")

        if len(inputstring) > 100:
            print("Input too long!")
            inputstring = ""
        elif (len(inputstring) > 0 and inputstring[-1] == "\n") or initgame == True:
            initgame = False
            
            inp = inputstring[:-1]
            inputstring = ""

            if len(inp) == 0:
                pass
            else:

                inp = inp.lower().split()
                cmd = inp[0][0]


                if cmd == 'h' or cmd == '?':
                    show_help(eeprom)



            ####################
            # not needed in FW #
            # vv from here  vv #
            ####################

                elif inp[0] == "t)gg!#_d3bu9":
                    DEBUG = not DEBUG
                    print("Debugging: {}".format(DEBUG))

                elif DEBUG and inp[0] == "tree":
                    print_tree(eeprom,[],loc,0,inventory)


                elif DEBUG and cmd == 's':
                    if len(inp) > 1:
                        update_state(int(inp[1]),eepromstate)
                    print("The game state is now:")
                    for i in range(status_bits//8):
                        print("0x{:02X}:{:08b}".format(i,game_state[i]))


                elif cmd == 'i':
                    if DEBUG:
                        if len(inp) == 3:
                            inventory = [[int(inp[1]),inp[2]]]
                    print("Inventory is now {}".format(inventory))


            ####################
            # ^^  to here   ^^ #
            ####################



                elif cmd == 'q':
                    print(s(eeprom,'QUIT'))
                    break


                elif cmd == 'l':
                    if len(inp) == 1:
            #            print(read_string_field(eeprom,loc_offset,'desc'))
            #            print(s(eeprom,'LOOK'),end='')
            #            sep = ""
            #            if loc_parent[1] != 0xffff and object_visible(eeprom,loc_parent[1]):
            #                name = read_string_field(eeprom,loc_parent[1],'name')
            #                print("{}".format(name),end='')
            #                sep = s(eeprom,'COMMA')
            #            for i in range(len(loc_children)):
            #                if object_visible(eeprom,loc_children[i][1]):
            #                    item = read_byte_field(eeprom,loc_children[i][1],'item_nr')
            #                    in_inventory = False
            #                    if item != 0:
            #                        for inv in range(len(inventory)):
            #                            if item == inventory[inv][0]:
            #                                in_inventory = True
            #                                break
            #                    if  not in_inventory:
            #                        name = read_string_field(eeprom,loc_children[i][1],'name')
            #                        print("{}{}".format(sep,name),end='')
            #                        sep = s(eeprom,'COMMA')
            #            print()
                        look_around(eeprom, loc_offset, loc_parent, loc_children,inventory)

                    else:
                        look_offset = 0xffff
                        for i in range(len(loc_children)):
                            if object_visible(eeprom,loc_children[i][1]):
                                if inp[1] == loc_children[i][0]:
                                    look_offset = loc_children[i][1]
                                    break
                        else:
                            if object_visible(eeprom,loc_parent[1]):
                                if inp[1] == loc_parent[0]:
                                    look_offset = loc_parent[1]
                                else:
                                    print(s(eeprom,'DONTSEE'))
                                    #continue
                        if look_offset != 0xffff:
                            if (read_byte_field(eeprom,look_offset,'action_mask') & A_LOOK == 0):
                                name = read_string_field(eeprom,look_offset,'name')
                                print(s(eeprom,'CANTLOOK') + "{}".format(name))
                                #continue
                            else:
                                desc = read_string_field(eeprom,look_offset,'desc')
                                print(desc)
                                #continue
                        else:
                            invalid(eeprom)

                        
                elif cmd == 'x':
                    exit_allowed = False
                    if len(loc) == 0:
                        invalid(eeprom)
                    elif len(loc) == 1:
                        msg = check_open_permission(eeprom,0)
                        if msg != "":
                            print(msg)
                        else:
                            exit_allowed = True
                    else:
                        exit_allowed = True

                    if exit_allowed:
                        del loc[-1]
                        loc_offset,loc_action_mask,loc_children,loc_parent = loc2offset(eeprom,loc)
                        current_effects = read_byte_field(eeprom,loc_offset,'effects')


                elif cmd == 'e' or cmd == 'o':
                    if len(inp) != 2:
                        invalid(eeprom)
                    else:
                        enter_offset = 0xffff
                        for i in range(len(loc_children)):
                            if object_visible(eeprom,loc_children[i][1]):
                                if inp[1][0] == loc_children[i][0]:
                                    enter_offset = loc_children[i][1]
                                    break
                        else:
                            if object_visible(eeprom,loc_parent[1]):
                                if inp[1][0] == loc_parent[0]:
                                    enter_offset = loc_parent[1]

                        if enter_offset != 0xffff:
                            enter_action_mask = read_byte_field(eeprom,enter_offset,'action_mask')
                            if cmd == 'e' and (enter_action_mask & A_ENTER == 0):
                                print(s(eeprom,'CANTENTER'))
                                #continue
                            elif cmd == 'o' and (enter_action_mask & A_OPEN == 0):
                                print(s(eeprom,'CANTOPEN'))
                                #continue
                            else:
                                msg = check_open_permission(eeprom,enter_offset)
                                if msg != "":
                                    print(msg)
                                    #continue
                                else:
                                    if enter_offset != loc_parent[1]:
                                        loc.append(i)
                                    else:
                                        del(loc[-1])
                                    loc_offset,loc_action_mask,loc_children,loc_parent = loc2offset(eeprom,loc)
                                    current_effects = read_byte_field(eeprom,loc_offset,'effects')
                                    look_around(eeprom, loc_offset, loc_parent, loc_children,inventory)
                                    #continue
                        else:
                            print(s(eeprom,'DONTSEE'))


                elif cmd == 't' or cmd == 'u' or cmd == 'g' or cmd == 'r':
                    if len(inp) < 2 or len(inp)>3:
                        invalid(eeprom)
                    else:
                        item = 0
                        if len(inp) == 2:
                            obj  = inp[1][0]
                        elif len(inp) == 3:
                            item = -1
                            obj  = inp[2][0]
                            for i in range(len(inventory)):
                                if "["+inp[1][0]+"]" in inventory[i][1].lower():
                                    item = inventory[i][0]
                                    break
                            else:
                                print(s(eeprom,'NOTCARRYING'))
                                #continue

                        if item >= 0:
                            obj_offset = 0xffff
                            for i in range(len(loc_children)):
                                if object_visible(eeprom,loc_children[i][1]):
                                    if obj == loc_children[i][0]:
                                        obj_offset = loc_children[i][1]
                                        break
                            else:
                                if object_visible(eeprom,loc_parent[1]):
                                    if obj == loc_parent[0]:
                                        obj_offset = loc_parent[1]

                            if obj_offset == 0xffff:
                                if cmd == 'u' or cmd == 'r':
                                    print(s(eeprom,'NOSUCHOBJECT'))
                                else:
                                    print(s(eeprom,'NOSUCHPERSON'))
                                #continue
                            else:
                                obj_action_mask = read_byte_field(eeprom,obj_offset,'action_mask')
                                msg = check_action_permission(eeprom,obj_offset)
                                request = read_string_field(eeprom,obj_offset,'action_str1')
                                if cmd == 't' and (obj_action_mask & A_TALK == 0):
                                    print(s(eeprom,'WHYTALK') + "{}".format(read_string_field(eeprom,obj_offset,'name')))
                                    #continue
                                elif cmd == 'u' and (obj_action_mask & A_USE == 0):
                                    print(s(eeprom,'CANTUSE'))
                                    #continue
                                elif cmd == 'g' and (obj_action_mask & A_GIVE == 0):
                                    print(s(eeprom,'CANTGIVE'))
                                    #continue
                                elif cmd == 'r' and (obj_action_mask & A_READ == 0):
                                    print(s(eeprom,'CANTREAD'))
                                    #continue
                                elif msg != "":
                                    print(msg)
                                    #continue
                                else:
                                    if len(request) == 1:
                                        if request == '1':
                                            pass
                                        else:
                                            print("Undefined challenge!")
                                            #continue
                                    elif cmd == 'u' and read_byte_field(eeprom,obj_offset,'action_item') != item:
                                        if item == 0:
                                            print(s(eeprom,'CANTUSE'))
                                        else:
                                            print(s(eeprom,'CANTUSEITEM'))
                                        #continue
                                    elif cmd == 'g' and item != 0 and read_byte_field(eeprom,obj_offset,'action_item') != item:
                                        print(s(eeprom,'CANTGIVE'))
                                        #continue
                                    else:
                                        skip = False
                                        if len(request) > 1:
                                            print("{}".format(request))
                                            response = input(s(eeprom,'RESPONSE'))
                                            if unify(read_string_field(eeprom,obj_offset,'action_str2')) != unify(response):
                                                print(s(eeprom,'INCORRECT'))
                                                time.sleep_ms(10000)
                                                skip = True
                                                #continue
                                        if not skip:
                                            update_state(read_byte_field(eeprom,obj_offset,'action_state'),eepromstate)
                                            print("{}".format(read_string_field(eeprom,obj_offset,'action_msg')))

                    
                elif cmd == 'p':
                    if len(inventory) >= 2:
                        print(s(eeprom,'CARRYTWO'))
                        
                    elif len(inp) != 2:
                        invalid(eeprom)

                    else:
                        obj_offset = 0xffff
                        for i in range(len(loc_children)):
                            if object_visible(eeprom,loc_children[i][1]):
                                if inp[1] == loc_children[i][0]:
                                    obj_offset = loc_children[i][1]
                                    break

                        if obj_offset == 0xffff:
                            print(s(eeprom,'NOSUCHOBJECT'))
                            #continue

                        else:
                            obj_id   = read_byte_field(eeprom,obj_offset,'item_nr')
                            if obj_id != 0:
                                obj_name = read_string_field(eeprom,obj_offset,'name')
                                if [obj_id,obj_name] in inventory:
                                    print(s(eeprom,'ALREADYCARRYING'))
                                else:
                                    msg = check_action_permission(eeprom,obj_offset)
                                    if msg != "":
                                        print(msg)
                                        #continue
                                    else:
                                        update_state(read_byte_field(eeprom,obj_offset,'action_state'),eepromstate)
                                        print("{}".format(read_string_field(eeprom,obj_offset,'action_msg')))
                                        print(s(eeprom,'NOWCARRING') + "{}".format(obj_name))
                                        inventory.append([obj_id,obj_name])
                            else:
                                invalid(eeprom)
                                

                elif cmd == 'd':
                    if len(inventory) == 0:
                        print(s(eeprom,'EMPTYHANDS'))
                        
                    elif len(inp) < 2:
                        invalid(eeprom)

                    else:
                        for i in range(len(inventory)):
                            if "["+inp[1][0]+"]" in inventory[i][1].lower():
                                print(s(eeprom,'DROPPING') + "{}".format(inventory[i][1]))
                                print(s(eeprom,'RETURNING'))
                                del inventory[i]
                                break
                        else:
                            print(s(eeprom,'NOTCARRYING'))


        ### end of command options

            if DEBUG:
                print("\nloc = {}".format(loc))
                print("effects = {}".format(current_effects))
                print("state = ",end="")
                for i in game_state:
                    print("{:08b},".format(i),end="")
                print()
                print("action_mask = {}".format(loc_action_mask))
                print("inventory = {}".format(inventory))
                print("offset = 0x{:04X}".format(loc_offset))
                print("children = {}".format(loc_children))
                print("eepromstate = ", end="")
                for i in eepromstate.readfrom_mem(80,64,16,addrsize=8):
                    print("{:08b},".format(i),end="")
                print()

            print(s(eeprom,'LOCATION') + "{}".format(read_string_field(eeprom,loc_offset,'name')))
            print("> ", end = "")
        
