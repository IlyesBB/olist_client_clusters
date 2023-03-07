# Ce fichier contient des fonctions génériques utiles


import os


def download_extraxt_zip(address, directory):
    """Permet de télécharger un zip et l'extraire dans un dossier"""
    os.system("curl %s --output %s/aux.zip" % (address, directory))
    os.system("unzip -o %s/aux.zip -d %s" % ((directory,)*2))
    os.system("rm %s/aux.zip" % (directory,)*2)
