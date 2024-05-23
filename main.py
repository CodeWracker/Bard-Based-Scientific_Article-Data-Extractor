import os
import time
import asyncio
import pandas as pd
import PyPDF2
from gemini import Gemini

import csv
from pathlib import Path
import json
import random



# read colunas_e_descricao.xslx e pega as colunas e descrição (é um arquivo excel que tem as colunas normais e no conteudo delas tem a descrição na primeira linha)
df_example = pd.read_excel('colunas_e_descricao.xlsx')

# pega as colunas
columns = df_example.columns.tolist()
descriptions = df_example.iloc[0].tolist()
print(columns)
print(descriptions)

try:
    # pra windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except:
    pass


TABLE_MODEL_CSV = ';'.join(columns)

cols_example = ""
for col in columns:
    if col != columns[-1]:
        cols_example += f'Exemplo de preenchimento normal; '
    else:
        cols_example += 'Exemplo de preenchimento com ponto e virgula, blablabla;'

# if last char is , remove it
if cols_example[-1] == ',':
    cols_example = cols_example[:-1]

TABLE_MODEL_DESCRIPTION = ""
for col, desc in zip(columns, descriptions):
    TABLE_MODEL_DESCRIPTION += f'{col}: {desc}\n'

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
Extraia e organize as informações do artigo científico seguindo o formato de um CSV na saída de texto.* Utilize ponto-e-vírgula (;) como delimitador entre células. Insira os dados conforme as colunas especificadas abaixo, assegurando que a resposta seja limitada à representação textual do CSV, sem adicionar texto explicativo ou fora do formato da tabela.

Colunas requeridas:

"{TABLE_MODEL_CSV}"


*Instruções detalhadas:*

1. Identifique as informações necessárias para preencher cada coluna listada.
2. Preencha as células de forma concisa, focando exclusivamente nas informações solicitadas.
3. Utilize a última coluna para quaisquer notas adicionais relevantes à extração de dados.
4. O preenchimento de dados deve ser feito em Português do Brasil, independentemente da lingua do artgo cientifico
5. A saída de texto deve ser estritamente o conteúdo formatado em CSV, como ilustrado no exemplo abaixo, sem adicionar texto explicativo ou contextual fora dessa formatação.
6. A separação entre células deve ser feita por ponto e vírgula (;) para evitar conflitos com vírgulas internas em células.

*Exemplo de preenchimento correto generico sem muita relação com o caso especifico que estou enviando agora:*

```csv
{TABLE_MODEL_CSV}
{cols_example}
```

A explicação de cada coluna é fornecida abaixo para referência:
{TABLE_MODEL_DESCRIPTION}

Nota: Siga estas instruções com atenção para assegurar a consistência e precisão das informações apresentadas no formato CSV textual.

Artigo:
{pdf_text}


----

LEMBRE-SE A SUA RESPOSTA DEVE SER SOMENTE UM CSV!!!!!!! NO FORMATO
```csv
{TABLE_MODEL_CSV}
{cols_example}
```
NÃO ESQUECE QUE A SUA RESPOSTA DEVE SER UM CSV SEPARADO POR PONTO E VÍRGULA (;).
        """

        print(f"Tentando a query com o texto com {len(pdf_text)} caracteres...")



        try:
            cookies = json.loads(open(
            str(Path(str(Path.cwd()) + "/bard_cookies.json")), encoding="utf-8").read())
            client = Gemini(cookies=cookies) # You can use various args
            response = client.generate_content(query_text)
            # response_json = json.loads(response.payload)
            
        except Exception as e:
            print(f"Erro ao criar a query: {e}")
            if("SNlM0e" not in str(e)):
                print("Diminuindo o texto em 10.000 caracteres")
                pdf_text = cut_text(pdf_text, 10000)
            else:
                print("Altere os Tokens de autenticação no arquivo bard_cookies.json")
                time.sleep(60)
            time.sleep(5)
            continue


        try:
            chosen_index = None
            # escolhe aleatoriamente entre 0 e o tamanho da lista de candidatos
            chosen_index = random.randint(0, len(response.candidates) - 1)
            response = response.candidates[chosen_index].text            
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

    response = response.split('\n')
    # remove linhas vazias
    response = [line for line in response if line.strip() != '']

    response_header = response[0].strip().replace('"', '').split(';')
    response_body = response[1].strip().replace('"', '').split(';')


    print(f"\n\n\nHeader: {response_header}")
    print(f"Body: {response_body}")


    if len(response_header) != len(columns):
        print(f"Erro ao processar a resposta: Número de colunas não corresponde ao esperado. Foram encontradas {len(response_header)} colunas, esperado {len(columns)}")
        return None

    if len(response_body) != len(columns):
        print(f"Erro ao processar a resposta: Número de colunas não corresponde ao esperado. Foram encontradas {len(response_body)} colunas, esperado {len(columns)}")
        return None
    
    # escreve um csv temporário sem a coluna de index
    with open('temp.csv', 'w', encoding='utf-8') as f:
        f.write(';'.join(response_header) + '\n')
        f.write(';'.join(response_body) + '\n')

    # lê o csv temporário
    try:
        df = pd.read_csv('temp.csv', sep=';', encoding='utf-8', engine='python', index_col=False)
        print("CSV temporário lido com sucesso")
        # remove o csv temporário
        os.remove('temp.csv')
        return df
    except Exception as e:
        print(f"Erro ao ler o csv temporário: {e}")
    


    return None

def main():
    pdfs = [pdf for pdf in os.listdir('./PDFs') if pdf.endswith('.pdf')]    

    # verifica se a pasta CSVs existe
    if not os.path.exists('./CSVs'):
        os.makedirs('./CSVs')

    try:
        df_final = pd.read_csv('df_final.csv', sep=';', encoding='utf-8', engine='python', index_col=False)
        print("Dataframe final lido com sucesso")
    except Exception as e:
        print(f"Erro ao ler o dataframe final: {e}")
        df_final = pd.DataFrame(columns=columns)
        df_final.to_csv('df_final.csv', sep=';', index=False)
        print("Dataframe final criado com sucesso")


    for pdf in pdfs:
        print(f"\n\nAnalisando o arquivo {pdf}...")
        # verifica se o arquivo é mesmo um pdf
        if not pdf.endswith('.pdf'):
            print(f"O arquivo {pdf} não é um pdf")
            continue

        # verifica se o arquivo ja foi processado
        pdf_name = pdf.split('.')[0]
        if os.path.exists(f'./CSVs/{pdf_name}.csv'):
            print(f"O arquivo {pdf} já foi processado")
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
                # concatena
                df_final = pd.concat([df_final, df], ignore_index=True)
                print(f"Adicionado o artigo {pdf} ao dataframe final")
                # cria um csv do arquivo para gerar um backup
                df.to_csv(f'./CSVs/{pdf_name}.csv', sep=';', index=False)
                df_final.to_csv('df_final.csv', sep=';', index=False)
                break
            except Exception as e:
                print(f"Erro ao adicionar o artigo {pdf} ao dataframe final: {e}")
                time.sleep(5)




if __name__ == "__main__":
    main()