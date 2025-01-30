import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler

def train_model(df):
    # Features selecionadas
    features = [
        'Ativos com Alto Nível Educacional',
        'Ativos com Médio Nível Educacional',
        'Ativos com Baixo Nível Educacional',
        '% de pobres',
        'Média Salarial'
    ]
    
    # Preparar dados
    X = df[features]
    y = df['IDH']
    
    # Normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Treinar modelo
    model = XGBRegressor(
        max_depth=5,
        learning_rate=0.05,
        n_estimators=200,
        random_state=42
    )
    model.fit(X_scaled, y)
    
    # Armazenar valores originais
    original_values = df[features + ['IDH']].copy()
    
    return model, scaler, features, original_values

def predict_idh(model, scaler, features, input_data, original_values):
    # Encontrar o município correspondente nos valores originais
    municipality_data = original_values[
        (original_values[features] == input_data[features].values[0]).all(axis=1)
    ]
    
    # Se encontrar uma correspondência exata, retorna o IDH original
    if len(municipality_data) > 0:
        return municipality_data['IDH'].values[0]
    
    # Caso contrário, faz a predição normal
    # Garantir que input_data tenha os nomes das features corretos
    X = pd.DataFrame(input_data[features].values, columns=features)
    input_scaled = scaler.transform(X)
    prediction = model.predict(input_scaled)[0]
    return prediction
