import os
import time
import asyncio
import pandas as pd
import PyPDF2
from gemini import Gemini

import csv
from pathlib import Path
import json


cookies = json.loads(open(
            str(Path(str(Path.cwd()) + "/bard_cookies.json")), encoding="utf-8").read())

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TABLE_MODEL_CSV = "Title,Authors,Year,Source,Battery Type,Control Method,Control Location,SoC Estimation Technique,Control Parameters,Energy Efficiency,Differences (Li vs. Pb-Acid),Battery Capacity,System Power,Energy Source,Implementation Challenges,PWM Circuit Notes,DC-DC Converter Used,Additional Notes"
columns = []
for col in TABLE_MODEL_CSV.split(','):
    columns.append(col.strip())
print(columns)

cols_example = ""
for col in columns:
    if col != columns[-1]:
        cols_example += f"{col}, "
    else:
        cols_example += "Exemplo de preenchimento com ponto e virgula; blablabla,"

# if last char is , remove it
if cols_example[-1] == ',':
    cols_example = cols_example[:-1]

TABLE_MODEL_DESCRIPTION = """
**Descrição das Colunas:**

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

        query_text = f"""
Extraia e organize as informações do artigo científico seguindo o formato de um CSV na saída de texto.* Utilize vírgula (,) como delimitador entre células. Em casos onde o conteúdo interno de uma célula naturalmente incluiria vírgulas, substitua-as por ponto e vírgula (;) para evitar problemas de formatação. Insira os dados conforme as colunas especificadas abaixo, assegurando que a resposta seja limitada à representação textual do CSV, sem adicionar texto explicativo ou fora do formato da tabela.

Colunas requeridas:

"Titulo,Universidade do 1º Autor,País da Universidade do 1º Autor,Ano,Hardware Utilizado para Treinamento,Hardware Utilizado para Utilização,Versões da YOLO citadas,Versão da YOLO utilizada,Versão Base da YOLO utilizada,Datasets,Desempenho do modelo utilizado,Motivo da seleção do modelo utilizado,Comentários e Observações"


*Instruções detalhadas:*

1. Identifique as informações necessárias para preencher cada coluna listada.
2. Use ponto e vírgula (;) para substituir quaisquer vírgulas no conteúdo das células, mantendo a clareza do formato CSV.
3. Preencha as células de forma concisa, focando exclusivamente nas informações solicitadas.
4. Utilize a última coluna para quaisquer notas adicionais relevantes à extração de dados.
5. O preenchimento de dados deve ser feito em Português do Brasil, independentemente da lingua do artgo cientifico
6. A saída de texto deve ser estritamente o conteúdo formatado em CSV, como ilustrado no exemplo abaixo, sem adicionar texto explicativo ou contextual fora dessa formatação.

*Exemplo de preenchimento correto generico sem muita relação com o caso especifico que estou enviando agora:*

```csv
{TABLE_MODEL_CSV}
{cols_example}
```

Nota: Siga estas instruções com atenção para assegurar a consistência e precisão das informações apresentadas no formato CSV textual.

Artigo:
{pdf_text}
```
        """

        print(f"Tentando a query com o texto com {len(pdf_text)} caracteres...")



        try:
            client = Gemini(cookies=cookies) # You can use various args
            response = client.generate_content(query_text)
            # response_json = json.loads(response.payload)
            
        except Exception as e:
            print(f"Erro ao criar a query: {e}")
            print("Diminuindo o texto em 10.000 caracteres")
            pdf_text = cut_text(pdf_text, 10000)
            time.sleep(5)
            continue


        try:
            response = response.candidates[0].text
            
            print(response)
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

    response = response[response.find(columns[0]):]

    # se os 2 primeiros caracteres forem || substitui por |
    if response[:2] == '||':
        # remove o primeiro |
        response = response[1:]

    

    response_head = response.split('\n')[0].strip()
    if response_head[0] == '|':
        response_head = response_head[1:]
    if response_head[-1] == '|':
        response_head = response_head[:-1]
    response_head = response_head.split('|')
    
    response_body =response.split('\n')[2].strip()
    # verifica se começa com | e remove
    if response_body[0] == '|':
        response_body = response_body[1:]
    # verifica se termina com | e remove
    if response_body[-1] == '|':
        response_body = response_body[:-1]
    response_body = response_body.split('|')
    for i in range(len(response_body)):
        response_body[i] = response_body[i].replace(',', ';') # substitui virgulas por ponto e virgula

    print(f"Head: {response_head}")
    print(f"Body: {response_body}")


    # Verifica se o cabeçalho e o corpo da resposta tem o mesmo tamanho
    if len(response_head) != len(response_body):
        print("Erro: Cabeçalho e corpo da resposta tem tamanhos diferentes")
        return None
    if len(response_head) != len(columns):
        print("Erro: Cabeçalho e corpo da resposta tem tamanhos diferentes do modelo")
        return None
    

    with open('temp.csv', 'w', encoding='utf-8') as f:
        # escreve o cabeçalho cm as colunas
        f.write(','.join(columns) + '\n')
        # escreve o corpo com os valores
        f.write(','.join(response_body) + '\n')
    
    # Ler o CSV e retorna o dataframe
    df = pd.read_csv('temp.csv', sep=',', encoding='utf-8', index_col=False)
    
    return df

def main():
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



if __name__ == "__main__":
    main()