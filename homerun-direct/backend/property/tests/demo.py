string="sampath"
dict={}
for char in string:
    if char in dict:
        dict[char]+=1
    else:
        dict[char]=1
print(dict)
    