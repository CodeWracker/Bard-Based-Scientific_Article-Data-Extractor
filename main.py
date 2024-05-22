import os
import time
import asyncio
import pandas as pd
import PyPDF2
from EdgeGPT.EdgeUtils import Query, Cookie
import csv


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TABLE_MODEL_MD = "No|Title|Authors|Year|Source|Battery Type|Control Method|Control Location|SoC Estimation Technique|Control Parameters|Energy Efficiency|Differences (Li vs. Pb-Acid)|Battery Capacity|System Power|Energy Source|Implementation Challenges|PWM Circuit Notes|DC-DC Converter Used|Additional Notes"
columns = []
for col in TABLE_MODEL_MD.split('|'):
    columns.append(col.strip())
print(columns)

TABLE_MODEL_DESCRIPTION = """
**Descrição das Colunas:**

- **No**: Número de referência do artigo.
- **Title**: Título do artigo.
- **Authors**: Autor(es) do artigo.
- **Year**: Ano de publicação.
- **Source**: Fonte ou revista onde o artigo foi publicado.
- **Battery Type**: Tipo de bateria estudada no artigo.
- **Control Method**: Método utilizado para controlar a tensão e corrente.
- **Control Location**: Local onde o controle foi implementado (por exemplo, ESP, Arduino).
- **SoC Estimation Technique**: Técnica usada para estimar o estado de carregamento da bateria.
- **Control Parameters**: Dados coletados para realizar o controle, como tensão e corrente de diferentes componentes.
- **Energy Efficiency**: Eficiência energética do método proposto.
- **Differences (Li vs. Pb-Acid)**: Diferenças notadas entre baterias de lítio e chumbo-ácido.
- **Battery Capacity**: Capacidade da bateria usada no estudo.
- **System Power**: Potência total do sistema estudado.
- **Energy Source**: Fonte de energia utilizada (por exemplo, fotovoltaica).
- **Implementation Challenges**: Desafios encontrados durante a implementação do método.
- **PWM Circuit Notes**: Anotações específicas sobre o circuito PWM utilizado.
- **DC-DC Converter Used**: Indicação se um conversor DC-DC foi usado no estudo.
- **Additional Notes**: Qualquer outra observação ou informação relevante sobre o artigo.
"""

def cut_text(text, cut_length=1000):
    if len(text) > cut_length:
        return text[:-cut_length]
    else:
        print("Texto não pode ser cortado mais")
    return text

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ''.join(page.extract_text() for page in reader.pages)

def query_article_info(pdf_text):
    while True:
        query_text = f'Leia o artigo abaixo e preencha a tabela com as informações necessárias (somente gere texto, eu NÃO quero que você faça nada alem de suas capacidades), segundo o modelo de markdown (a sua resposta deve ser APENAS o texto da tabela preenchida e não use virgula, se precisar separar algo use ; e se precisar aspas use aspas dupla "):\n\n{TABLE_MODEL_MD}\n{TABLE_MODEL_DESCRIPTION}n\n\nArtigo:\n\n{pdf_text}'

        print(f"Tentando a query com o texto com {len(pdf_text)} caracteres...")
        try:
            q = Query(query_text)
        except Exception as e:
            print(f"Erro ao criar a query: {e}")
            print("Diminuindo o texto em 10.000 caracteres")
            pdf_text = cut_text(pdf_text, 10000)
            time.sleep(5)
            continue
        try:
            response = str(q)
        except Exception as e:
            print(f"Erro ao converter a query: {e}")
            print("Diminuindo o texto em 10.000 caracteres")
            pdf_text = cut_text(pdf_text, 10000)
            time.sleep(5)
            continue
        print(f"Resposta obtida com {len(response)} caracteres: {response[:100]}...")
        if all(keyword in response for keyword in [columns[0], columns[1], columns[-1]]):
            #  escreve a resposta em um temp_resp.txt
            with open('temp_resp.txt', 'w', encoding='utf-8') as f:
                f.write(response)
            print("Resposta obtida com sucesso")
            return response
        else:
            print("Erro na resposta, o cabeçalho não foi encontrado")
            print("Diminuindo o texto em 1.000 caracteres")
            pdf_text = cut_text(pdf_text, 1000)
            time.sleep(5)
        

def process_query_response(response):
    response = '|'+response[response.find(columns[0]):]
    # se os 2 primeiros caracteres forem || substitui por |
    if response[:2] == '||':
        # remove o primeiro |
        response = response[1:]
    if all(keyword in response for keyword in [columns[0], columns[1], columns[-1]]):
        with open('temp.csv', 'w', encoding='utf-8') as f:
            f.write(response.replace(',',';').replace('|', ','))
        
        # Ler o CSV sem cabeçalho
        df_temp = pd.read_csv('temp.csv', header=None, sep=',', quoting=csv.QUOTE_ALL, quotechar='"', engine='python')
        
        # Determinar o número máximo de colunas
        max_columns = df_temp.shape[1]
        
        # Criar uma lista de nomes de coluna
        col_names = [f'col_{i}' for i in range(1, max_columns + 1)]
        
        # Ler o CSV novamente com os nomes de coluna corretos
        df = pd.read_csv('temp.csv', names=col_names, sep=',', quoting=csv.QUOTE_ALL, quotechar='"', engine='python')
        
        # Se você quiser que as primeiras linhas do arquivo original sejam o cabeçalho, você pode fazer:
        df.columns = df.iloc[0]
        df = df.drop(0).reset_index(drop=True)
        
        return df
    return None

if __name__ == "__main__":
    pdfs = [pdf for pdf in os.listdir('./PDFs') if pdf.endswith('.pdf')]    
    df_final = pd.DataFrame(columns=columns)


    for pdf in pdfs:
        print(f"\n\nAnalisando o arquivo {pdf}...")
        # verifica se o arquivo é mesmo um pdf
        if not pdf.endswith('.pdf'):
            print(f"O arquivo {pdf} não é um pdf")
            continue
        pdf_text = extract_text_from_pdf(os.path.join('./PDFs', pdf))
        while True:
            response = query_article_info(pdf_text)
            try:
                df = process_query_response(response)
                if df is not None:
                    print("Resposta processada com sucesso")
                else:
                    print(f"Erro o processar a query de resposta: Colunas não encontradas")
                    continue
            except Exception as e:
                print(f"Erro ao processar a resposta em um temp.csv: {e}")
                time.sleep(5)
                continue        
            try:
                df_final = pd.concat([df_final, df.iloc[1:2]], ignore_index=True)
                print(f"Adicionado o artigo {pdf} ao dataframe final")
                break
            except Exception as e:
                print(f"Erro ao adicionar o artigo {pdf} ao dataframe final: {e}")
                time.sleep(5)

        df_final.to_csv('df_final.csv', sep=',', index=False)
