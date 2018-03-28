# -*- coding: utf-8 -*-
"""
@author: Shubham
"""

import os
import requests
from bs4 import BeautifulSoup
import re
from  more_itertools import unique_everseen

url ='https://www.drugs.com/drug_information.html'
a = requests.get(url)
soup = BeautifulSoup(a.content)

generic_drugs = ['albuterol']
alphabet_list = []

for tag in soup.findAll('div',{'class':'search-browse'}):
    for t in tag.find_all('a', href=True):
        if(t.get_text()!='Advanced Search'):
            alphabet_list.append(t.get('href'))

alphabet_list2 = []

for pair in alphabet_list:
    url2 = 'https://www.drugs.com' + str(pair) + '?filter=GX'
    r = requests.get(url2)
    soup = BeautifulSoup(r.content)
    
    for tag in soup.findAll('td',{'class':'paging-list-index'}):
        for t in tag.find_all('a', href=True):
            if(t.get_text()!='Advanced Search'):
                alphabet_list2.append(t.get('href'))

alphabet_list = alphabet_list + alphabet_list2
alphabet_list = sorted(list(set(alphabet_list)))

alphabet_list3 = alphabet_list
for index, link in enumerate(alphabet_list):
    if 'filter' not in link:
        del alphabet_list3[index]

alphabet_list = alphabet_list3

for element in alphabet_list:
    url2 = 'https://www.drugs.com' + str(element)
    r = requests.get(url2)
    soup = BeautifulSoup(r.content)
    
    for tag in soup.findAll('ul',{'class':'doc-type-list'}):
        for t in tag.find_all('a', href=True):
            generic_drugs.append(t.get_text())

generic_drugs = sorted(list(set(generic_drugs)))
generic_drugs1 = generic_drugs

for index, drug in enumerate(generic_drugs):
    generic_drugs[index] = re.sub(r' \(.*\)', '', drug)
    
for index, drug in enumerate(generic_drugs):
    if len(drug.split()) == 2:
        generic_drugs[index] = generic_drugs[index].replace(', ', '-')
        generic_drugs[index] = generic_drugs[index].replace(' ', '-')
    elif (len(drug.split()) == 3):
        if 'and' in drug:
            generic_drugs[index] = generic_drugs[index].replace(' and ', '-')
        generic_drugs[index] = generic_drugs[index].replace(', ', '-')
        generic_drugs[index] = generic_drugs[index].replace(' ', '-')
        generic_drugs[index] = generic_drugs[index].replace('-/-', '-')
        generic_drugs[index] = generic_drugs[index].replace(' / ', '-')
    elif (len(drug.split()) < 6):
        if 'and' in drug:
            generic_drugs[index] = generic_drugs[index].replace(', and ', '-')
            generic_drugs[index] = generic_drugs[index].replace(' and ', '-')
        generic_drugs[index] = generic_drugs[index].replace(', ', '-')
        generic_drugs[index] = generic_drugs[index].replace(' ', '-')
        generic_drugs[index] = generic_drugs[index].replace('-/-', '-')
        generic_drugs[index] = generic_drugs[index].replace(' / ', '-')
    else:
        generic_drugs[index] = generic_drugs[index].replace(' / ', '-')
        generic_drugs[index] = generic_drugs[index].replace(' ', '-')

folder_path = "E:\\UNCC\\Modern Data Science\\drugsdotcom_data"
list_of_list = []

for drug in generic_drugs:
    url ='https://www.drugs.com/drug-interactions/' + str(drug).strip("[]'").strip().replace(" ", "%20")+ '-index.html'
    a = requests.get(url)
    soup = BeautifulSoup(a.content)
    folder_name =  str(drug).strip("[]'").strip()
    newpath = str(folder_path + "\\" + folder_name)
        
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    flag = 0
    for tag in soup.findAll('div',{'class':'contentBox'}):
        for t in tag.find_all('h1'):
            if t.get_text() == 'Page Not Found':
                flag = 1
                list_data = []
                list_data.append("Consumer Interaction Data:")
                list_data.append("There are no known drug interactions for " + drug + ". However, this does not necessarily mean no interactions exist. Always consult with your doctor or pharmacist.")
                with open( newpath + "//" + 'File' + ".txt", mode='wt', encoding='utf-8') as myfile:
                    myfile.write('\n'.join(list_data))
                    
    for tag in soup.findAll('span',{'class':'alert bold'}):
        if 'no known drug interactions' in tag.get_text():
            flag = 2
            list_data = []
            list_data.append("Consumer Interaction Data:")
            list_data.append("There are no known drug interactions for " + drug + ". However, this does not necessarily mean no interactions exist. Always consult with your doctor or pharmacist.")
            with open( newpath + "//" + 'File' + ".txt", mode='wt', encoding='utf-8') as myfile:
                myfile.write('\n'.join(list_data))
                    
    if flag == 0:
        for tag in soup.findAll('ul',{'class':'interactions column-list-2'}):
            drug_and_url_list = []
            for t in tag.find_all('a', href=True):
                drug_and_url_list.append(t.get_text())
                drug_and_url_list.append(t.get('href'))
                if('disease' not in t.get('href') or 'food' not in t.get('href') or 'alcohol' not in t.get('href')):
                    list_of_list.append(drug_and_url_list)
                    drug_and_url_list = []
        
        list_of_list = list_of_list[:10]
        k = -1 
        for element in list_of_list:
            k = k+1
            list_data = []
            url2 = 'https://www.drugs.com' + str(element[1]).lower()
            r = requests.get(url2)
            soup = BeautifulSoup(r.content)
            
            for tag in soup.findAll('link',{"rel":"canonical"}):
                url10 = tag.get('href') 
                
            list_data.append("URL:")
            list_data.append(url10)
            list_data.append("\nDrug 1:")
            list_data.append(drug)
            list_data.append("\nDrug 2:")
            list_data.append(element[0])
            
            for tag in soup.findAll('div',{"class":"interactions-reference"}):
                text1 = tag.get_text()
                list_data.append("\nClassification:")
                list_data.append(text1.split(' ', 1)[0])
                list_data.append("\nConsumer Interaction Data:")
                list_data.append(text1.split(' ', 1)[1])
            
            if 'professional' not in url10:
                url3 = url10 + '?professional=1'
            else:
                url3 = url10
            c = requests.get(url3)
            soup = BeautifulSoup(c.content)
            
            for tag in soup.findAll('div',{"class":"interactions-reference"}):
                text2 = tag.get_text()
                text2 = text2.split(' ', 1)[1]
                list_data.append("\nProfessional Interaction Data:")
                list_data.append(text2.split("References", 1)[0])
            
            for tag in soup.findAll('div',{"class":"referenceList"}):
                for t in soup.findAll('ol'):
                    list_data.append("\nReferences:")
                    list_data.append(t.get_text())
            
            list_data = list(unique_everseen(list_data))
            
            with open( newpath + "//" + 'File ' + str(k) + ".txt", mode='wt', encoding='utf-8') as myfile:
                    myfile.write('\n'.join(list_data))
        list_of_list = []