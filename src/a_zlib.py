import zlib

with open('data/zlib/index', mode='rb') as f:
    data = f.read()
decompressed = zlib.decompress(zlib.compress(data))
print(decompressed) # b'test data\x00'