import streamlit as st
import zipfile
import xml.etree.ElementTree as ET
import io

st.set_page_config(page_title="Removedor de Pinos KML/KMZ", page_icon="📍")

st.title("Removedor de PIN(s) em arquivos KML/KMZ")
st.write("Faça o upload do seu arquivo de mapa para remover automaticamente todos os marcadores de ponto (pinos), mantendo polígonos e linhas intactos.")

# Botão para inserir o arquivo
uploaded_file = st.file_uploader("Envie seu arquivo (.KMZ ou .KML)", type=["kml", "kmz"])

if uploaded_file is not None:
    file_name = uploaded_file.name
    st.write(f"Arquivo **{file_name}** carregado! Processando...")

    # Variáveis de controle
    is_kmz = file_name.lower().endswith('.kmz')
    kml_content = None

    # Leitura do arquivo
    try:
        if is_kmz:
            with zipfile.ZipFile(uploaded_file, 'r') as kmz:
                kml_content = kmz.read('doc.kml')
        else:
            kml_content = uploaded_file.read()
    except KeyError:
        st.error("Erro: Não foi possível encontrar o arquivo 'doc.kml' dentro do KMZ.")
        st.stop()
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        st.stop()

    # Prepara a leitura do XML evitando problemas com as tags
    ET.register_namespace('', 'http://www.opengis.net/kml/2.2')
    
    try:
        root = ET.fromstring(kml_content)
    except Exception as e:
        st.error(f"Erro ao analisar a estrutura do mapa (XML): {e}")
        st.stop()

    # Varre o arquivo procurando Pinos e apaga todos eles
    pinos_removidos = 0
    for parent in root.iter():
        for child in list(parent):
            if child.tag.endswith('Placemark'):
                # Verifica se esse Placemark é um Ponto (Pin)
                if any(subchild.tag.endswith('Point') for subchild in child):
                    parent.remove(child)  # Apaga o pin
                    pinos_removidos += 1

    if pinos_removidos > 0:
        st.success(f"✅ Sucesso! {pinos_removidos} pinos foram deletados.")
    else:
        st.info("Nenhum pino foi encontrado neste arquivo.")

    # Salva as alterações em memória (BytesIO)
    tree = ET.ElementTree(root)
    out_kml = io.BytesIO()
    tree.write(out_kml, encoding='utf-8', xml_declaration=True)
    out_kml.seek(0) # Retorna o ponteiro para o início do arquivo em memória

    st.write("👇 **BAIXE SEU ARQUIVO LIMPO ABAIXO** 👇")

    # Prepara o download de acordo com o arquivo original
    if is_kmz:
        out_kmz = io.BytesIO()
        with zipfile.ZipFile(out_kmz, 'w', zipfile.ZIP_DEFLATED) as novo_kmz:
            novo_kmz.writestr('doc.kml', out_kml.getvalue())
        out_kmz.seek(0)
        
        st.download_button(
            label="Baixar mapa SEM pinos (.kmz)",
            data=out_kmz,
            file_name="mapa_SEM_pinos.kmz",
            mime="application/vnd.google-earth.kmz"
        )
    else:
        novo_nome = file_name.replace('.kml', '_SEM_pinos.kml')
        # Ajuste de caixa para extensões maiúsculas (.KML)
        novo_nome = novo_nome.replace('.KML', '_SEM_pinos.kml')
        
        st.download_button(
            label="Baixar mapa SEM pinos (.kml)",
            data=out_kml,
            file_name=novo_nome,
            mime="application/vnd.google-earth.kml+xml"
        )
