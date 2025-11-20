import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from kiwipiepy import Kiwi
from collections import Counter


class TextAnalyzer:
    @staticmethod
    @st.cache_resource
    def get_kiwi():
        return Kiwi()

    @staticmethod
    def get_stopwords():
        return [
            '이', '그', '저', '것', '수', '등', '및', '위해', '통해', '대한', '때문',
            '관련', '가장', '지난', '최근', '바로', '경우', '중', '속',
            '기자', '기사', '뉴스', '언론사', '언론', '취재', '사람', '우리', '생각',
            '콘텐츠', '미디어', '방송', '사회'
        ]


class AnalysisEngine:
    def __init__(self, metrics_df, contents_df, demo_df):
        self.metrics_df = metrics_df
        self.contents_df = contents_df
        self.demo_df = demo_df

    def calculate_scores(self, w_comment, w_like, w_view, top_n):
        summary = self.metrics_df.groupby('article_id').agg({
            'comments': 'sum',
            'likes': 'sum',
            'views_total': 'sum'
        }).reset_index()

        scaler = MinMaxScaler()
        cols = ['comments', 'likes', 'views_total']
        summary[cols] = scaler.fit_transform(summary[cols])

        summary['score'] = (
                summary['comments'] * w_comment +
                summary['likes'] * w_like +
                summary['views_total'] * w_view
        )

        return summary.sort_values(by='score', ascending=False).head(top_n)

    def get_demographics_data(self, top_article_ids):
        top_demo = self.demo_df[self.demo_df['article_id'].isin(top_article_ids)].copy()
        top_demo['group'] = top_demo['age_group'] + " " + top_demo['gender']
        return top_demo

    def generate_wordcloud_data(self, top_article_ids):
        target_df = self.contents_df[self.contents_df['article_id'].isin(top_article_ids)]
        text = " ".join(target_df['content'].astype(str))

        kiwi = TextAnalyzer.get_kiwi()
        tokens = kiwi.analyze(text)
        nouns = [t.form for t in tokens[0][0] if t.tag in {'NNG', 'NNP'}]

        stopwords = TextAnalyzer.get_stopwords()
        filtered = [w for w in nouns if len(w) > 1 and w not in stopwords]
        return Counter(filtered)

    def run_lda(self, top_article_ids, n_topics):
        target_df = self.contents_df[self.contents_df['article_id'].isin(top_article_ids)].copy()
        stopwords = TextAnalyzer.get_stopwords()
        kiwi = TextAnalyzer.get_kiwi()

        docs = []
        for content in target_df['content'].astype(str):
            tokens = kiwi.analyze(content)
            nouns = [t.form for t in tokens[0][0] if t.tag in {'NNG', 'NNP'}]
            docs.append(" ".join([w for w in nouns if len(w) > 1 and w not in stopwords]))

        vectorizer = TfidfVectorizer(max_df=0.85, min_df=2)
        matrix = vectorizer.fit_transform(docs)

        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(matrix)

        return lda, vectorizer.get_feature_names_out()
