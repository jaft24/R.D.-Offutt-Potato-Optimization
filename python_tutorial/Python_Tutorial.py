#Here are some examples of using lists, dicts, and dataframes in python
'''
How to import an external library:
Syntax:
for entire lib:
import [library name]
for single module:
from [library module] import [function/class]
import the library and call it using a nickname:
import [library name] as [nickname]
'''
import pandas as pd
import numpy as np

'''
Pandas datafrmame:
Dataframes in python are objects of the Pandas library.
syntax: pd.DataFrame() creates an empty dataframe with 0 cols and 0 rows
'''
df = pd.DataFrame()

'''
lists and dictionaries (dict):
lists and dictionaries are a data type native to python that are useful
Lists are 0 indexed in python which means the index starts at 0 and ends at (list length - 1)
'''
#creating a list
listExample = [1, 2, 3, 4, 5]
listExample2 = [6, 7, 8, 9, 10]
#to append a value to a list:
listExample.append(0)
#to remove a value from a list:
listExample.remove(0) #removes value 0, but make sure the value does exist in the list otherwise an error occurs
'''
syntax to get an element from a list:
list[n] #returns the nth element from the list. Throws an error if equal or greater than the length of the list
'''
#get the length of a list:
len(listExample) #len() function returns the length of the list


#creating a ditionary
dictExample = {'list1': listExample,
               'list2': listExample2}
#this dictionary now has 2 keys: 'list1' and 'list2' which are keys for the values in the listExamples
#you can access these lists with the following syntax:
dictExample['list1']
dictExample['list2']
#this only returns the list you are speciifying.
#to return the keys of the dict, use the following syntax:
dictExample.keys()

#creating a dataframe from a dict:
df = pd.DataFrame(dictExample)
'''
when you create a dataframe from a dict, the keys become the column names and the lists contained in the
keys are the row values
'''
#return a column from a dataframe
df['list1']
#to return multiple cols
df[['list1', 'list2']]

'''
list comprehension:
list comprehension is a useful tool for returning a subset of a list, or applying a function to an entire list
This is the syntax:
'''
[x for x in listExample]
'''
the first x is what you will do to each element in the list, the second x after 'for' is identifying the variable name placeholder
and the part after 'in' is the iterable (or list) you'd like to run a list comprehension on

for example, if you wanted to multiply each entry in the list by 2, you can simply do this:
[x * 2 for x in listExample]
if you wanted to apply a function called function() to each element in the list:
[function(x) for x in listExample]

you can also return values based on conditions:
example:
'''
[x for x in listExample if x > 2]
'''
The above list comprehension will return all elements in listExample that are greater than 2 
'''

#See online documentation for more examples and examples of numpy functions