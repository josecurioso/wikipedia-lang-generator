# wikipedia-lang-generator
Colección de scripts de python para generar las tablas de datos utilizadas en [Módulo:Lang](https://es.wikipedia.org/wiki/Módulo:Lang)
## Archivos generados
### Nombres
Se generan los siguientes listados:
* `<código ISO639> - <nombre>` Para los activos y los obsoletos
* `<código ISO639> - <artículo>` Para los activos y los obsoletos
* `<código IETF> - <nombre>` Para los que no tienen código simple
* `<código IETF> - <artículo>` Para los que no tienen código simple

Se utilizan como fuentes de información:
* La siquiente query a Wikidata
```sparql
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
```
* El [registro de sub-etiquetas del IANA](https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry).
* Un listado de traducciones al español compilado manualmente.
### Sistemas de escritura
### Regiones
## Uso
Para generar el archivo de nombres basta con ejecutar el `run.py`, automáticamente se hace la query a wikidata, se procesan los datos y se generan los archivos.
