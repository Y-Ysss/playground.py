import struct

a = 0b1
b = 0b1
c = 0b0

extended_optional_flag = (a << 15) | (b << 14) | (c << 13)
d = struct.pack('>H', extended_optional_flag)
print(d)
e = struct.unpack('>H', d)[0]
rsvflg = (e >> 15) & 0x01
skpflg = (e >> 14) & 0x01
addflg = (e >> 13) & 0x01

print(rsvflg, skpflg, addflg)


f =g =h =0
print(f,g,h)