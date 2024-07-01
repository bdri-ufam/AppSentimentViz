import streamlit as st
from collections import Counter
import re
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key='')

st.title('Dashboard')

arquivo = '~/Dev/tcc/streamlit/analyzed_reviews.csv'
dados = pd.read_csv(arquivo)

dados['content'] = dados['title'] + ' ' + dados['content']
content_list = dados['content'].tolist()

def sentiment_category(score):
    if score == 1:
        return 'Muito negativo'
    elif score == 2:
        return 'Negativo'
    elif score == 3:
        return 'Neutro'
    elif score == 4:
        return 'Positivo'
    elif score == 5:
        return 'Muito positivo'

dados['Sentiment Category'] = dados['Sentiment Score'].apply(sentiment_category)
category_order = ['Muito negativo','Negativo', 'Neutro', 'Positivo', 'Muito positivo']
dados['Sentiment Category'] = pd.Categorical(dados['Sentiment Category'], categories=category_order, ordered=True)

# VISÃO GERAL DOS DADOS
st.subheader('Visão geral dos dados:')
total_reviews = len(dados)
reviews_by_rating = dados['im_rating'].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)

general_view_df = pd.DataFrame({
    'Metric': ['Número total de reviews:', 'Reviews com ⭐', 'Reviews com ⭐⭐', 'Reviews com ⭐⭐⭐', 'Reviews com ⭐⭐⭐⭐', 'Reviews com ⭐⭐⭐⭐⭐'],
    'Count': [total_reviews] + reviews_by_rating.tolist()
})
st.table(general_view_df)

# DADOS CRUS
st.write('Primeiras linhas de dados crus:')
st.write(dados.head())

# FILTRANDO PARA O MES ATUAL
dados['date'] = pd.to_datetime(dados['date'])
dados['day'] = dados['date'].dt.to_period('D')

current_month = '2024-06'
june_data = dados[dados['date'].dt.to_period('M') == current_month]

avg_sentiment_per_day = june_data.groupby('day')['Sentiment Score'].mean().reset_index()
avg_sentiment_per_day['day'] = avg_sentiment_per_day['day'].dt.to_timestamp()

col1, col2 = st.columns(2)

with col1:
    st.subheader('Média do *Sentiment Score* por dia neste mês:')
    st.line_chart(avg_sentiment_per_day.set_index('day'))

with col2:
    st.subheader("Distribuição de ⭐ (avaliação de 1 a 5 estrelas)")
    rating_counts = dados['im_rating'].value_counts().sort_index()

    rating_to_star = {
        1: '⭐',
        2: '⭐⭐',
        3: '⭐⭐⭐',
        4: '⭐⭐⭐⭐',
        5: '⭐⭐⭐⭐⭐'
    }
    rating_counts.index = rating_counts.index.map(rating_to_star)
    st.bar_chart(rating_counts)

col3, col4 = st.columns(2)

with col3:
    st.subheader('Distribuição do *Sentiment Score*')
    sentiment_score_counts = dados['Sentiment Score'].value_counts().sort_index()
    st.bar_chart(sentiment_score_counts)

with col4:
    st.subheader('Contagem de Categorias de Sentimento')
    sentiment_category_counts = dados['Sentiment Category'].value_counts().reindex(category_order)
    st.bar_chart(sentiment_category_counts)

# MÉDIA DE SENTIMENT SCORE POR NUMERO DE ESTRELAS
st.subheader('Média de score de sentimento por número de estrelas')
avg_sentiment_per_rating = dados.groupby('im_rating')['Sentiment Score'].mean()
st.write(avg_sentiment_per_rating)

todasReviews = ' '.join(dados['content'])
todasReviewsClean = re.sub(r'[^a-zA-Z\s]', '', todasReviews).lower()
todasPalavras = todasReviewsClean.split()
word_counts = Counter(todasPalavras)

# REMOÇÃO DE STOPWORDS
stopwords = set(['the', 'and', 'to', 'of', 'in', 'i', 'it', 'for', 'is', 'that', 'on', 'with', 'as', 'was', 'this', 'but', 'are', 'have', 'be', 'you', 'not', 'my', 'or', 'at', 'if', 'so', 'they', 'we', 'me', 'one', 'can', 'all', 'by', 'an', 'there', 'from', 'your', 'will', 'has', 'had', 'about', 'like', 'would', 'what', 'out', 'just', 'up', 'which', 'when', 'their', 'more', 'also', 'some', 'no', 'could', 'were', 'them', 'do', 'time', 'any', 'how', 'only', 'than', 'us', 'its', 'who', 'get', 'been', 'am', 'new', 'then', 'a', 'chat', 'gpt'])
palavrasFiltradas = [palavra for palavra in todasPalavras if palavra not in stopwords]

contadorPalavrasFiltradas = Counter(palavrasFiltradas)

palavrasMaisComuns = contadorPalavrasFiltradas.most_common(20)

palavrasComuns = pd.DataFrame(palavrasMaisComuns, columns=['Palavra', 'Frequencia']).sort_values(by='Frequencia', ascending=False)

st.subheader('Top 20 palavras mais frequentes nas reviews')
st.table(palavrasComuns)

def getRecomendacaoChatGPT(reviews):
    prompt = (
        "Com base nas seguintes avaliações do aplicativo, forneça uma recomendação de negócio para melhorar ainda mais o aplicativo."
        "Destaque as principais áreas para melhoria e possíveis novas funcionalidades. Reviews:\n" + reviews
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Você é um assistente que sabe tudo sobre negócios."}, {"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return response.choices[0].message.content


todasReviews = ' '.join(palavrasFiltradas)
rec = getRecomendacaoChatGPT(todasReviews)

st.subheader("Recomendação de Negócio")
st.write(rec)
