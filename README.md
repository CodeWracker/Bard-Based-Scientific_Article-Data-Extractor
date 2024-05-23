# Bard-Based Scientific Article Data Extractor

## Overview

This program is designed to extract and organize information from scientific articles stored in PDF format into a structured CSV file. It uses column headers and descriptions predefined in an Excel file (`colunas_e_descricao.xlsx`). The program leverages OpenAI's Gemini model for content generation and extraction.

## Prerequisites

1. **Python 3.9**: Ensure that Python 3.9 is installed on your system.
2. **Dependencies**: Use `pipenv` to manage Python packages. Install it with the command `pip install pipenv`.
3. **Cookies for Gemini**: Obtain cookies by visiting [Google Gemini](https://gemini.google.com/). Use the Chrome extension [ExportThisCookie](https://chromewebstore.google.com/detail/exportthiscookie/dannllckdimllhkiplchkcaoheibealk) to export the cookies to `bard_cookies.json`.

This will install all necessary Python packages in a virtual environment.

## Configuration

1. **Prepare Cookies**: Place the exported cookies in `bard_cookies.json` in the project directory.
2. **Configure Columns and Descriptions**: Modify `colunas_e_descricao.xlsx` to define the columns you want to extract from the articles. The first row of each column should describe what the information represents. Here is an example configuration (you can put any column and any description, but try to be clear because LLM models can be somewhat literal, as evidenced by the fact that I had to shout in capslock for it to understand what I wanted in one of the fields):

| Title         | First Author                                                    | Year of Publication | Source                                            | Battery Type                           | Efficiency                               | Datasets                                                      | Additional Notes                                                |
| ------------- | --------------------------------------------------------------- | ------------------- | ------------------------------------------------- | -------------------------------------- | ---------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------- |
| Article Title | ONLY THE NAME OF THE FIRST AUTHOR OF THE ARTICLE!!!!! NAME ONLY | Year of Publication | Source or journal where the article was published | Type of battery studied in the article | Energy efficiency of the proposed method | List of datasets separated by commas cited during the article | Any other relevant information or observation about the article |

3. **Prepare PDFs**: Place the PDFs to be analyzed in the `PDFs` folder.

## Usage

The program processes each PDF file in the `PDFs` directory, extracts the relevant information using the Gemini model, and outputs the results in a CSV format with the specified columns.

### With docker

You need to install the docker engine previously for this, if you don't want to, follow the manually steps.

- build the image with: `docker compose build`
- run the program with: `docker compose up`. This will automatically trigger the main.py file and start the application, so be sure to have all the files configurated befor running this command.

### Mannualy

To run the program, use the following command within the project directory:

- install pipenv with: `pip install -U pipenv`
- run the following: `pipenv shell` and then `pipenv install`
- execute the program with: `python main.py`

## Important Notes

- The program processes text only; if graphical analysis is crucial and the article does not discuss the graph in the text, this solution may not be ideal.
- Ensure that your cookie file and column configuration are correctly set up to avoid authentication or analysis issues.
- The Gemini response should strictly follow the CSV format with a semicolon (`;`) as the delimiter.

## Output

The extracted data from all PDFs will be saved in `df_final.csv` in the project directory. The CSV will follow the column structure specified in `colunas_e_descricao.xlsx`.
