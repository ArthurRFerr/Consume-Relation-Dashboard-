import streamlit as st
import pandas as pd 
import plotly.express as px
import numpy as np
import streamlit_authenticator as stauth
import bcrypt as bcrypt

st.markdown(
     "<h1 style='color:#fb9800;'>Consumo e Descarte (Eventos)</h1>",
 unsafe_allow_html=True
    )
   

# -------------------------Caminho do arquivo
caminho_arquivo = "data/MediaEventosTotalDataAnalysis.xlsx" #Define o caminho do arquivo pra análise


# -------------------------Mapeamento
mapeamento_colunas = {
    "ALIMENTOS": {
        "data": "data",
        "item": "item",
        "consumo por cliente": "consumo por cliente",
        "consumo por cliente teorico": "consumo por cliente teorico",
        "descarte por cliente": "descarte por cliente",
        "evento": "evento"
    },
    "BEBIDAS": {
        "data": "data",
        "item": "item",
        "consumo por cliente": "consumo por cliente",
        "consumo por cliente teorico": "consumo por cliente teorico",
        "descarte por cliente": "descarte por cliente",
        "evento": "evento"
    }
}


def padronizar_df(df, aba):
    col_map  = mapeamento_colunas[aba]
    df_pad = df.rename(columns={v: k for k, v in col_map.items()})
    return df_pad

#-----------------------Carregamento dos dados

if caminho_arquivo.endswith((".xlsx", ".xls")):
    df_alimentos = pd.read_excel(caminho_arquivo, sheet_name="ALIMENTOS")
    df_bebidas   = pd.read_excel(caminho_arquivo, sheet_name="BEBIDAS")
elif caminho_arquivo.endswith(".csv"):
    df_alimentos = pd.read_csv(caminho_arquivo)
    df_bebidas  = pd.read_csv(caminho_arquivo)
else:
    st.error("Formato de arquivo não suportado!")
    st.stop()



# -------------------------Padronização dos DataFrames
df_alimentos = padronizar_df(df_alimentos, "ALIMENTOS")
df_bebidas   = padronizar_df(df_bebidas, "BEBIDAS")

st.sidebar.header("Filtros")
tipo = st.sidebar.radio("Selecione a categoria:", ["Alimentos", "Bebidas"]) 


#-------------------------Padronização das colunas
def padroniza_colunas(df):
    df.columns = df.columns.str.strip()                 # remove espaços extras
    df.columns = df.columns.str.lower()                 # deixa tudo minúsculo
    df.columns = df.columns.str.replace("ã","a")        # remove acentos
    df.columns = df.columns.str.replace("é","e")
    return df
df_alimentos = padroniza_colunas(df_alimentos)
df_bebidas   = padroniza_colunas(df_bebidas)


#--------------------------Converte datas
df_alimentos["data"] = pd.to_datetime(df_alimentos["data"], dayfirst=True, errors="coerce")
df_bebidas["data"]   = pd.to_datetime(df_bebidas["data"], dayfirst=True, errors="coerce")




# -------------------------Função auxiliar p/ plotar
def mostrar_dashboard(df, titulo):
    #if df is None or not set(["DATA", "Item", "Consumo por cliente", "Consumo por cliente teorico", "descarte por cliente"]).issubset(df.columns):
        #st.warning(f"Dados insuficientes para {titulo}.")
        #return
    
    itens = df["item"].unique().tolist()
    item_escolhido = st.sidebar.selectbox(f"Selecione o Item ({titulo}):", itens, key=titulo)

    st.subheader(titulo)

    df_filtrado = df[df["item"] == item_escolhido]

    if st.checkbox(f"Mostrar dados filtrados ({titulo})", key="check_"+titulo):
        st.dataframe(df_filtrado, use_container_width=True, height=400)

    #st.write("Colunas disponíveis em df_filtrado:", df_filtrado.columns.tolist()) #-----USAR SE NECESSÁRIO PRA DEBUGAR
    #st.write("Colunas Alimentos:", df_alimentos.columns.tolist())
    #st.write("Colunas Bebidas:", df_bebidas.columns.tolist())

    

    colunas_alvo = ["consumo por cliente", "consumo por cliente teorico", "descarte por cliente"]
    colunas_validas = [col for col in colunas_alvo if col in df_filtrado.columns]

    if not colunas_validas:
        st.warning(f"Nenhuma das colunas esperadas está presente em {titulo}.")
        return
   
    if "evento" in df_filtrado.columns:
        eventos = df_filtrado["evento"].dropna().unique()
        nome_evento = ", ".join(eventos) if len(eventos) > 0 else "Não informado"
    else:
        nome_evento = "Não informado"

    

    #----------------------- Long format
    df_long = df_filtrado.melt(
        id_vars=["data"],
        value_vars=colunas_validas,
        var_name="tipo",
        value_name="valor"
    ).dropna(subset=["valor"]).sort_values("data")


    #-----------------------Plot
    fig = px.line(
        df_long,
        x="data",
        y="valor",
        color="tipo",
        markers=True,
        color_discrete_map={
            "consumo por cliente": "lightblue",
            "consumo por cliente teorico": "darkblue",
            "descarte por cliente": "orange"
        },
        title=f"Relação Consumo Real vs Consumo Teórico  ({titulo} - {item_escolhido})",
        labels={"valor": "Consumo", "data": "data",  "tipo": "categoria"},
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------Exibição condicional
if tipo == "Alimentos":
    mostrar_dashboard(df_alimentos, "Alimentos")
elif tipo == "Bebidas":
     mostrar_dashboard(df_bebidas, "Bebidas")



