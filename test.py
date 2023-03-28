l = ['bmw\n', 'mercedes\n', 'ford\n', 'honda\n', 'lexus']

x = open('1.txt', mode='w')
x.writelines(l)
x.close()

x = open('1.txt', mode='r')
t = x.readlines()
x.close()

print(type(t))
print(t)

with open('1.txt', mode='r') as f:
    t = f.readlines()

# https://pythonworld.ru/tipy-dannyx-v-python/fajly-rabota-s-fajlami.html
