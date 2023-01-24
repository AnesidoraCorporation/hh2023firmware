#!/usr/bin/env python3

import random

def binprint(x):
    return format(x, 'b').zfill(8)

#repeat - repeat the pattern
def game_repeat(c):
    if c == 0:
        return random.randint(1, 254)

    return c

#invert - invert the pattern
def game_invert(c):
    if c == 0:
        return random.randint(1, 254)

    return c ^ 255

#lshift - shifted left 2 places
def game_lshift(c):
    if c == 0:
        return random.randint(1, 254)

    return (4 * c) % 256 + c//64

#rshift - shifted right 3 places
def game_rshift(c):
    if c == 0:
        return random.randint(1, 254)

    return (c % 8) * 32 + c//8

#reverse - put the pattern backwards
def game_reverse(c):
    if c == 0:
        return random.randint(1, 254)

    r = 0
    for i in range(8):
        r = 2 * r + (c % 2)
        c = c // 2
    return r

#nibbles - both nibbles backwards separately
def game_nibbles(c):
    if c == 0:
        return random.randint(1, 254)

    r1 = 0
    for i in range(4):
        r1 = 2 * r1 + (c % 2)
        c = c // 2
    r2 = 0
    for i in range(4):
        r2 = 2 * r2 + (c % 2)
        c = c // 2
    return 16 * r2 + r1

#xor - XOR 10010011
def game_xor(c):
    if c == 0:
        return random.randint(1, 254)

    return c ^ 147

#plus - add 35
def game_plus35(c):
    if c == 0:
        return random.randint(1, 254)

    return (c + 35) % 256

#five - multiply by 5
def game_five(c):
    if c == 0:
        return random.randint(1, 254)

    return (c * 5) % 256

#primes - Next prime
def game_primes(c):
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
              53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
              109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
              173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
              233, 239, 241, 251]

    if c == 0:
        return random.choice(primes[:-1])

    return primes[primes.index(c) + 1]

#13 - ROT13 a-z0-9!@#$%^&*()
def game_rot13(c):
    challenges = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    responses  = '0123456789NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'

    if c == 0:
        return ord(random.choice(list(challenges)))

    return ord(responses[list(challenges).index(chr(c))])


#14 - 1 letter naar rechts op toetsenbord
def game_keyboard(c):
    challenges = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    responses  = 'wertyuiopqsdfghjklaxcvbnmzWERTYUIOPQSDFGHJKLAXCVBNMZ'

    if c == 0:
        return ord(random.choice(list(challenges)))

    return ord(responses[list(challenges).index(chr(c))])

#15 - Een letter verder in de serie "HACKERhotel" waarbij MSB hoofd/klein wisseling aangeeft
def game_hh(c):
    challenges = 'hackerHOTEL'
    responses  = 'ackerHOTELh'

    if c == 0:
        return ord(random.choice(list(challenges))) + 128 * random.randint(0,1)

    return ord(responses[list(challenges).index(chr(c & 127))]) ^ ((c & 128) // 4)

#nibble_xor - XOR right 4 bits with the left 4 bits
def game_xor_nibble(c):
    if c == 0:
        return random.randint(1, 254)

    return c ^ (c // 16)

#xorshift - Xorshift x ^= x<<1
def game_xorshift(c):
    if c == 0:
        return random.randint(1, 254)

    return (c ^ (c<<1)) % 256

#multiply - Multiply left 4 bits with right 4 bits
def game_multiply(c):
    if c == 0:
        return random.randint(1, 254)

    return (c // 16) * (c % 16)



games = [[game_repeat,0,"Repeat"]
        ,[game_invert,0,"Invert"]
        ,[game_lshift,0,"Shift Left"]
        ,[game_rshift,0,"Shift Right"]
        ,[game_reverse,0,"Reverse"]
        ,[game_nibbles,0,"Reverse Nibles"]

        ,[game_xor,0,"XOR"]
        ,[game_plus35,0,"Add 35"]
        ,[game_five,0,"Times 5"]

        ,[game_primes,0,"Next prime"]
        ,[game_rot13,0,"ROT13"]
        ,[game_keyboard,0,"Keyboard shift"]
        ,[game_hh,0,"Hacker Hotel"]

        ,[game_xor_nibble,0]
        ,[game_xorshift,0]
        ]

if __name__ == "__main__":
  for game in range(len(games)):
      print(game)
      for i in range(3):
          challenge = games[game][0](0)
          print(binprint(challenge),binprint(games[game][0](challenge)))
      print()

  for i in range(3):
    challenge = games[game][0](0)
    response  = challenge
    for x in range(6):
      response = games[x][0](response)
      print("{} : {}".format(x,response))
    print("{} -> {}".format(challenge,response))
    print()
