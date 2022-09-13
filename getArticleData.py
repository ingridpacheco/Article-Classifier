# -*- coding: utf-8 -*-
"""Scraping_DataSet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZAdtcJCWiIYTxKuDaovbe16sl79gN2Jb

# **MAI712** - Fundamentos em Ciência de Dados
___
#### **Professores:** Sergio Serra e Jorge Zavaleta
___
#### **Equipe:** Ingrid Pacheco, Eduardo Prata, Renan Parreira
___
### **OBJETIVO:**
Esse script tem como objetivo auxiliar no Web Scraping para criação do nosso DataSet do projeto final da matéria MAI712

#### **Requisito:**
É necessário que tenhamos instalado o Beautiful Soup, antes mesmo de iniciarmos nosso _**Script de Web Scraping**_ para construção do nosso _DataSet_ de artigos.

#### **Imports e Bibliotecas**

Aqui estaremos declarando as bibliotecas e módulos necessários para nosso scrtipt
"""

# Importar módulo de Requests e de Expressões Regulares
import requests, re, random, json
# Import para tratamento do arquivo e da versão do sistema
from os import system, name, remove
from os.path import isfile
# Import do beautifulSoup para tratamento dos dados retornados da pagina Web
from bs4 import BeautifulSoup
from datetime import date
import csv
import time

#!pip install feedparser
import feedparser
import urllib, urllib.request

#!pip install semanticscholar
import semanticscholar as sch

#!pip install prov
#from prov.model import ProvDocument

"""#### **Primeiro Etapa:** Declaração das variáveis necessárias para nosso WebScraping

"""

# Pegando aleatoriedade de browser para não ser identificado o Robo.
UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", 
       "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
       "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
       "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
       )

ua = UAS[random.randrange(len(UAS))]

# Variáveis do sistema
#cabecalho = {'user-agent': 'Mozilla/5.0'}
cabecalho = {'user-agent': ua}
header = ['title', 'paperId', 'doi', 'authors', 'abstract', 'publisher', 'year', 'topics', 'fields_of_study']
today = date.today()
nome_arquivo = 'articles-' + str(today) + '.csv'

alvo = "https://sigir.org/sigir2022/program/accepted/"

"""#### **Segunda Etapa:** Request no alvo e `html.parser` e filtra penas _tags_ analisadas como importantes


"""

# OBS: segundo professor Jorge precisamos inicialmente pegar o arquivo robot.txt para saber os caminhos permitidos para o Scraping


# Busca o HTML a ser explorado
resposta = requests.get(alvo, headers = cabecalho)
print(resposta.text)

# Formatando o retorno
sopa = BeautifulSoup(resposta.text, 'html.parser')

# Dados da Carteira:
#infos = sopa.find('div', {'class':'post-body'}).prettify()
infos = sopa.find('div', {'class':'post-body'})
print(infos)

"""#### **Terceira Etapa:** Testando os Conteúdos

Testando o retorno para estudar a estrutura do HTML para montar o _Scraping_
"""

#print( infos )
#print( infos[0].contents[1].text )
print( len(infos) )
#print( infos.contents[4].text )

# Controle
conta = 0
# Indicador de início de captura
comeca_captura = False
# Lista de Nomes de artigos
lista_artigos = []
for info in infos:
  # Marcação de START de captura de linhas: "Full Papers"
  if comeca_captura == False:
    if "Full Papers" in info: comeca_captura = True
  else:
    if len( info ) > 1:
      print( f'info({str(conta)}): {info}' )
      lista_artigos.append( info.find('b').text.strip() )
  if conta == 327: break
  # Marcação de END de captura de linhas: "<hr>"
  conta +=1

print( f'Caprutou {conta} linha(s)')

"""#### **Quarta Etapa:** Loop de criação do _DataSet_

Loop o qual estaremos montando nosso DataSet:   
* com todas as transações de acordo com o _**filtro** (carteira)_

1. Lista de elementos da página do _Scraping_:
"""

# Lista dos elementos a serem garimpados
#lista_elementos = sopa.find_all('div', {'class': 'sc-1fp9csv-0 ifDzmR'})
print("Tamanho da lista: " + str(len(lista_artigos)))
print(lista_artigos)

########################################################################################
# ENRIQUECENDO OS DADOS DO DATASET ATRAVÉS DOS NOMES DOS ARTIGOS LISTADOS ANTERIORMENTE
########################################################################################

# Site de onde vamos completar as informações dos artigos
link = 'https://api.semanticscholar.org/graph/v1/paper/search?query='
total_linhas = 0

# Listar os artigos para montar o dataSet complementando com as demais informações
with open(nome_arquivo,'w') as f:

  # create the csv writer
  writer = csv.writer(f)

  # write header to csv file
  writer.writerow(header)

  for artigo in lista_artigos:
    filtro = artigo.replace(' ','+')

    def getFromSemanticScholar(filtro):
        link = 'https://api.semanticscholar.org/graph/v1/paper/search?query='
        print('Não tem DOI')
        retorno = requests.get( link + filtro, headers = cabecalho)
        if retorno.status_code == 429:
            time.sleep(300)
            print('Esperando um pouco')
            retorno = requests.get( link + filtro, headers = cabecalho)
        sp_artigo = BeautifulSoup(retorno.text, 'html.parser')
        artigo_json = json.loads(sp_artigo.text)
        if len(artigo_json["data"]) > 0:
            str_paperId = artigo_json["data"][0]["paperId"]
            str_title = artigo_json["data"][0]["title"]
            search_id = str_paperId
            return str_paperId,str_title,search_id
        return None,None,None

    url = 'http://export.arxiv.org/api/query?search_query=' + filtro + '&start=0&max_results=1'
    data = urllib.request.urlopen(url)
    data = data.read().decode('utf-8')
    d = feedparser.parse(data)
    
    if len(d['entries']) > 0:
        alvo = d['entries'][0]['id']
        alvo = alvo.replace('arxiv', 'export.arxiv')
        alvo = alvo[:-2]

        resposta = requests.get(alvo)

        print(resposta)

        sopa = BeautifulSoup(resposta.text, 'html.parser')
        search_id = None

        subjects = sopa.find('td', {'class': 'tablecell subjects'})
        print(subjects.get_text())
        doi = sopa.find('td', {'class': 'tablecell doi'})
        if doi is not None:
            search_id = doi.get_text()
        else:
            str_paperId,str_title,search_id = getFromSemanticScholar(filtro)
    else:
        str_paperId,str_title,search_id = getFromSemanticScholar(filtro)

    # Complementando as informações do DataSet

    if total_linhas == 99:
      time.sleep(300)

    if search_id is not None:
      retorno = sch.paper(search_id, timeout=8)
      print(retorno)
      paperId = retorno['paperId']
      title = retorno['title']
      doi = retorno['doi']
      authors_list = retorno['authors']
      abstract = retorno['abstract']
      publisher = retorno['venue']
      year = retorno['year']
      topics_list = retorno['topics']
      fields_of_study_list = retorno['fieldsOfStudy']

      print( f'RETORNO: {retorno}' )
      authors = ''
      for author in authors_list: authors = authors + author['name'] + ','
      authors = authors[0:len(authors)-1]

      topics = ''
      for topic in topics_list:
        topic = topic if type(topic) is not dict else topic['topic']
        topics = topics + topic + ','
      topics = topics[0:len(topics)-1]

      fields_of_study = ''
      if fields_of_study_list is not None:
        for field in fields_of_study_list: fields_of_study = fields_of_study + field + ','
        fields_of_study = fields_of_study[0:len(fields_of_study)-1]

      article_data = [title,paperId,doi,authors,abstract,publisher,year,topics,fields_of_study]
      writer.writerow(article_data)

      total_linhas += 1

print(total_linhas)