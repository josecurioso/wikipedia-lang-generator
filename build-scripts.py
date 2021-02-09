import requests
import json
from pathlib import Path
import json
import urllib.parse
from pathlib import Path
from datetime import datetime
import os

data = []
processedQueryIndexes = set(())
count = 0

         #JSON  LUA
output = [False, True]

output_spanish = {}
output_english = {}

url = 'https://query.wikidata.org/sparql'
query = '''
SELECT ?item ?label_en ?label_es ?articleEn ?articleEs ?code
WHERE
{
  ?item wdt:P506 ?code
  OPTIONAL {
    ?item rdfs:label ?label_en.
    FILTER((LANG(?label_en)) = "en")
  }
  OPTIONAL {
    ?item rdfs:label ?label_es.
    FILTER((LANG(?label_es)) = "es")
  }
  OPTIONAL {
    ?articleEs schema:about ?item;
      schema:inLanguage "es";
      schema:isPartOf <https://es.wikipedia.org/>.
  }
  OPTIONAL {
    ?articleEn schema:about ?item;
      schema:inLanguage "en";
      schema:isPartOf <https://en.wikipedia.org/>.
  }
}
'''

def writeJSON(filename, contents):
    if output[0]:
        with open(str(Path(__file__).parent / ('./output/json/'+filename+'.json')), 'w', encoding='utf-8') as f:
            f.write(json.dumps(contents, ensure_ascii=False))

def writeLUA(filename, contents):
    if output[1]:
        with open(str(Path(__file__).parent / ('./output/lua/'+filename+'.lua')), 'w', encoding='utf-8') as f:
            for el in list(contents.keys()):
                tmp = f'"{contents[el][0]}"'
                for i in range(len(contents[el])-1):
                    tmp = tmp + f', "{contents[el][i+1]}"'
                f.write(f'\t["{el}"] = {{{tmp}}},\n')

def write(filename, contents):
    writeJSON(filename, contents)
    writeLUA(filename, contents)

def load(filename):
    with open(str(Path(__file__).parent / ('./'+filename+'.json')), 'r', encoding='utf-8') as f:
        return json.loads(''.join(f.readlines()))

def generate_iana_scripts(contents, contents2):    
    file = "	-- File-Date: " + str(datetime.today().strftime('%Y-%m-%d')) + "\n"
    file = file + "return {\n"

    for el in list(contents.keys()):
        tmp = f'"{contents[el][0]}"'
        for i in range(len(contents[el])-1):
            tmp = tmp + f', "{contents[el][i+1]}"'
        file = file + (f'\t["{el}"] = {{{tmp}}},\n')
    file = file + "\n\n\n\n"

    for el in list(contents2.keys()):
        tmp = f'"{contents2[el][0]}"'
        for i in range(len(contents2[el])-1):
            tmp = tmp + f', "{contents2[el][i+1]}"'
        file = file + (f'\t["{el}"] = {{{tmp}}},\n')
    file = file + "}\n"
    return file

def write_iana_scripts(contents, contents2):
    writeJSON("iana_scripts", dict(contents, **contents2))  
    with open(str(Path(__file__).parent / ('./output/lua/iana_scripts.lua')), 'w', encoding='utf-8') as f:
        f.write(generate_iana_scripts(contents, contents2))

def is_vacio(elem, code):
    return code in list(elem.keys()) and elem[code][0]==""

def getLink(lang, link):
    return urllib.parse.unquote(link.replace("https://"+lang+".wikipedia.org/wiki/", "")).replace("_", " ")

def cleanString(n):
    word = n.replace("Alfabeto ", "").replace("alfabeto ", "")
    return ' '.join(w[0].upper() + w[1:] for w in word.split())

def clean(element):
    global count
    obj = {}
    for k in element.keys():
        obj[k] = element[k]['value']
    if("articleEn" in list(obj.keys())):
        obj["articleEn"] = getLink("en", obj["articleEn"])
    if("articleEs" in list(obj.keys())):
        obj["articleEs"] = getLink("es", obj["articleEs"])
    return obj

engData = load('scripts-en')
espData = load('scripts-es')

#Realizar query
print('Realizando query...')
result = requests.get(url, params = {'format': 'json', 'query': query})

#Limpiar datos
print('Limpiando datos...')
data = list(map(clean, result.json()['results']['bindings']))

#Seleccionando etiquetas
print('Seleccionando etiquetas...')
for el in data:
    if(el["code"] in list(espData.keys())):
        output_spanish[el["code"]] = espData[el["code"]]
    if("label_es" in list(el.keys())):
        output_spanish[el["code"]] = [cleanString(el["label_es"])]
    elif("articleEs" in list(el.keys())):
        output_spanish[el["code"]] = [cleanString(el["articleEs"])]
    elif(el["code"] in list(engData.keys())):
        output_english[el["code"]] = engData[el["code"]]
    elif("label_en" in list(el.keys())):
        #print(el["code"])
        output_english[el["code"]] = [el["label_en"]]
    elif("articleEn" in list(el.keys())):
        #print(el["code"])
        output_english[el["code"]] = [el["articleEn"]]


print('Escribiendo archivo...')
if not os.path.exists(str(Path(__file__).parent / './output/')):
    os.mkdir(str(Path(__file__).parent / './output/'))
if output[0] and not os.path.exists(str(Path(__file__).parent / './output/json/')):
    os.mkdir(str(Path(__file__).parent / './output/json/'))
if output[1] and not os.path.exists(str(Path(__file__).parent / './output/lua/')):
    os.mkdir(str(Path(__file__).parent / './output/lua/'))

write_iana_scripts(output_spanish, output_english)

