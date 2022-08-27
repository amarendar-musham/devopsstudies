## 3 columns in a stdout = pid cpu process_name
## find out max cpu 
## what is the pid of it. 

import sys
ls=[]
f = open("test.txt","w")
for line in sys.stdin:
    ls=line.split()
    pid=ls[0]
    cpu=ls[1]
    
    f.write(pid + " " + cpu + "\n")
    

f = open("test.txt","r")
# print(f.read())
lst=[]

for line in f:
    lst.append([int(x) for x in line.split()])
#print(lst)
plist=[ x[0] for x in lst ]
clist=[ x[1] for x in lst ]

#print(plist)
#print(clist)
#print(max(clist))
#print(clist.index(max(clist)))
print(plist[clist.index(max(clist))])
