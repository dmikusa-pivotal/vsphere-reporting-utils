
def convert_size(b):
    b = (b, 'bytes')
    kb = (b[0] / 1024.0, 'KB')
    mb = (kb[0] / 1024.0, 'MB')
    gb = (mb[0] / 1024.0, 'GB')
    tb = (gb[0] / 1024.0, 'TB')
    if kb[0] < 1.0:
        return "{:>7}{}".format(*b)
    elif mb[0] < 1.0:
        return "{:>7.2f}{}".format(*kb)
    elif gb[0] < 1.0:
        return "{:>7.2f}{}".format(*mb)
    elif tb[0] < 1.0:
        return "{:>7.2f}{}".format(*gb)
    else:
        return "{:>7.2f}{}".format(*tb)
