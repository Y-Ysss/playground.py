import sqlite3

if __name__ == '__main__':

    con = sqlite3.connect(':memory:')
    cur = con.cursor()
    cur.execute('create table T1 (c1, c2, c3)')

    for i in range(1,10):
        cur.execute('insert into T1 values (?, ?, ?)', (i, i*i, 'fhwefhiufhwohfwuehfwoihfeuiwhfuiowheufhwoeuifhweuhfoweuhfuwiehfuiwehfweuifhuewhfwueihfwe'))

    rows = cur.execute('select * from T1')

    print('Output')
    for row in rows:
        print('{0}*{0}={1}'.format(row[0], row[1]))
        print(f'{row[0]}*{row[0]}={row[1]}')
    
    # print(rows.fetchone())

    # print('---')

    # for row in rows.fetchmany(3):
    #     print(row)

    # print('---')

    # for row in rows.fetchall():
    #     print(row)

    con.close()


"""
Output
(1, 1)
---
(2, 4)
(3, 9)
(4, 16)
---
(5, 25)
(6, 36)
(7, 49)
(8, 64)
(9, 81)
"""