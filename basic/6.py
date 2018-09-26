#!/usr/bin/env python

a = b =c = 1;
print a
print b
print c

a, b, c = 2, 3, 'pengxu'
print a,; print b,; print c

hello = "hello world"
print hello[2:] + 'fuck'

list1 = ['pengxu', 4, 5.0, 56+4j]
list2 = ['px', 5, 666.0, 6e+4j]
print list1
print list1[3]
print list1[2:]

list3 = list1 + list2;
list4 = list2 * 3
print list3;

print list4

#t = 1e+0.5j
t = complex(1,0.5j)
print t


dict = {}
dict['px'] = 'peng xu'
dict[23] = 23;

other_dict = {'dcy':"dengchunyan", 'number':444, 45:'46'}

print dict
print other_dict

print dict['px']

print dict.keys()
print dict.values()

print other_dict.keys()
print other_dict.values()


