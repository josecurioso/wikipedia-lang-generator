import json;
from operator import itemgetter
from pathlib import Path

query = {}
queryLen = 0
enLang = {}
enLangLen = 0
enLangDep = {}
enLangDepLen = 0
esLang = {}
esLangLen = 0

processedQueryIndexes = set(())

queryProcesada = []
queryProcesadaIETF = []

sustituciones = {
'ccx': "",#deprecated
'chs': "", # es una familia
'nbx': "", #separada en varias
'nhj': "", #merged en nhi
'qbt': "",  #merged en sai
}

#prototipo = [
#    {
#        "wdLink": "",
#        "enwikiLink": "",
#        "eswikiLink": "",
#        "wdLabel_es": "",
#        "wdLabel_en": "",
#        "enLang_Code": "",
#        "enLang_LangNames": [],
#        "esLang_LangName": "",
#        "esLang_ArticleName": "",
#        "wdCodes" : {
#            "ISO1": [],
#            "ISO2": [],
#            "ISO3": [],
#            "LL": [],
#            "IETF": [],
#        }
#    }
#]

def load(filename):
    with open(str(Path(__file__).parent / ('./'+filename+'.json')), 'r', encoding='utf-8') as f:
        data = json.loads(''.join(f.readlines()))
        return {'data':data, 'dataLen': len(data)}

def write(filename, data):
    with open(str(Path(__file__).parent / ('./'+filename+'.json')), 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))

def processNewElement(j):
    obj = {}
    if( j != "not found"):
        processedQueryIndexes.add(query.index(query[j]))
        if("item" in query[j].keys()):
            obj["wdLink"] = query[j]["item"]
        if("article_en" in query[j].keys()):
            obj["enWikiLink"] = query[j]["article_en"]
        if("article_es" in query[j].keys()):
            obj["esWikiLink"] = query[j]["article_es"]
        if("label_en" in query[j].keys()):
            obj["wdLabel_en"] = query[j]["label_en"]
        if("label_es" in query[j].keys()):
            obj["wdLabel_es"] = query[j]["label_es"]
        obj["wdCodes"] = {}
        if("codesISO1" in query[j].keys()):
            obj["wdCodes"]["ISO1"] = query[j]["codesISO1"]
        if("codesISO2" in query[j].keys()):
            obj["wdCodes"]["ISO2"] = query[j]["codesISO2"]
        if("codesISO3" in query[j].keys()):
            obj["wdCodes"]["ISO3"] = query[j]["codesISO3"]
        if("codesLL" in query[j].keys()):
            obj["wdCodes"]["LL"] = query[j]["codesLL"]
        if("codesIETF" in query[j].keys()):
            obj["wdCodes"]["IETF"] = query[j]["codesIETF"]
    return obj

def processEnCode(code):
    obj = processNewElement(buscarCodeEnQuery(code, ["codesISO1", "codesISO2", "codesISO3"]))
    
    #Data from Module:Lang/data
    obj["enLang_Code"] = code
    obj["enLang_LangNames"] = enLang[code]
    enLang.pop(code, None)

    #Data from Spanish Plantilla:Lang and Spanish Wiktionary manually merged
    if(code in esLang.keys()):
        obj["esLang_LangName"] = esLang[code]
        esLang.pop(code, None)
    queryProcesada.append(obj)


def processEnDepCode(code):
    obj = processNewElement(buscarCodeEnQuery(code, ["codesISO1", "codesISO2", "codesISO3"]))
    
    #Data from Module:Lang/data
    obj["enLang_Code"] = code
    obj["enLang_LangNames"] = enLangDep[code]
    enLangDep.pop(code, None)

    #Data from Spanish Plantilla:Lang and Spanish Wiktionary manually merged
    if(code in esLang.keys()):
        obj["esLang_LangName"] = esLang[code]
        esLang.pop(code, None)
    queryProcesada.append(obj)


def processEsLangLeftover(code):
    res = "not found"
    obj = processNewElement(buscarEnQuery(code))
    if("wdLink" in obj.keys()):
        res = buscarCoincidencia("wdLink", obj["wdLink"])
    elif(code in sustituciones.keys() and sustituciones[code] != ''):
        res = buscarCoincidencia("enLang_Code", sustituciones[code])
        
    if(res != "not found"):
        queryProcesada[res]["esLang_LangName"] = esLang[code]
        esLang.pop(code, None)
        
def buscarEnQuery(code):
    return buscarCodeEnQuery(code, ["codesISO1", "codesISO2", "codesISO3", "codesLL", "codesIETF"])

def buscarCodeEnQuery(code, fields):
    count = 0
    for el in query:
        for f in fields:
            if(code in el[f]):
                return count
        count+=1
    return "not found"

def buscarCoincidencia(clave, contenido):
    count = 0
    for el in queryProcesada:
        if(clave in el.keys() and el[clave] == contenido):
            return count
        count+=1
    return "not found"

print('')
print('Cargando datos...')
query, queryLen = itemgetter('data', 'dataLen')(load('query'))
enLang, enLangLen = itemgetter('data', 'dataLen')(load('eng'))
enLangDep, enLangDepLen = itemgetter('data', 'dataLen')(load('eng_dep'))
esLang, esLangLen = itemgetter('data', 'dataLen')(load('esp'))

print('')
print('Procesando datos')
print('     Procesando enLang...')
for i in list(enLang.keys()).copy():
    processEnCode(i) 

print('     Procesando enLangDep...')
for i in list(enLangDep.keys()).copy():
    processEnDepCode(i)  

print('     Procesando esLang...')
for e in list(esLang.keys()).copy():
    processEsLangLeftover(e)

print('     Eliminando procesados...')
for i in sorted(processedQueryIndexes, reverse=True):
    query.pop(i)


processedQueryIndexes = set(())
count = 0

print('     Procesando IETF...')
for el in query:
    if("-" in el["codesIETF"][0]):
        queryProcesadaIETF.append(processNewElement(count))
        processedQueryIndexes.add(count)
    count += 1
print('     Eliminando procesados...')
for i in sorted(processedQueryIndexes, reverse=True):
    query.pop(i)

print('')
print('Resultados procesado')
print("     Sin procesar de enLang: " + str( len(enLang.keys()) ) + " de " + str( enLangLen ))
#print(enLang)
print("     Sin procesar de enLangDep: " + str( len(enLangDep.keys()) ) + " de " + str( enLangDepLen ))
#print(enLangDep)
print("     Sin procesar de esLang: " + str( len(esLang.keys())) + " de " + str( esLangLen ))
#print(esLang)
print("     Sin procesar de wikidata: " + str( len(query) ) + ' de ' + str( queryLen ))
print("")
print("     Elementos en el archivo final: " + str(len(queryProcesada)))
print("     Elementos en el archivo final de IETF con guión: " + str(len(queryProcesadaIETF)))


write('queryProcesada', queryProcesada)
write('queryNoProcesada', query)
write('queryProcesadaIETF', queryProcesadaIETF)


    