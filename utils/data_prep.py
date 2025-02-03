import pandas as pd
import streamlit as st

def load_and_filter_data(path):
    # Carregar dados
    df = pd.read_csv(path)
    
    # Filtrar municípios até 100k habitantes e criar uma cópia
    df_filtered = df[df['População residente'] <= 100000].copy()
    
    return df_filtered

@st.cache_data
def get_municipality_data(df, municipality):
    return df[df['nomeLocalidade'] == municipality].iloc[0]