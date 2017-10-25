def ssn_parser(ssn):
    front, back = ssn.split('-')
    sex = back[0]

    if sex == '1' or sex == '2':
        year = '19' + front[:2]
    else:
        year = '20' + front[:2]

    if (int(sex) % 2) == 0:
        sex = '여성'
    else:
        sex = '남성'

    month = front[2:4]
    day = front[4:6]

    return year, month, day, sex
