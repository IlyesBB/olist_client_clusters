#!/usr/bin/env python
# coding: utf-8

# In[10]:


import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
from math import sqrt
from scipy.stats import norm
from sklearn.decomposition import PCA
import pandas as pd
from sklearn.model_selection import cross_validate
from unidecode import unidecode
from collections import Counter
from datetime import datetime

# # Fonctions générales

# In[2]:
most_common = lambda array: Counter(array).most_common(1)[0][0]

format_str = lambda x: unidecode(x.lower())

def drop_duplicates(data, subset, data_name):
    """Supprime les doublons dans une base de données, en affichant le nombre de doublons trouvés"""
    # On enregistre le nombre de lignes avant suppression des doublons
    len_data = len(data)  
    data.drop_duplicates(subset=subset, inplace=True)
    print("%d doublons ont été repérés dans %s" %
          (len_data-len(data), data_name))
    return data

def plot_shape(shp_file, id, ax, c='black', background_c=None, title=None):
    #plotting the graphical axes where map ploting will be done
    points = np.array(shp_file.shape(id).points)
    parts = list(shp_file.shape(id).parts) + [len(points)]
    for ind_part in range(len(parts)-1):
        #plotting using the derived coordinated stored in array created by numpy
        points_part = points[parts[ind_part]:parts[ind_part+1]]
        ax.plot(points_part[:, 0], points_part[:, 1], c=c, linewidth=2)
        if background_c is not None:
            ax.add_patch(Polygon(points_part, closed=True, color=background_c))
    ax.text(np.mean(points[:,0]), np.mean(points[:,1]), title, ha='center')

def gini(x):
    total = 0
    for i, xi in enumerate(x[:-1], 1):
        total += np.sum(np.abs(xi - x[i:]))
    return total / (len(x)**2 * np.mean(x))

def str_to_datetime(date_str):
    """Retourne l'objet datetime associé à une date sous forme de chaîne de caractères"""
    date, time = date_str.split(' ')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))


# # Pour les distributions

# In[3]:


def distribution_discrete_var(data, distribution_var, to_count):
    """Retourne une série ayant en index les valeurs d'une variable et en contenu le nombre d'individus associés."""
    return data[[distribution_var, to_count]].groupby(distribution_var).count()[to_count]

# get_mean_interval: Obtenir la moyennes des bornes d'un intervalle pandas


def get_mean_interval(pd_interval):
    return (pd_interval.left+pd_interval.right)/2


def distribution_continuous_var(data, distribution_var, to_count, bins, dtype=float):
    """Discrétise une variable continue puis retourne sa distribution."""
    data_copy = data.copy()
    data_copy[distribution_var] = pd.cut(data_copy[distribution_var], bins)
    data_copy[distribution_var] = data_copy[distribution_var].map(
        get_mean_interval)
    data_copy[distribution_var] = data_copy[distribution_var].astype(dtype)
    return distribution_discrete_var(data_copy, distribution_var, to_count)


def plot_distribution(distribution_series, kwargs=None):
    """Affiche une distribution. Chaque indice correspond à une valeur, et son contenu à l'effectif."""
    kwargs = {} if kwargs is None else kwargs
    plt.bar(distribution_series.index, distribution_series, **kwargs)
    plt.xlabel(distribution_series.index.name)
    plt.ylabel("Effectifs")


# # Pour les courbes de Lorenz

# In[5]:


def gini_index(quantity_per_individual):
    """Retourne l'indice de Gini à partir d'une série contenant les individus en indice et les quantités en valeurs."""
    # n_individuals: Nombre de d'individus
    n_individuals = len(quantity_per_individual)
    # quantity_cum_norm: Somme cumulée normalisée des quantités
    quantity_cum_norm = quantity_per_individual.cumsum()/quantity_per_individual.sum()
    # integral: Intégrale sous la courbe étudiée
    integral = (quantity_cum_norm.sum() -
                (1+quantity_cum_norm.iloc[0])/2)/n_individuals
    return 2*(0.5-integral)


def plot_lorenz_curve(quantity_per_individual, font_size=11):
    """Affiche la courbe de Lorenz pour une répartition d'une quantité"""
    n_individuals = len(quantity_per_individual)
    # quantity_cum_norm: Somme cumulée normalisée des quantités
    quantity_cum_norm = quantity_per_individual.cumsum()/quantity_per_individual.sum()
    plt.plot(quantity_cum_norm.index, quantity_cum_norm)  # Courbe étudiée
    plt.plot(quantity_cum_norm.index, np.linspace(
        0, 1, n_individuals), linestyle='--')  # Courbe modèle
    # gini: Indice de gini de la courbe
    gini = gini_index(quantity_per_individual)
    plt.legend(["Courbe mesurée, gini=%.2f" % gini,
               "Courbe de répartition uniforme, gini=0"], fontsize=font_size)
    plt.xlabel(quantity_per_individual.index.name, fontsize=font_size)
    plt.ylabel(quantity_per_individual.name, fontsize=font_size)
    return gini


# # Pour l'ACP

# In[6]:


def inertia_per_len_components(list_n_components, values_scaled):
    # intertia_for_nb_comps: Dictionnaire de l'inertie pour un nombre de composantes principales
    inertia_per_nb_comps = {}
    for n_components in list_n_components:
        pca = PCA(n_components=n_components)
        values_projected = pca.fit_transform(values_scaled)
        scree = pca.explained_variance_ratio_*100
        inertia_per_nb_comps[n_components] = sum(scree)
    return pd.DataFrame(data=inertia_per_nb_comps, index=pd.Index(['Pourcentage de l\'inertie totale']))


# In[7]:


def scree_plot(pca):
    # scree: Contient les pourcentages de l'inertie pour chaque composante
    scree = pca.explained_variance_ratio_*100
    # On numérote chaque composante et on affiche ce pourcentage dans un histogramme
    plt.bar(np.arange(len(scree))+1, scree)
    # On affiche aussi la somme cumulée des pourcentage d'inertie contenue dans chaque composante
    plt.plot(np.arange(len(scree))+1, scree.cumsum(), c="red", marker='o')
    plt.xlabel("rang de l'axe d'inertie")
    plt.ylabel("pourcentage d'inertie")
    plt.title("Eboulis des valeurs propres")
    plt.show(block=False)


# In[8]:


def plot_correlation_circle(ind_axis_1, ind_axis_2, pca, labels):
    # Les données sont centrées-réduites dont les vecteurs sont normés i.e sur [-1,1]
    # pcs: La composition linéaire de chacune des composante principale en fonction de chaque variable
    pcs = pca.components_
    # On crée la figure qui va contenir tous les cercles
    fig = plt.figure(figsize=(7, 6))
    plt.quiver(np.zeros(pcs.shape[1]), np.zeros(pcs.shape[1]),
               pcs[ind_axis_1, :], pcs[ind_axis_2, :],
               angles='xy', scale_units='xy', scale=1, color="grey")
    # On parcours les segments pour les annoter
    for i, (x, y) in enumerate(pcs[[ind_axis_1, ind_axis_2]].T):
        plt.text(x, y, labels[i], fontsize='14',
                 ha='center', va='center', color="blue", alpha=0.5)
    # nom des axes, avec le pourcentage d'inertie expliqué
    plt.xlabel('F{} ({}%)'.format(ind_axis_1+1, round(100 *
               pca.explained_variance_ratio_[ind_axis_1], 1)))
    plt.ylabel('F{} ({}%)'.format(ind_axis_2+1, round(100 *
               pca.explained_variance_ratio_[ind_axis_2], 1)))
    xmin, xmax, ymin, ymax = -1, 1, -1, 1
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    # On crée un cercle de centre (0,0) et de rayon 1, contenant tous les segments
    circle = plt.Circle((0, 0), 1, facecolor='none', edgecolor='b')
    # plt.gca: Permet d'obtenir l'objet Axes de la figure courante, pour ajouter le cercle
    plt.gca().add_artist(circle)
    # affichage des lignes horizontales et verticales
    plt.plot([-1, 1], [0, 0], color='grey', ls='--')
    plt.plot([0, 0], [-1, 1], color='grey', ls='--')
    plt.title("Cercle des corrélations (F{} et F{})".format(
        ind_axis_1+1, ind_axis_2+1))


# In[9]:


def plot_factorial_plane(ind_axis_1, ind_axis_2, values_projected, pca, labels=None, s=0.5):
    # initialisation de la figure
    fig = plt.figure(figsize=(7, 6))
    # affichage des points
    plt.scatter(values_projected[:, ind_axis_1],
                values_projected[:, ind_axis_2], alpha=1, s=s)

    if not (labels is None):
        for i, (x, y) in enumerate(values_projected[:, [ind_axis_1, ind_axis_2]]):
            plt.text(x, y, labels[i], fontsize='14', ha='center', va='center')

    xmin = np.min(values_projected[:, ind_axis_1])
    xmax = np.max(values_projected[:, ind_axis_1])
    dx = abs(xmax-xmin)/10
    plt.xlim([xmin-dx, xmax+dx])
    ymin = np.min(values_projected[:, ind_axis_2])
    ymax = np.max(values_projected[:, ind_axis_2])
    dy = abs(ymax-ymin)/10
    plt.ylim([ymin-dy, ymax+dy])

    # affichage des lignes horizontales et verticales
    plt.plot([-100, 100], [0, 0], color='grey', ls='--')
    plt.plot([0, 0], [-100, 100], color='grey', ls='--')

    # nom des axes, avec le pourcentage d'inertie expliqué
    plt.xlabel('F{} ({}%)'.format(ind_axis_1+1, round(100 *
               pca.explained_variance_ratio_[ind_axis_1], 1)))
    plt.ylabel('F{} ({}%)'.format(ind_axis_2+1, round(100 *
               pca.explained_variance_ratio_[ind_axis_2], 1)))

    plt.title("Projection des individus (sur F{} et F{})".format(
        ind_axis_1+1, ind_axis_2+1))
