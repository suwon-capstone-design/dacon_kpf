import pandas as pd
import streamlit as st
from app.data_loader import DataLoader
from app.analyzer import AnalysisEngine
from app.ui_components import DashboardUI

st.set_page_config(page_title="신문과방송 독자 데이터 분석 솔루션", layout="wide")


def main():
    ui = DashboardUI()
    w_c, w_l, w_v, top_n, n_topics = ui.render_sidebar()
    st.session_state['n_topics'] = n_topics

    loader = DataLoader()
    m_df, c_df, d1, d2 = loader.load_data()

    st.title("📰 신문과방송 데이터 기반 인사이트 솔루션")

    if m_df is not None:
        d_df = pd.concat([d1, d2], ignore_index=True)
        engine = AnalysisEngine(m_df, c_df, d_df)

        # 1. 지표 분석
        top_metrics = engine.calculate_scores(w_c, w_l, w_v, top_n)
        ui.render_metrics_chart(top_metrics, w_c, w_l, w_v)

        top_ids = top_metrics['article_id'].tolist()
        st.divider()

        # 2. 독자층 분석
        ui.render_demographics(engine, top_ids)
        st.divider()

        # 3. 텍스트 분석
        ui.render_keywords(engine, top_ids)


if __name__ == "__main__":
    main()
