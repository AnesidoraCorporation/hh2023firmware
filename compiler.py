#code = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
code = "++++++[>+++++++[-<<+>>]<-]<.|"

mem = [0]*256

f = open("memory.py", "wt")

f.write("memory = [\n")

for i in range(len(code)):
    if code[i] == ">":
        mem[i] = 0b0010
        #f.write("{},\n".format(0b0010))
        print("○○●○")
    elif code[i] == "<":
        mem[i] = 0b0011
        #f.write("{},\n".format(0b0011))
        print("○○●●")
    elif code[i] == "+":
        mem[i] = 0b0100
        #f.write("{},\n".format(0b0100))
        print("○●○○")
    elif code[i] == "-":
        mem[i] = 0b0101
        #f.write("{},\n".format(0b0101))
        print("○●○●")
    elif code[i] == ".":
        mem[i] = 0b0110
        #f.write("{},\n".format(0b0110))
        print("○●●○")
    elif code[i] == ",":
        mem[i] = 0b0111
        #f.write("{},\n".format(0b0111))
        print("○●●●")
    elif code[i] == "[":
        mem[i] = 0b1000
        #f.write("{},\n".format(0b1000))
        print("●○○○")
    elif code[i] == "]":
        mem[i] = 0b1001
        #f.write("{},\n".format(0b1001))
        print("●○○●")
    elif code[i] == "|":
        mem[i] = 0b1111
        #f.write("{},\n".format(0b1111))
        print("●●●●")

for pos in mem:
    f.write(f"{pos},\n")

f.write("0]\n")
f.close()