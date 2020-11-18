# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 07:48:44 2020

@author: Usuario
"""
#%%Libraries
import scipy.io
import numpy as np
import pandas as pd
import os
import tarfile
import matplotlib.pyplot as plt
import skimage.transform
import shutil
import re
import random
from math import isnan
#%% PART 1
#read data in matlab format
mat = scipy.io.loadmat('imdb.mat')
mat.items()
mat.keys()
mat['__header__']
mat['__version__']
mat['__globals__']
mat['imdb'][0][0]

#take the data I need: date of birth, year when the photo was taken, photo path, gender
#and face scores just for clean a bit the data
#and build an array 
datos = mat['imdb'][0][0]
datosFin = np.empty(shape=(0,datos[0].shape[1]))
for i in [0,1,2,3,6,7]:
    print(i)
    datosFin = np.vstack((datosFin, datos[i]))
 
datosFin = np.transpose(datosFin)

datosFin = pd.DataFrame(datosFin,columns=['dob','photoTaken','photoPath','gender','score1','score2'])

for i in ['dob','photoTaken','gender']:
    datosFin[i] = pd.to_numeric(datosFin[i], errors='coerce')
for i in ['score1','score2']:
    datosFin[i] = datosFin[i].astype("str")
#celaning data
datosFin = datosFin[datosFin['score1'] != '-inf']
datosFin = datosFin[datosFin['score2'] == 'nan']
datosFin = datosFin.drop(['score1', 'score2'], axis=1)

#I write a csv to read in R
datosFin.to_csv("RdataBase.csv",index=False)

#%% PART 2

#read the csv builded in R
datosFin = pd.read_csv('Rresult.csv')
#leaving only the variables needed
datosFin = datosFin.drop(['dob', 'photoTaken','dob_date','gender','photo_date'], axis=1)
#random 1000 subsset
random.seed(123)
ind = list(range(datosFin.shape[0]))
ind = random.sample(ind,3500)
datosFin = datosFin.iloc[ind,:]
datosFin = datosFin.reset_index()
datosFin = datosFin.drop('index',axis=1)

#image size
n_px_ancho =  30
n_px_alto = 30

#zip file with the face photos
tar_file = 'imdb_crop'
my_tar = tarfile.open(tar_file+'.tar')
#my_tar.getnames()

#empty objects where the image data will be stored
matDatos = np.empty(shape=(n_px_ancho*n_px_alto*3,1),dtype=object)

#foreach image
for i in range(datosFin.shape[0]):
    #getting the file name
    file = datosFin.iloc[i,0]
    #fixing it
    file = re.sub("[[]|[]]|[']","",file)
    #eextracting the file
    try:
        my_tar.extract(tar_file+'/'+file)
        #from jpg to array
        image = np.array(plt.imread(os.getcwd()+'/'+tar_file+'/'+file))
        my_image = skimage.transform.resize(image, output_shape=(n_px_ancho,n_px_alto)).reshape((1, n_px_ancho*n_px_alto*3)).T
        #erase the jpg
        shutil.rmtree(os.getcwd()+'/'+tar_file)
    except:
        my_image = np.empty((n_px_ancho*n_px_alto*3,1))
        my_image[:] = None
        print("image "+str(i)+" couldnt be found")
        
    #add to the other ones
    matDatos = np.concatenate((matDatos, my_image),axis=1)
    print(i)

#the first row was nothing
matDatos = matDatos[:,1:].transpose()
#to data frame
data = pd.DataFrame.from_records(matDatos)
#join with all the data
datosFin = pd.concat([datosFin,data],axis=1)
#drop unused variables
datosFin = datosFin.drop(["photoPath"],axis=1)
#drop if the image couldnt be found
ind = [not isnan(datosFin.iloc[i,1]) for i in range(datosFin.shape[0])]
datosFin = datosFin[ind]
#a function to verify the data is correctly saved
def vector2image(vector,n_px_ancho=30, n_px_alto=30):
    
    y = vector.reshape((n_px_ancho,n_px_alto,3))
    plt.subplot(121)
    plt.imshow(y)
    # h,w,c = y.shape
    # x = skimage.transform.resize(y, output_shape=(n_px_ancho,n_px_alto))
    # plt.subplot(122)
    # plt.imshow(y)
    plt.show()


posImagen = 100
vector = datosFin.iloc[posImagen,1:]
vector = vector.to_numpy(dtype=np.dtype('float64'))
vector2image(vector)
#I write a csv
datosFin.to_csv("BaseFin.csv",index=False)
