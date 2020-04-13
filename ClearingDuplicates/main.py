import mysql.connector as mysql
from fuzzywuzzy import fuzz

def clear_prefix(res):
    res = res.replace('город', '')
    res = res.replace('Город', '')
    res = res.replace('г.', '')
    res = res.replace('Г.', '')

    res = res.replace('р.', '')
    res = res.replace('Р.', '')

    res = res.replace('село', '')
    res = res.replace('Cело', '')
    res = res.replace('с.', '')
    res = res.replace('С.', '')

    res = res.replace('п.', '')
    res = res.replace('П.', '')
    return res

def number_eq(x, y):
    tmp = [""] * 2
    for it in range(2):
        for ch in x:
            if (ch >= '0' and ch <= '9'):
                tmp[it] = tmp[it] + ch
        x, y = y, x
    return tmp[0] == tmp[1]

cities = {}
city_names = []

def init():
    db = mysql.connect(
        host = "localhost",
        user = "root",
        passwd = "(S#,c}pQvr5XY8jE",
        database = "inno"
    )

    cursor = db.cursor()
    cursor.execute("SELECT * FROM institution")


    rows = cursor.fetchall()

    for row in rows:
        if (row == None):
            continue
        arr_row = list(row)
        arr_row[2] = clear_prefix(arr_row[2])

        if arr_row[2][0] == ' ':
            arr_row[2] = arr_row[2][1:]
        if arr_row[2][0].isalpha():
            arr_row[2] = arr_row[2].capitalize()
        if (arr_row[2] in cities):
            cities[arr_row[2]].append(arr_row)
        else:
            city_names.append(arr_row[2])
            cities[arr_row[2]] = [arr_row]


def clear_city():
    db = mysql.connect(
        host = "localhost",
        user = "root",
        passwd = "",
        database = "countryDB"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM city")
    rows = cursor.fetchall()

    for i in range(len(city_names)):
        city = city_names[i]
        mx = 0
        name = ""
        for j in rows:
            if (mx <= fuzz.ratio(j[2].lower(), city.lower())):
                mx = fuzz.ratio(j[2].lower(), city.lower())
                name = j[2]
        if (mx >= 85):
            print(i, city, "--->", name, mx)
            tmp = cities[city]
            del cities[city]
            if (name in cities):
                cities[name] += tmp
            else:
                cities[name] = tmp
        else:
            del cities[city]
            print(i, city, "====/====", name, mx)


init()
clear_city()

ok = 0
for city in cities:
    mn = 0
    while True:
        ok = 0
        tmp = ("", "", "")
        for k1 in range(0, len(cities[city])):
            for k2 in range(0, len(cities[city])):
                i = cities[city][k1]
                j = cities[city][k2]
                if (k1 != k2 and fuzz.ratio(str(i[1]).lower(), str(j[1]).lower()) >= 60 and number_eq(i[1], j[1])):
                    if not ok:
                        mn = k1
                    ok = 1
                    if (len(tmp[1]) < len(i[1])):
                        tmp = i
                    if (len(tmp[1]) < len(j[1])):
                        tmp = j
                    #print(i[1], j[1])
            if (ok):
                break
        if (not ok):
            break
        print(tmp[1])
        toremove = []
        for i in cities[city]:
            if (fuzz.ratio(i[1].lower(), tmp[1].lower()) >= 60 and number_eq(tmp[1], i[1])):
                toremove.append(i)
        for elem in toremove:
            print(elem)
            cities[city].remove(elem)
        print("\n")
        print()
        print("{}%".format(int(1.0 * mn / (len(cities[city])+1) * 100)))
        cities[city].append(tmp)

f = open("output.sql", "w")
id = 1
db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "",
    database = "output"
)
cursor = db.cursor()

for city in cities:
    for i in cities[city]:
        i[1] = i[1].replace("\'", "\'\'")
        f.write("INSERT INTO institution (id, title, city) VALUES ({}, '{}', '{}');\n".format(id, i[1], city))

        sql = "INSERT INTO institution (id, title, city) VALUES (%s, %s, %s);"
        val = (id, i[1], city)
        cursor.execute(sql, val)
        id += 1
f.close()
db.commit()
