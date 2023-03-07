import os
from utils import download_extraxt_zip
from requests_html import HTMLSession
import pandas as pd
from bs4 import BeautifulSoup


"""On commence par importer les données téléchargeables."""

olist_address="https://storage.googleapis.com/kaggle-data-sets/55151/2669146/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20230213%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20230213T112732Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=b7d0783cd597eb062f8a0655549e473ae758656eeeb844f3ceb0f3fc28405fe90802a7e000b045d10149b80e1c605869b75a3a0d581550306b509c16a146bb34e55ca83e14fb4ee1784d9bae89081bdaf01a792f466f0d5482b9036eb992ad4e61d3870853e6319f18425497df4763b78f2079db6bf4ac2359e95395cde9c224fb5f6d1d14374313a1e6d54027f3d81a318105b766b654cb0a1d51ff593bec5b3c3dc092b9ecccb7de19e313489d2dfad57ed811508750da77c3de85d5cd00e91a3752bd33c58b9977ee1d6ceddfee8d1b8224ac96f98a7e2ecd36c366b82e6fd4b9b98ac69c21e81e739821e3bf68b097800c03bf696e530995b476770320ec"
indicators_address="https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2017_2018/Perfil_das_despesas_no_Brasil_indicadores_de_qualidade_de_vida/xlsx/tabela_06.xlsx"
pop_address="https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Previa_da_Populacao/POP2022_Municipios.xls"
territorial_div_address="https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2021/DTB_2021.zip"
shapefiles_address="https://data.humdata.org/dataset/f5f0648e-f085-4c85-8242-26bf6c942f40/resource/2f26be26-a081-4557-8572-58545cd70e9f/download/bra_adm_ibge_2020_shp.zip"

if not os.path.isdir('./data'):
    os.mkdir('./data')

# Téléchargement des fichiers isolés
os.system('curl %s --output ./data/indicators_states.xlsx' % indicators_address) # Indicateurs socioéconomiques par État:
os.system('curl %s --output ./data/POP2022_Municipios.xls' % pop_address)  # Population par État

if not os.path.isdir('./shapefiles'):
    os.mkdir('./shapefiles')

# Téléchargement des zip
download_extraxt_zip(territorial_div_address, './data')  # Divisions territoriales
os.system("rm ./data/*.ods")
# Pour les shapefiles, on doit d'abord générer le lien vers AWS
# TODO: La requête vers le lien aws s3 génère Acces Denied...  
"""
shapefiles_address="https://data.humdata.org/dataset/f5f0648e-f085-4c85-8242-26bf6c942f40/resource/2f26be26-a081-4557-8572-58545cd70e9f/download/bra_adm_ibge_2020_shp.zip"
os.system("curl %s --output %s/aux" % (shapefiles_address, './shapefiles'))
page = open('./shapefiles/aux', 'r').read()
bs = BeautifulSoup(page, 'html.parser')
shapefiles_address = bs.find_all('a')[0]['href']
print(shapefiles_address)
os.system("rm ./shapefiles/aux")
download_extraxt_zip(shapefiles_address, './shapefiles')  # Shapefiles du Brézil
"""


"""On scrappe les codes isos. Le site générant les données avec js, on va devoir utiliser HTMLSession."""

# On charge la page...
address = "https://www.iso.org/obp/ui/#iso:code:3166:BR"
session = HTMLSession()
r = session.get(address)
r.html.render(timeout=10, sleep=10)
# ...Et on parse les éléments qui nous intéressent
table = r.html.find('#subdivision')[0]
columns = [th.text for th in table.find(".header")]
table_content = table.find('tbody')[0]
list_2d = [[td.text for td in line.find('td')] for line in table_content.find('tr')]
df = pd.DataFrame(list_2d, columns=columns)
df.to_csv('./data/states_iso.csv')


"""On va ensuite scrapper les données des zip codes"""
# TODO: Cette partie n'est pas fonctionnelle, à terminer
"""
address = "https://bra.postcodebase.com/fr"
class_states = "view view-region2-text view-id-region2_text view-display-id-block view-dom-id-fb5b0df2f7c500d4f11f1ffb23931ce2"
field_content_class = "field-content"
class_states = class_states.replace(' ', '.')

async def get_response(address):
    session = AsyncHTMLSession()
    r = await session.get(address)
    await r.html.arender()
    return r

response = asyncio.run(get_response(address))
table = response.html.find(".%s" % class_states, first=True)
content = table.find(".%s" %  field_content_class)
content = [c.find('a', first=True) for c in content]
"""