import requests # pip install requests
from bs4 import BeautifulSoup # pip install beautifulsoup4
import pandas as pd # pip install lxml
from expected_fields import WikipediaPopulationFields

response = requests.get("https://fr.wikipedia.org/wiki/Liste_des_pays_par_population")
soup = BeautifulSoup(response.content, 'html.parser')
#table = soup.select_one("table.sticky-header-multi.wikitable.sortable.alternance.jquery-tablesorter")
table = soup.find('table', class_='wikitable')

datatables = pd.read_html(str(table))
dataframe = datatables[0]

df_filtered = dataframe.iloc[:, [1, 3]]
df_filtered.columns = [WikipediaPopulationFields.COUNTRY.value, WikipediaPopulationFields.POPULATION.value] 
df_filtered[WikipediaPopulationFields.COUNTRY.value] = df_filtered[WikipediaPopulationFields.COUNTRY.value].str.replace(r'\[.*?\]', '', regex=True)
df_filtered[WikipediaPopulationFields.POPULATION.value] = df_filtered[WikipediaPopulationFields.POPULATION.value].astype(str).str.replace(r'\D', '', regex=True).astype(int)
df_filtered.to_csv('wikipedia_populations.csv', index=False, encoding='utf-8')
