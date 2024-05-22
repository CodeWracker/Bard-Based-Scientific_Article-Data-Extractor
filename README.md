# Bard-Based-Scientific_Article-Data-Extractor

## Visão Geral

Este programa é projetado para extrair e organizar informações de artigos científicos armazenados em formato PDF em um arquivo CSV estruturado. Ele usa cabeçalhos de colunas e descrições pré-definidas em um arquivo Excel (`colunas_e_descricao.xlsx`). O programa utiliza o modelo Gemini da OpenAI para geração e extração de conteúdo.

## Pré-requisitos

1. **Python 3.9**: Certifique-se de que o Python 3.9 está instalado em seu sistema.
2. **Dependências**: Use `pipenv` para gerenciar os pacotes Python. Instale-o através do comando `pip install pipenv`.
3. **Cookies para Gemini**: Obtenha cookies visitando [Google Gemini](https://gemini.google.com/). Use a extensão do Chrome [ExportThisCookie](https://chromewebstore.google.com/detail/exportthiscookie/dannllckdimllhkiplchkcaoheibealk) para exportar os cookies para `bard_cookies.json`.

## Instalação

1. Clone o repositório ou baixe o código-fonte.
2. Dentro do diretório do projeto, execute: `pipenv install`

Isso instalará todos os pacotes Python necessários em um ambiente virtual.

## Configuração

1. **Prepare os Cookies**: Coloque os cookies exportados em `bard_cookies.json` no diretório do projeto.
2. **Configure Colunas e Descrições**: Modifique `colunas_e_descrição.xlsx` para definir as colunas que deseja extrair dos artigos. A primeira linha de cada coluna deve descrever o que a informação representa. Aqui está um exemplo de configuração (voce pode colocar qualquer coluna e qualquer descrição, mas tente ser claro pois os modelos de LLM são meio burros, vide o fato de que eu tive que gritar em capslock para ele entender o que eu queria em um dos campos):

| Título| Primeiro Autor| Ano de Publicação | Fonte| Tipo de Bateria| Eficiência| Datasets| Notas Adicionais|
| ---------------- | ------------- | ----------------- | ------------------- | --------- | --------------- | ---------------- | --------------- |
| Título do Artigo | SOMENTE O NOME DO PRIMEIRO AUTOR DO ARTIGO!!!!! NOME SÓ APENAS | Ano de Publicação | Fonte ou revista onde o artigo foi publicado | Tipo de bateria estudada no artigo | Eficiência energética do método proposto | Lista dos datasets separados por vírgula citados durante o artigo | Qualquer outra observação ou informação relevante sobre o artigo |

3. **Prepare os PDFs**: Coloque os PDFs a serem analisados na pasta `PDFs`.

## Uso

Para executar o programa, use o seguinte comando dentro do diretório do projeto:

```
python main.py
```

O programa processa cada arquivo PDF no diretório `PDFs`, extrai as informações relevantes usando o modelo Gemini e produz os resultados em formato CSV com as colunas especificadas.

## Notas Importantes

- O programa processa apenas texto; se a análise gráfica for crucial e o artigo não discutir o gráfico no texto, essa solução pode não ser ideal.
- Certifique-se de que seu arquivo de cookies e a configuração das colunas estejam corretamente configurados para evitar problemas de autenticação ou de análise.
- A resposta do Gemini deve seguir estritamente o formato CSV com ponto e vírgula (`;`) como delimitador.

## Saída

Os dados finais extraídos de todos os PDFs serão salvos em `df_final.csv` no diretório do projeto. O CSV seguirá a estrutura de colunas especificada em `colunas_e_descrição.xlsx`.
