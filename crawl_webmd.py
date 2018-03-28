# -*- coding: utf-8 -*-
"""
@author: Shubham
"""

import os
import requests
from bs4 import BeautifulSoup
from  more_itertools import unique_everseen

url ='https://www.webmd.com/drugs/2/index'
a = requests.get(url)
soup = BeautifulSoup(a.content)

generic_drugs = []
alphabet_list = []

for tag in soup.findAll('ul',{'class':'browse-letters squares'}):
    for t in tag.find_all('a', href=True):
        alphabet_list.append(t.get('href'))
        
for element in alphabet_list:
    url2 = 'https://www.webmd.com' + str(element)
    r = requests.get(url2)
    soup = BeautifulSoup(r.content)
    
    for tag in soup.findAll('ul',{'class':'drug-list'}):
        list1 = []
        for t in tag.find_all('a', href=True):
            list1.append(t.get_text())
            list1.append(t.get('href'))
            generic_drugs.append(list1)
            list1 = []
            
folder_path = "E:\\UNCC\\Modern Data Science\\webmd_data"

for element in generic_drugs:
    element[0] = element[0].replace(':',' ')
    element[0] = element[0].replace('<',' ')
    element[0] = element[0].replace('>',' ')
    element[0] = element[0].replace('"',' ')
    element[0] = element[0].replace(':',' ')

for element in generic_drugs[1177:]:
    folder_name =  str(element[0])
    newpath = str(folder_path + "\\" + folder_name)
        
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        
    url3 = 'https://www.webmd.com' + str(element[1]) + '/list-interaction-medication'
    r = requests.get(url3)
    soup = BeautifulSoup(r.content)
    
    interactions_list = []
    list_data = []
    
    for tag in soup.findAll('article',{'class':'subpage interaction-medication'}):
        list2 = []
        for index, t in enumerate(tag.find_all('a', href=True)):
            if index != 0:
                list2.append(t.get_text())
                list2.append(t.get('href'))
                interactions_list.append(list2)
                list2 = []
            
    if len(interactions_list) != 0:
        k = 0
        for e in interactions_list[:20]:
             url5 = 'https://www.webmd.com' + str(e[1])
             r = requests.get(url5)
             soup = BeautifulSoup(r.content)
             
             list_data = []
             
             list_data.append("URL:")
             list_data.append(url5)
             
             list_data.append("\nDrug 1:")
             list_data.append(element[0])
             
             list_data.append("\nDrug 2:")
             list_data.append(e[0])
             
             for tag in soup.findAll('article',{'class':'subpage interaction-details'}):
                 flag1 = True
                 flag2 = True
                 for index, t in enumerate(tag.find_all('p',{'class':'answer'})):
                     if index == 1:
                         text = t.get_text()
                         text = text.split(' ', 1)[0]
                         text = text.replace('.','')
                         list_data.append("\nClassification:")
                         list_data.append(text)
                     elif index == 2 or index == 3 or index == 4:
                         if flag1:
                             list_data.append("\nConsumer Interaction Data:")
                             flag1 = False
                         list_data.append(t.get_text())
                     elif index > 4:
                         if flag2:
                             list_data.append("\nReferences:")
                             flag2 = False
                         list_data.append(t.get_text())
             
             list_data = list(unique_everseen(list_data))
            
             with open( newpath + "//" + 'File ' + str(k) + ".txt", mode='wt', encoding='utf-8') as myfile:
                    myfile.write('\n'.join(list_data))
             k += 1
    else:
        list_data = []
        list_data.append("Consumer Interaction Data:")
        list_data.append("There are no known drug interactions for " + element[0] + ". However, this does not necessarily mean no interactions exist. Always consult with your doctor or pharmacist.")
        with open( newpath + "//" + 'File' + ".txt", mode='wt', encoding='utf-8') as myfile:
            myfile.write('\n'.join(list_data))
        