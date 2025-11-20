import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from app.utils import FontManager


class DashboardUI:
    def __init__(self):
        self.font_name = FontManager.set_pyplot_font()

    def render_sidebar(self):
        st.sidebar.header("⚙️ 분석 환경 설정")

        st.sidebar.subheader("1. 가중치 설정")
        w_c = st.sidebar.slider("댓글 가중치", 0.0, 1.0, 0.5, 0.1)
        w_l = st.sidebar.slider("좋아요 가중치", 0.0, 1.0, 0.3, 0.1)
        w_v = st.sidebar.slider("조회수 가중치", 0.0, 1.0, 0.2, 0.1)

        st.sidebar.subheader("2. 분석 옵션")
        top_n = st.sidebar.slider("분석 대상 상위 기사 수", 5, 50, 20)
        n_topics = st.sidebar.number_input("토픽 모델링 주제 수", 2, 10, 3)

        return w_c, w_l, w_v, top_n, n_topics

    def render_metrics_chart(self, top_df, w_c, w_l, w_v):
        st.subheader("📊 핵심 지표 분석 및 조언")

        col1, col2 = st.columns([3, 1])

        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='score', y='article_id', data=top_df, palette='viridis', ax=ax)
            ax.set_title(f"종합 점수 상위 TOP {len(top_df)}")
            st.pyplot(fig)

        with col2:
            st.markdown("### 💡 AI 전략 조언")
            top_article = top_df.iloc[0]['article_id']
            st.info(f"""
            현재 설정(댓글 {w_c * 100:.0f}%, 좋아요 {w_l * 100:.0f}%) 기준,
            가장 영향력 있는 기사는 **ID: {top_article}** 입니다.

            사용자 참여 유도를 위해 해당 기사의 포맷을 벤치마킹하세요.
            """)

    def render_demographics(self, engine, top_ids):
        st.subheader("👥 독자층 심층 분석")
        demo_df = engine.get_demographics_data(top_ids)

        tab1, tab2 = st.tabs(["누적 막대 그래프", "히트맵 분석"])

        summary = demo_df.groupby(['article_id', 'group'])['ratio'].mean().unstack().fillna(0)
        summary = summary.loc[top_ids]

        with tab1:
            fig, ax = plt.subplots(figsize=(12, 8))
            summary.plot(kind='barh', stacked=True, ax=ax, colormap='tab20')
            ax.invert_yaxis()
            ax.set_title("기사별 독자층 분포")
            ax.legend(bbox_to_anchor=(1.05, 1))
            st.pyplot(fig)

        with tab2:
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(summary, cmap='viridis', annot=True, fmt='.1f', ax=ax)
            ax.set_title("독자층 히트맵")
            st.pyplot(fig)

        # [수정된 로직] 전체/세부 타겟 분리 분석
        mean_values = summary.mean()
        main_target = mean_values.idxmax()  # 전체 포함 1등 (보통 '전체 여' 등)

        # '전체' 글자가 들어간 컬럼을 제외하고 다시 계산
        filtered_values = mean_values[~mean_values.index.str.contains('전체')]
        sub_target = filtered_values.idxmax() if not filtered_values.empty else "분석 불가"

        message = f"📌 **핵심 타겟 분석:** 현재 상위 콘텐츠의 주 소비층은 **'{main_target}'** 입니다."

        # 만약 1등이 '전체' 카테고리라면, 추가 멘트를 붙임
        if "전체" in main_target:
            message += f"\n\n (※ **'전체'** 통계는 누적 데이터로 분포 분석에 한계가 있으므로, 이를 제외하면 **'{sub_target}'** 그룹이 가장 높은 분포를 보입니다.)"

        st.success(message)

    def render_keywords(self, engine, top_ids):
        st.subheader("☁️ 키워드 & 토픽 분석")
        col1, col2 = st.columns(2)

        with col1:
            counts = engine.generate_wordcloud_data(top_ids)
            wc = WordCloud(
                font_path=FontManager.get_font_path(),
                background_color='white', width=800, height=600
            ).generate_from_frequencies(counts)

            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

            top_k = [w[0] for w in counts.most_common(3)]
            st.caption(f"🔑 **핵심 키워드:** {', '.join(top_k)}")

        with col2:
            st.markdown("**LDA 토픽 모델링 결과**")
            n_topics = st.session_state.get('n_topics', 3)
            lda, features = engine.run_lda(top_ids, n_topics)

            for idx, topic in enumerate(lda.components_):
                top_features = [features[i] for i in topic.argsort()[:-11:-1]]
                st.markdown(f"**Topic {idx + 1}:** {', '.join(top_features)}")
