import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title='Calculadora de reinvestimento de proventos',layout='wide')

def convert_date_format(date_str):
    return pd.to_datetime(date_str).strftime('%Y-%m-%d')

files_path = st.sidebar.text_input('Pasta com extratos')

# Lista para armazenar os dataframes de cada arquivo
dataframes = []

# Loop para percorrer todos os arquivos .xlsx na pasta
for arquivo in os.listdir(files_path):
    if arquivo.endswith('.xlsx'):
        caminho_arquivo = os.path.join(files_path, arquivo)
        # Lê o arquivo e adiciona ao dataframe
        df = pd.read_excel(caminho_arquivo,header=13)
        df = df.iloc[0:-19]
        dataframes.append(df)

# Combina todos os dataframes em um único
df = pd.concat(dataframes, ignore_index=True)

# Remove linhas duplicadas
df = df.drop_duplicates()

df['Movimentação'] = df['Movimentação'].apply(convert_date_format)
df['Liquidação'] = df['Liquidação'].apply(convert_date_format)

df = df.drop('Unnamed: 0',axis=1)
df = df.drop('Unnamed: 4',axis=1)

df['Tipo'] = df['Lançamento'].str.split(' DE').str[0]
df['Ativo'] = df['Lançamento'].str.split(' CLIENTES').str[1].str.split(' S/').str[0].str.split(' ').str[-1]
df = df.drop('Lançamento',axis=1)
df.loc[df['Valor (R$)']<0,'Tipo'] = 'RETIRADA'
df = df[['Movimentação','Liquidação','Tipo','Ativo','Valor (R$)','Saldo (R$)',]]


lista_meses =  st.sidebar.multiselect(options=pd.to_datetime(df['Movimentação']).dt.month.unique(),label='Meses selecionados',default=list(pd.to_datetime(df['Movimentação']).dt.month.unique()))
lista_anos = st.sidebar.multiselect(options=pd.to_datetime(df['Movimentação']).dt.year.unique(),label='Anos selecionados',default=list(pd.to_datetime(df['Movimentação']).dt.year.unique()))

mask_mes = pd.to_datetime(df['Movimentação']).dt.month.isin(lista_meses)
mask_ano = pd.to_datetime(df['Movimentação']).dt.year.isin(lista_anos)


lista_ativos = st.sidebar.multiselect(options=df.loc[mask_mes & mask_ano,'Ativo'].unique(),label='Ativos selecionados')
mask_ativos = df['Ativo'].isin(lista_ativos)

dado_all = df.loc[mask_mes & mask_ano].groupby('Ativo').sum()['Valor (R$)'].div(df.loc[mask_mes & mask_ano].groupby('Ativo').sum()['Valor (R$)'].sum())
dado_target = df.loc[mask_mes & mask_ano & mask_ativos].groupby('Ativo').sum()['Valor (R$)'].div(df.loc[mask_mes & mask_ano & mask_ativos].groupby('Ativo').sum()['Valor (R$)'].sum())
resto = dado_all[~dado_all.index.isin(list(dado_target.index))]*df.loc[mask_mes & mask_ano].groupby('Ativo').sum()['Valor (R$)'].sum()

col1,col2,col3 = st.columns(3)
with col1:
    st.write('Total do recebido no período')
    st.write(f'{np.round(df.dropna().loc[mask_mes & mask_ano,'Valor (R$)'].sum(),2)} R$')
    st.bar_chart(df.dropna().loc[mask_mes & mask_ano].groupby('Ativo').sum()['Valor (R$)'],horizontal=True)
with col2:
    st.write(df.loc[mask_mes&mask_ano].dropna())
with col3:
    st.write('Valoers para os ativos selecionados')
    st.write(df.loc[df['Ativo'].isin(list(dado_target.index))].groupby('Ativo').sum()['Valor (R$)'] + dado_target*np.sum(resto))
