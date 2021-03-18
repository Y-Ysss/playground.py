import os, glob, hashlib



def get_hashlist(path):
    hashlist = {}
    for f in glob.glob(path):
        data = open(f, 'rb').read()
        hash = hashlib.sha1(os.path.basename(f).encode() + data).hexdigest()
        hashlist[hash] = os.path.basename(f)
    return hashlist



if __name__ == '__main__':
    hd = get_hashlist('data/hash_test_data/a/*')
    for h, f in hd.items():
        print(h, f)

    print('----')

    for h, f in get_hashlist('data/hash_test_data/b/*').items():
        print(h, f)
    print('----')

    print(hd.get('5eab4d9905ca2768b515fb525e535cff56098e57'))
    print(hd.get('7a969deb308df4aa9f3291f135f05769e6b9d848'))
    print(hd.get('1d09210ad7fdae4afa5f21f735815813a295bebf'))