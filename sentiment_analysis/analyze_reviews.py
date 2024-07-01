from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import torch

def sentiment_score(review, tokenizer, model):
    tokens = tokenizer.encode(review, return_tensors='pt')
    result = model(tokens)
    return int(torch.argmax(result.logits) + 1)

tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

arquivo = '~/Dev/tcc/sentiment_analysis/fetchedReviews.csv'
dados = pd.read_csv(arquivo)

dados['content'] = dados['title'] + ' ' + dados['content']
dados['Sentiment Score'] = dados['content'].apply(lambda x: sentiment_score(x[:512], tokenizer, model))

dados.to_csv('~/Dev/tcc/sentiment_analysis/analyzed_reviews.csv')
print(dados.head())

    
    
