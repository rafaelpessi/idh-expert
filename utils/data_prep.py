import pandas as pd

def load_and_filter_data(path):
    # Carregar dados
    df = pd.read_csv(path)
    
    # Filtrar municípios até 100k habitantes e criar uma cópia
    df_filtered = df[df['População residente'] <= 100000].copy()
    
    return df_filtered

def get_municipality_data(df, municipality):
    # Verificar nome correto da coluna
    # return df[df['Município'] == municipality].iloc[0]  # versão antiga
    return df[df['nomeLocalidade'] == municipality].iloc[0]  # nova versão
