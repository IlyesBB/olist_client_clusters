#!/bin/bash

olist_address="https://storage.googleapis.com/kaggle-data-sets/55151/2669146/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20230213%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20230213T112732Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=b7d0783cd597eb062f8a0655549e473ae758656eeeb844f3ceb0f3fc28405fe90802a7e000b045d10149b80e1c605869b75a3a0d581550306b509c16a146bb34e55ca83e14fb4ee1784d9bae89081bdaf01a792f466f0d5482b9036eb992ad4e61d3870853e6319f18425497df4763b78f2079db6bf4ac2359e95395cde9c224fb5f6d1d14374313a1e6d54027f3d81a318105b766b654cb0a1d51ff593bec5b3c3dc092b9ecccb7de19e313489d2dfad57ed811508750da77c3de85d5cd00e91a3752bd33c58b9977ee1d6ceddfee8d1b8224ac96f98a7e2ecd36c366b82e6fd4b9b98ac69c21e81e739821e3bf68b097800c03bf696e530995b476770320ec"
indicators_address="https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2017_2018/Perfil_das_despesas_no_Brasil_indicadores_de_qualidade_de_vida/xlsx/tabela_06.xlsx"
pop_address="https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Previa_da_Populacao/POP2022_Municipios.xls"
territorial_div_address="https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2021/DTB_2021.zip"
shapefiles_address="https://s3.us-east-1.amazonaws.com/hdx-production-filestore/resources/2f26be26-a081-4557-8572-58545cd70e9f/bra_adm_ibge_2020_shp.zip?AWSAccessKeyId=AKIAXYC32WNAQNXGU66R&Signature=TmnMODHlw3cstGtQ0UpUCED7xrY%3D&Expires=1676502777"

if [ ! -d "./data" ]; then
    mkdir "./data"
fi

# Téléchargement des données Olist
curl $olist_address --output "./data/data.zip"
unzip "./data/data.zip" -d "./data"
rm "./data/data.zip"

# Téléchargement des indicateurs socioéconomiques par État
curl $indicators_address --output "./data/socioeconomic_indicators_states.xlsx"

# Téléchargement de la population par État
curl $pop_address --output "./data/POP2022_Municipios.xls"

# Téléchargement des divisions territoriales
curl $territorial_div_address --output "./data/data.zip"
unzip "./data/data.zip" -d "./data"
rm ./data/data.zip ./data/*.ods

# Téléchargement des divisions territoriales
curl $shapefiles_address --output "./shapefiles/data.zip"
unzip "./shapefiles/data.zip" -d "./shapefiles"
rm ./data/data.zip