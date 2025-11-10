import random

length = 100
choices = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 
           'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ' ', '\n', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

for i in range(length):
    print(random.choice(choices), end='')
