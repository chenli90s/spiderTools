


def main(stri):
    ss = stri.split("?")
    param = ss[1].split("&")
    pdict = {}
    for p in param:
        mm = p.split('=')
        # print(mm[0], mm[1])
        pdict[mm[0]] = mm[1]
    return pdict


if __name__ == '__main__':
    # p1 = main(str1)
    # p2 = main(str2)
    # p2 = main(str2)
    # for key, value in p1.items():
    # 	if p2[key] != value:
    # 		print("1", key, value)
    # 		print("2", key, p2[key])
    print(main(str3))
