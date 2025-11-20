import pandas as pd
import os
import streamlit as st


class DataLoader:
    def __init__(self, data_dir='./data/'):
        self.data_dir = data_dir

    @st.cache_data
    def load_data(_self):
        try:
            print("--- 데이터 로드 시작 ---")

            metrics_df = _self._load_optimized('article_metrics_monthly.xlsx')
            contents_df = pd.read_excel(f'{_self.data_dir}contents.xlsx')
            print(f"✅ contents.xlsx 로드 완료")

            demo_part1 = _self._load_optimized('demographics_part001.xlsx')
            demo_part2 = _self._load_optimized('demographics_part002.xlsx')

            # 데이터 타입 변환
            metrics_df['article_id'] = metrics_df['article_id'].astype(str)
            contents_df['article_id'] = contents_df['article_id'].astype(str)
            demo_part1['article_id'] = demo_part1['article_id'].astype(str)
            demo_part2['article_id'] = demo_part2['article_id'].astype(str)

            print("--- 모든 데이터 로드 완료! ---")
            return metrics_df, contents_df, demo_part1, demo_part2
        except Exception as e:
            st.error(f"데이터 로드 중 오류 발생: {e}")
            print(f"❌ 오류 발생: {e}")
            return None, None, None, None

    def _load_optimized(self, filename):
        base_name = filename.split('.')[0]
        feather_path = f'{self.data_dir}{base_name}.feather'
        excel_path = f'{self.data_dir}{filename}'

        if os.path.exists(feather_path):
            print(f"🚀 [고속 로딩] {feather_path} 읽는 중...")
            return pd.read_feather(feather_path)
        else:
            print(f"🐢 [최초 실행] {excel_path} 변환 중... (잠시만 기다려주세요)")
            df = pd.read_excel(excel_path)
            try:
                df.to_feather(feather_path)
                print(f"💾 {feather_path} 저장 완료!")
            except Exception as e:
                print(f"⚠️ Feather 저장 실패 (무시하고 진행): {e}")
            return df
