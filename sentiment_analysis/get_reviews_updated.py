import json
import pandas as pd
import requests
from datetime import datetime
import os

chavesOriginais = [
    ("uri", "label", "author_uri"),
    ("name", "label", "author_name")
]

outrasChaves = [
    ("im:version", "label", "im_version"),
    ("im:rating", "label", "im_rating"),
    ("id", "label", "id"),
    ("title", "label", "title"),
    ("content", "label", "content"),
    ("im:voteSum", "label", "im_votesum"),
    ("im:voteCount", "label", "im_votecount"),
    ("updated", "label", "date")
]

linkChaves = [
    ('attributes', 'rel', 'link_attributes_related'),
    ('attributes', 'href', 'link_attributes_href')
]

chavesConteudo = [
    ('attributes', 'term', 'content_attributes_term'),
    ('attributes', 'label', 'content_attributes_label')
]

chavesReview = [
    ('author', chavesOriginais),
    ('link', linkChaves),
    ('im:contentType', chavesConteudo)
]

def getReviews(idReview, numeroPaginas):
    todasReviews = []
    for pagina in range(numeroPaginas):
        respostaReviews = fetchReviews(idReview, pagina + 1)
        if respostaReviews is None:
            print("Nao foi possivel coletar reviews")
            return
        else:
            reviews = json.loads(respostaReviews.text)
            try:
                listaReviews = reviews['feed']['entry']
                salvaJSON(respostaReviews.text, pagina + 1)
                todasReviews = process_reviews(todasReviews, listaReviews)
            except Exception as e:
                print("Não há mais entradas.")
                break

    return todasReviews

def fetchReviews(review_id, page_no):
    print(f"Apanhando reviews da API da Apple App Store \n Página: {page_no}")
    url = f'https://itunes.apple.com/us/rss/customerreviews/page={page_no}/id={review_id}/sortBy=mostRecent/json'
    response = requests.get(url)
    if response.status_code == 200:
        return response
    elif response is None:
        return None
    else:
        print(f"Erro HTTP: {response.status_code}")
        return None

def nomeJSON(page):
    ts = datetime.now()
    file_name = f"review_pagina_{page}_{ts.strftime('%Y%m%d_%H%M%S')}.json"
    return file_name

def process_reviews(todasReviews, listaReviews):
    print("Processando JSON...")
    for review in listaReviews:
        review_flat = extraiChave(outrasChaves, review)
        for sec in chavesReview:
            review_flat.update(extraiChave(sec[1], review[sec[0]]))
        todasReviews.append(review_flat)
    return todasReviews

def extraiChave(keys, review_section):
    reviewExtraida = {}
    for key in keys:
        if key[0] in review_section:
            if key[1] == '':
                reviewExtraida[key[2]] = review_section[key[0]]
            else:
                reviewExtraida[key[2]] = review_section[key[0]][key[1]]
    return reviewExtraida

def salvaReview(todasReviews, arquivo):
    new_reviews_df = pd.DataFrame(todasReviews)
    
    if os.path.exists(arquivo):
        reviewsExistentes = pd.read_csv(arquivo)
        reviewsCombinadas = pd.concat([reviewsExistentes, new_reviews_df]).drop_duplicates(subset=['date'], keep='last')
    else:
        reviewsCombinadas = new_reviews_df
    
    reviewsCombinadas.to_csv(arquivo, index=False)
    print(f"Todas as reviews salvas em csv em: {arquivo}")

def salvaJSON(texto, numeroPagina):
    file_name = nomeJSON(numeroPagina)
    with open(file_name, "w") as json_file:
        print(f"{texto}", file=json_file)
    print(f"JSON salvo em: {file_name}")

def deletarJSONS():
    for file in os.listdir():
        if file.endswith(".json") and file.startswith("review_pagina_"):
            os.remove(file)
            print(f"Deletando JSON: {file}")

no_of_pages = 10
review_id = 6448311069 # ID o app na App Store da Apple
todasReviews = getReviews(review_id, no_of_pages)
salvaReview(todasReviews, '~/Dev/tcc/sentiment_analysis/fetchedReviews.csv')
deletarJSONS()
