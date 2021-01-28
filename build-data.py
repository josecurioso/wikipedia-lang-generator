import json
import urllib.parse
from pathlib import Path
import os

data = {}
dataIETF = {}
engData = {}
engDepData = {}

code_name = {}
code_article = {}
code_name_dep = {}
code_article_dep = {}
ietf_name = {}
ietf_article = {}

def load(filename):
    with open(str(Path(__file__).parent / ('./'+filename+'.json')), 'r', encoding='utf-8') as f:
        return json.loads(''.join(f.readlines()))

def write(filename, contents):
    with open(str(Path(__file__).parent / ('./output/json/'+filename+'.json')), 'w', encoding='utf-8') as f:
        f.write(json.dumps(contents, ensure_ascii=False))

    with open(str(Path(__file__).parent / ('./output/lua/'+filename+'.lua')), 'w', encoding='utf-8') as f:
        for el in list(contents.keys()):
            tmp = f'"{contents[el][0]}"'
            for i in range(len(contents[el])-1):
                tmp = tmp + f', "{contents[el][i+1]}"'
            f.write(f'["{el}"] = {{{tmp}}},\n')

def buscarCoincidencia(clave, contenido):
    count = 0
    for el in data:
        if(clave in el.keys() and el[clave] == contenido):
            return count
        else:
            count+=1
    return "not found"


def cleanAndCap(s):
    s = s.replace("Idioma ", "").replace("Lengua ", "").replace("idioma ", "").replace("lengua ", "").replace(" language", "")
    return s[0].lower() + s[1:]


def cleanAndCapList(l):
    for i in range(len(l)):
        l[i] = cleanAndCap(l[i])
    return l


def getLink(lang, link):
    return urllib.parse.unquote(link.replace("https://"+lang+".wikipedia.org/wiki/", "")).replace("_", " ")


def extractName(element):
    if ('esLang_LangName' in list(element.keys()) and element['esLang_LangName'] != ""):
        return cleanAndCap(element['esLang_LangName'])
    elif ('wdLabel_es' in list(element.keys()) and element['wdLabel_es'] != ""):
        return cleanAndCap(element['wdLabel_es'])
    elif ('wdLabel_en' in list(element.keys()) and element['wdLabel_en'] != ""):
        return cleanAndCap(element['wdLabel_en'])
    elif ('esWikiLink' in list(element.keys()) and element['esWikiLink'] != ""):
        return cleanAndCap(getLink('es', element['esWikiLink']))
    elif ('enWikiLink' in list(element.keys()) and element['enWikiLink'] != ""):
        return cleanAndCap(getLink('en', element['enWikiLink']))
    return "not found"


def extractArticle(element, lang_name):
    if('esWikiLink' in list(element.keys()) and element['esWikiLink'] != ""):
        #print(("Idioma " + lang_name) + " vs " + getLink('es', element['esWikiLink']))
        if(("Idioma " + lang_name) != getLink('es', element['esWikiLink'])):
            #print("pasa")
            return getLink('es', element['esWikiLink'])
    return "not found"

print('')
print('Cargando datos...')
data = load('queryProcesada')
dataIETF = load('queryProcesadaIETF')
engData = load('eng')
engDepData = load('eng_dep')

print('')
print('Generando datos')
print('     Generando code_name + code_article...')
for el in list(engData.keys()):
    j = buscarCoincidencia("enLang_Code", el)
    if(j != "not found"):
        res = data[j]

        code_name[el] = [extractName(res)]
        if (code_name[el][0] == "not found"):
            code_name[el] = cleanAndCapList(res['enLang_LangNames'])

        tmp = extractArticle(res, code_name[el][0])
        if(tmp != "not found"):
            code_article[el] = [tmp]

print('     Generando code_name_dep + code_article_dep...')
for el in list(engDepData.keys()):
    j = buscarCoincidencia("enLang_Code", el)
    if(j != "not found"):
        res = data[j]

        code_name_dep[el] = [extractName(res)]
        if (code_name_dep[el][0] == "not found"):
            code_name_dep[el] = cleanAndCapList(res['enLang_LangNames'])

        tmp = extractArticle(res, code_name_dep[el][0])
        if(tmp != "not found"):
            code_article_dep[el] = [tmp]

print('     Generando ietf_name + ietf_article...')
for el in dataIETF:
    code = el["wdCodes"]["IETF"][0].lower()

    name = extractName(el)
    if(name != "not found"):
        ietf_name[code] = [name]
        tmp = extractArticle(el, ietf_name[code][0])
        if(tmp != "not found"):
            ietf_article[code] = [tmp]

print('')
print('Escribiendo datos...')
if not os.path.exists(str(Path(__file__).parent / './output/')):
    os.mkdir(str(Path(__file__).parent / './output/'))
if not os.path.exists(str(Path(__file__).parent / './output/json/')):
    os.mkdir(str(Path(__file__).parent / './output/json/'))
if not os.path.exists(str(Path(__file__).parent / './output/lua/')):
    os.mkdir(str(Path(__file__).parent / './output/lua/'))
write('code_name', code_name)
write('code_article', code_article)
write('code_name_dep', code_name_dep)
write('code_article_dep', code_article_dep)
write('ietf_name', ietf_name)
write('ietf_article', ietf_article)