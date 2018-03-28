import club
import country

italia = country.Country('ITA')
juventus = club.Club('Juventus', italia)

print(juventus.name, juventus.country)

with open('results.csv', 'r', encoding='UTF-8') as f:
    for el in range(79, 98):
        print(repr(f.readline(el)))