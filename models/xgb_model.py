import xgboost as xgb
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_trained_model():
    # Carregar o modelo salvo em formato JSON dentro da pasta models
    model = xgb.Booster()
    model.load_model('models/modelo_idh_xgboost_6vars_scaled.json')  # Caminho atualizado
    
    # Carregar o scaler dentro da pasta models
    with open('models/scaler_6vars.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    # Definir as features usadas no modelo
    features = [
        '% de pobres',
        'Ativos com Alto Nível Educacional',
        'Produtividade',
        'Médicos por milhares de habitantes',
        'Média Salarial',
        'PIB Municipal'
    ]
    
    return model, scaler, features

def predict_idh(model, scaler, features, input_data):
    # Garantir que input_data tenha as colunas corretas na ordem esperada
    input_data_scaled = scaler.transform(input_data[features])
    dmatrix = xgb.DMatrix(input_data_scaled, feature_names=features)
    prediction = model.predict(dmatrix)
    return prediction[0]  # Retorna o valor previsto para o primeiro (e único) registro

# Função opcional para validação com valores originais (se necessário)
def validate_with_original_data(model, scaler, features, df):
    original_values = df[features + ['IDH']].copy()
    return original_values