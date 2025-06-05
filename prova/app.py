import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os


def moeda_para_float(valor):
    valor = str(valor).strip()
    valor = valor.replace("R$", "").replace("$", "").replace(".", "").replace(",", ".").replace(" ", "")
    if re.match(r"^\(.*\)$", valor):  
        valor = "-" + valor.strip("()")
    if valor == "-" or valor == "":
        valor = "0"
    return float(valor)


@st.cache_data
def carregar_dados():
    df = pd.read_csv("dataset.csv", sep=";", encoding="utf-8")
    df.columns = df.columns.str.strip()

    colunas_moeda = [
        "Units Sold", "Manufacturing Price", "Sale Price", "Gross Sales",
        "Discounts", "Sales", "COGS", "Profit"
    ]
    for coluna in colunas_moeda:
        df[coluna] = df[coluna].apply(moeda_para_float)

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df

if not os.path.exists("dataset.csv"):
    st.error("Arquivo 'dataset.csv' não encontrado no diretório atual. Coloque o arquivo na mesma pasta do app.")
else:
    st.title("📊 Dashboard de Vendas")

    df = carregar_dados()

    anos = st.multiselect("Ano", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
    paises = st.multiselect("País", sorted(df["Country"].unique()), default=sorted(df["Country"].unique()))
    produtos = st.multiselect("Produto", sorted(df["Product"].unique()), default=sorted(df["Product"].unique()))

    df_filtrado = df[
        (df["Year"].isin(anos)) &
        (df["Country"].isin(paises)) &
        (df["Product"].isin(produtos))
    ]


    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total de Vendas", f"R$ {df_filtrado['Sales'].sum():,.2f}")
    col2.metric("📦 Total Vendido", f"{df_filtrado['Units Sold'].sum():,.0f} unidades")
    col3.metric("📈 Lucro Total", f"R$ {df_filtrado['Profit'].sum():,.2f}")

    st.markdown("---")


    st.subheader("🗓️ Vendas ao Longo do Tempo")
    vendas_tempo = df_filtrado.groupby("Date")["Sales"].sum().reset_index()
    fig_linha = px.line(vendas_tempo, x="Date", y="Sales", title="Vendas por Data")
    st.plotly_chart(fig_linha, use_container_width=True)

    st.subheader("🌍 Vendas por País")
    vendas_pais = df_filtrado.groupby("Country")["Sales"].sum().reset_index()
    fig_barra = px.bar(vendas_pais, x="Country", y="Sales", title="Vendas por País")
    st.plotly_chart(fig_barra, use_container_width=True)

    st.subheader("📦 Vendas por Produto")
    vendas_produto = df_filtrado.groupby("Product")["Sales"].sum().reset_index()
    fig_pizza = px.pie(vendas_produto, names="Product", values="Sales", title="Participação por Produto")
    st.plotly_chart(fig_pizza, use_container_width=True)


    st.subheader("🧠 Insights Rápidos")
    produto_top = vendas_produto.sort_values(by="Sales", ascending=False).iloc[0]
    pais_top = vendas_pais.sort_values(by="Sales", ascending=False).iloc[0]

    st.markdown(f"- 🔝 O produto mais vendido é **{produto_top['Product']}** com R$ {produto_top['Sales']:,.2f} em vendas.")
    st.markdown(f"- 🌐 O país com maior volume de vendas é **{pais_top['Country']}** com R$ {pais_top['Sales']:,.2f}.")
