import json
import urllib.parse
from pathlib import Path
from datetime import datetime
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

vetados = [
    "cel-gaulish"
]
         #JSON  LUA
output = [False, True]

def load(filename):
    with open(str(Path(__file__).parent / ('./'+filename+'.json')), 'r', encoding='utf-8') as f:
        return json.loads(''.join(f.readlines()))

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

def generate_iana_languages(contents, contents2):    
    file = "	-- File-Date: " + str(datetime.today().strftime('%Y-%m-%d')) + "\n"
    file = file + "local active = {\n"

    for el in list(contents.keys()):
        tmp = f'"{contents[el][0]}"'
        for i in range(len(contents[el])-1):
            tmp = tmp + f', "{contents[el][i+1]}"'
        file = file + (f'\t["{el}"] = {{{tmp}}},\n')
    file = file + "}\n"
    file = file + "local deprecated = {\n"

    for el in list(contents2.keys()):
        tmp = f'"{contents2[el][0]}"'
        for i in range(len(contents2[el])-1):
            tmp = tmp + f', "{contents2[el][i+1]}"'
        file = file + (f'\t["{el}"] = {{{tmp}}},\n')
    file = file + "}\n"
    file = file + "return {\n"
    file = file + "\tactive = active,\n"
    file = file + "\tdeprecated = deprecated,\n"
    file = file + "}"
    return file

def write_iana_languages(contents, contents2):  
    writeJSON("code_name", contents)  
    writeJSON("code_name_dep", contents2)  
    with open(str(Path(__file__).parent / ('./output/lua/iana_languages_translation.lua')), 'w', encoding='utf-8') as f:
        f.write(generate_iana_languages(contents, contents2))


def generate_articles(contents, contents2, contents3):
    file = "\t-- For active\n"
    for el in list(contents.keys()):
        tmp = f'"{contents[el][0]}"'
        for i in range(len(contents[el])-1):
            tmp = tmp + f', "{contents[el][i+1]}"'
        file = file + (f'\t["{el}"] = {{{tmp}}},\n')
    file = file + "\n\n\n"

    file = file + "\t-- For deprecated\n"
    for el in list(contents2.keys()):
        tmp = f'"{contents2[el][0]}"'
        for i in range(len(contents2[el])-1):
            tmp = tmp + f', "{contents2[el][i+1]}"'
        file = file + (f'\t["{el}"] = {{{tmp}}},\n')
    file = file + "\n\n\n"

    file = file + "\t-- For complex\n"
    for el in list(contents3.keys()):
        tmp = f'"{contents3[el][0]}"'
        for i in range(len(contents3[el])-1):
            tmp = tmp + f', "{contents3[el][i+1]}"'
        file = file + (f'\t["{el}"] = {{{tmp}}},\n')
    return file

def write_articles(contents, contents2, contents3):  
    writeJSON("code_article", contents)  
    writeJSON("code_article_dep", contents2)  
    writeJSON("ietf_article", contents3)  
    with open(str(Path(__file__).parent / ('./output/lua/articles.lua')), 'w', encoding='utf-8') as f:
        f.write(generate_articles(contents, contents2, contents3))

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


def extractName(element, fallback = False):
    if ('esLang_LangName' in list(element.keys()) and element['esLang_LangName'] != ""):
        return cleanAndCapList(element['esLang_LangName'])
    elif ('wdLabel_es' in list(element.keys()) and element['wdLabel_es'] != ""):
        return [cleanAndCap(element['wdLabel_es'])]
    elif (fallback and 'wdLabel_en' in list(element.keys()) and element['wdLabel_en'] != ""):
        return [cleanAndCap(element['wdLabel_en'])]
    elif ('esWikiLink' in list(element.keys()) and element['esWikiLink'] != ""):
        return [cleanAndCap(getLink('es', element['esWikiLink']))]
    elif (fallback and 'enWikiLink' in list(element.keys()) and element['enWikiLink'] != ""):
        return [cleanAndCap(getLink('en', element['enWikiLink']))]
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

        name = extractName(res)
        if (name != "not found"):
            code_name[el] = name
        #else: 
            #code_name[el] = cleanAndCapList(res['enLang_LangNames'])

        tmp = extractArticle(res, code_name[el][0] if (el in list(code_name.keys())) else engData[el][0] )
        if(tmp != "not found"):
            code_article[el] = [tmp]

print('     Generando code_name_dep + code_article_dep...')
for el in list(engDepData.keys()):
    j = buscarCoincidencia("enLang_Code", el)
    if(j != "not found"):
        res = data[j]

        name = extractName(res)
        if (name != "not found"):
            code_name_dep[el] = name
        #else: 
            #code_name_dep[el] = cleanAndCapList(res['enLang_LangNames'])

        tmp = extractArticle(res, code_name_dep[el][0] if (el in list(code_name_dep.keys())) else engDepData[el][0])
        if(tmp != "not found"):
            code_article_dep[el] = [tmp]

print('     Generando ietf_name + ietf_article...')
for el in dataIETF:
    code = el["wdCodes"]["IETF"][0].lower()

    name = extractName(el) ##Pensar si activar o no el fallback extractName(el, True)
    if(name != "not found" and not (code in vetados)):
        ietf_name[code] = name
        tmp = extractArticle(el, ietf_name[code][0])
        if(tmp != "not found"):
            ietf_article[code] = [tmp]

print('')
print('Escribiendo datos...')
if not os.path.exists(str(Path(__file__).parent / './output/')):
    os.mkdir(str(Path(__file__).parent / './output/'))
if output[0] and not os.path.exists(str(Path(__file__).parent / './output/json/')):
    os.mkdir(str(Path(__file__).parent / './output/json/'))
if output[1] and not os.path.exists(str(Path(__file__).parent / './output/lua/')):
    os.mkdir(str(Path(__file__).parent / './output/lua/'))

write_iana_languages(code_name, code_name_dep) 
write_articles(code_article, code_article_dep, ietf_article)
write('override', ietf_name)