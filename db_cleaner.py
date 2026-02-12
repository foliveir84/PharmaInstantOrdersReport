import sqlite3
import pandas as pd
import numpy as np
import os

def get_cleaned_data(db_path='bd_order_history.db'):
    """
    Le a base de dados de encomendas e aplica os filtros de limpeza e normalizacao.
    Mantem registos sem fornecedor para calculo preciso de ROI e monitorizacao.
    """
    if not os.path.exists(db_path):
        return None

    conn = sqlite3.connect(db_path)
    try:
        query = "SELECT * FROM ORDER_HISTORY"
        df = pd.read_sql_query(query, conn)
    except Exception:
        return None
    finally:
        conn.close()

    # 1. Tratamento de Tipos e Nulos
    cols_numeric = ['CNP', 'QT_TARGET', 'QT_STOCK', 'QT_A_ENCOMENDAR', 'QT_DISPONIVEL', 'QT_ENCOMENDADA']
    for col in cols_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Limpeza de strings basicas
    if 'FORNECEDOR' in df.columns:
        df['FORNECEDOR'] = df['FORNECEDOR'].fillna('').str.strip()

    # 2. Bug Fix (QT_A_ENCOMENDAR == 0 -> QT_ENCOMENDADA = 0)
    bug_condition = (df['QT_A_ENCOMENDAR'] == 0) & (df['QT_ENCOMENDADA'] > 0)
    df.loc[bug_condition, 'QT_ENCOMENDADA'] = 0

    # 3. Normalizacao de Descricoes
    if 'CNP' in df.columns and 'DESCRICAO' in df.columns:
        mapeamento_nomes = df.groupby('CNP')['DESCRICAO'].first().to_dict()
        df['DESCRICAO'] = df['CNP'].map(mapeamento_nomes)

    # 4. Tratamento de Datas
    if 'TIME_STAMP' in df.columns:
        df['TIME_STAMP'] = pd.to_datetime(df['TIME_STAMP'], errors='coerce')
        df = df.dropna(subset=['TIME_STAMP'])
        df['Date'] = df['TIME_STAMP'].dt.date
    
    df['PRODUTO_DISPLAY'] = df['CNP'].astype(str) + " - " + df['DESCRICAO'].fillna('')

    return df

def calculate_session_roi(df, custo_hora, session_threshold_minutes=60, discount_per_iteration=20):
    """
    Calcula o ROI baseado na duracao real das sessoes.
    Returns: num_sessoes, total_iters, total_horas (float), valor_poupado
    """
    if df.empty:
        return 0, 0, 0.0, 0.0

    df_sorted = df.sort_values('TIME_STAMP')
    df_sorted['gap'] = df_sorted['TIME_STAMP'].diff()
    df_sorted['new_session'] = df_sorted['gap'] > pd.Timedelta(minutes=session_threshold_minutes)
    df_sorted['session_id'] = df_sorted['new_session'].cumsum()
    
    session_metrics = []
    for sess_id, group in df_sorted.groupby('session_id'):
        start = group['TIME_STAMP'].min()
        end = group['TIME_STAMP'].max()
        raw_duration = (end - start).total_seconds()
        
        unique_iters = group.groupby(['TIME_STAMP', 'CNP']).size().shape[0]
        correction = unique_iters * discount_per_iteration
        adjusted_duration = max(0, raw_duration - correction)
        
        session_metrics.append({
            'duration': adjusted_duration,
            'iters': unique_iters
        })
    
    total_seconds = sum(m['duration'] for m in session_metrics)
    total_iters = sum(m['iters'] for m in session_metrics)
    
    total_horas = total_seconds / 3600
    valor_poupado = total_horas * custo_hora
    num_sessoes = len(session_metrics)
    
    return num_sessoes, total_iters, total_horas, valor_poupado
