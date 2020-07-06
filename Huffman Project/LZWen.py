# refer https://www.runoob.com/w3cnote/python-lzw.html

f = open(r'd.md','r')
string = str(f.readlines())


dicts = {chr(i):i for i in range(0,127)}
 
last = 256
p = ''
result = []
 
for c in string:
    pc = p+c
    if pc in dicts:
        p = pc
    else:
        result.append(dicts[p])
        dicts[pc] = last
        last += 1
        p = c
 
if p != '':
    result.append(dicts[p])
 
print(result)

o= open(r'd.md.lzw','w')
o.write(str(result))