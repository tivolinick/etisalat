list1=['1','2','3','4','5','','','8']
joinit=[item for item in list1 if item != '']
print(list1)
print(joinit)
str1=' '.join(list1)
print(str1)
str2=' '.join([item for item in list1 if item != ''])
print(str2)
