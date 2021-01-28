import requests
import json
from pathlib import Path


data = {}
processedQueryIndexes = set(())
count = 0
url = 'https://query.wikidata.org/sparql'
query = '''
SELECT DISTINCT ?item ?label_es ?label_en ?article_es ?article_en (GROUP_CONCAT(DISTINCT ?codeISO1; SEPARATOR=", ") AS ?codesISO1) (GROUP_CONCAT(DISTINCT ?codeISO2; SEPARATOR=", ") AS ?codesISO2) (GROUP_CONCAT(DISTINCT ?codeISO3; SEPARATOR=", ") AS ?codesISO3) (GROUP_CONCAT(DISTINCT ?codeLL; SEPARATOR=", ") AS ?codesLL) (GROUP_CONCAT(DISTINCT ?codeIETF; SEPARATOR=", ") AS ?codesIETF) WHERE {
  { ?item wdt:P305 ?codeIETF. }
  UNION { ?item wdt:P218 ?codeISO1. }
  UNION { ?item wdt:P219 ?codeISO2. }
  UNION { ?item wdt:P220 ?codeISO3. }
  UNION { ?item wdt:P1232 ?codeLL. }
  OPTIONAL {
    ?item rdfs:label ?label_en.
    FILTER((LANG(?label_en)) = "en")
  }
  OPTIONAL {
    ?item rdfs:label ?label_es.
    FILTER((LANG(?label_es)) = "es")
  }
  OPTIONAL {
    ?article_es schema:about ?item;
      schema:inLanguage "es";
      schema:isPartOf <https://es.wikipedia.org/>.
  }
  OPTIONAL {
    ?article_en schema:about ?item;
      schema:inLanguage "en";
      schema:isPartOf <https://en.wikipedia.org/>.
  }
}
GROUP BY ?item ?label_es ?label_en ?article_es ?article_en
'''

def is_vacio(elem, code):
    return code in list(elem.keys()) and elem[code][0]==""

def clean(element):
    global count
    obj = {}
    for k in element.keys():
        obj[k] = element[k]['value']
    #Separar las listas de códigos
    obj['codesISO1'] = element['codesISO1']['value'].split(', ')
    obj['codesISO2'] = element['codesISO2']['value'].split(', ')
    obj['codesISO3'] = element['codesISO3']['value'].split(', ')
    obj['codesLL'] = element['codesLL']['value'].split(', ')
    obj['codesIETF'] = element['codesIETF']['value'].split(', ')
    #Comprobar que elementos solo tienen código LL
    if(is_vacio(obj, 'codesISO1') and is_vacio(obj, 'codesISO2') and is_vacio(obj, 'codesISO3') and is_vacio(obj, 'codesIETF')):
        processedQueryIndexes.add(count)
    count+= 1
    return obj


#Realizar query
print('Realizando query...')
result = requests.get(url, params = {'format': 'json', 'query': query})

#Limpiar datos
print('Limpiando datos...')
data = list(map(clean, result.json()['results']['bindings']))

#Retirar los elementos que solo tenían código LL
print('Retirando elementos...')
sortedSet = sorted(processedQueryIndexes, reverse=True)
for i in sortedSet:
    data.pop(i)

#Guardar archivo
with open(Path(__file__).parent / "./query.json", 'w', encoding='utf-8') as f:
    f.write(json.dumps(data, ensure_ascii=False))
