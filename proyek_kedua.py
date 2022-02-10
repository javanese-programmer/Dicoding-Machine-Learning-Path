# -*- coding: utf-8 -*-
"""Proyek_Kedua.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RyC4v-wACiosHNHMWxiqQXN7F9Ss-jvO

# Time Series Analysis using RNN

## Dev's Profile

Nama : Tariq Fitria Aziz <br>
Bergabung: 02 September 2020 <br>
Asal: Kabupaten Wonogiri, Jawa Tengah

## Problem Desc

Di sini, akan dibuat sebuah model Deep Learning yang dapat digunakan untuk melakukan forecast pada sebuah time series, yaitu data stock exchange.

Dataset yang digunakan dapat dilihat di sumber berikut: https://www.kaggle.com/mattiuzc/stock-exchange-data?select=indexProcessed.csv

## Part I: Preparation

### Import Library
"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import Huber

from sklearn.model_selection import train_test_split

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# %matplotlib inline

"""### Set Drive Folder"""

drive.mount('/content/drive/')

"""## Part II: Data Preparation

### Data Loading
"""

data = pd.read_csv('/content/drive/MyDrive/Datasets/indexProcessed.csv')
data.head(5)

"""### Data Information"""

data.info()

"""KETERANGAN <br>

Index: Ticker symbol for indexes <br>
Date: Date of observation <br>
Open: Opening Price <br>
High: Highest price during trading day <br>
Low: Lowest price during trading day <br>
Close: Closing price <br>
Adj Close: Closing price adjusted for dividends and stock splits <br>
Volume: Number of shares traded during trading day <br>
CloseUSD: Close price in terms of USD
"""

data.isna().sum()

"""### Data Preprocessing

Choose One Index
"""

data2 = data.loc[data['Index'] == 'NYA']

data2.head(10)

"""Change Datatype"""

data2['Date'] = pd.to_datetime(data2['Date'])

data2.info()

"""## Part III: Data Visualization"""

series1 = data2['Open'].values
date = data2['Date'].values

fig1, ax1 = plt.subplots(figsize = (15,5))

ax1.plot(date, series1, label = 'Open')
ax1.legend()
ax1.set_title('Opening Stock Price by Years')
ax1.set_xlabel('Years');
ax1.set_ylabel('Price');

"""## Part IV: Data Split and Windowing"""

train_series, test_series = train_test_split(series1, shuffle=False, test_size = 0.2)

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

train_set = windowed_dataset(train_series, window_size = 5, batch_size = 50, shuffle_buffer = 1000)
validation_set = windowed_dataset(test_series, window_size = 5, batch_size = 50, shuffle_buffer = 1000)

"""## Part V: Model Creation

### Function Definition
"""

def initialize_model(name, loss, optimizer, metrics):
  model = Sequential(name = name)

  model.add(LSTM(
      units = 512,
      return_sequences = True
      )
  )
  model.add(LSTM(
      units = 256,
      dropout = 0.5,
      return_sequences = True
      )
  )
  model.add(LSTM(
      units = 128,
      dropout = 0.5,
      )
  )
  model.add(Dense(
      units = 2048,
      activation = 'relu',
      kernel_initializer = 'he_uniform'
      )
  )
  model.add(Dropout(
      rate = 0.5
      )
  )
  model.add(Dense(
      units = 1024,
      activation = 'relu',
      kernel_initializer = 'he_uniform'
      )
  )
  model.add(Dropout(
      rate = 0.5
      )
  )
  model.add(Dense(
      units = 512,
      activation = 'relu',
      kernel_initializer = 'he_uniform'
      )
  )
  model.add(Dropout(
      rate = 0.5
      )
  )
  model.add(Dense(
      units = 256,
      activation = 'relu',
      kernel_initializer = 'he_uniform'
      )
  )
  model.add(Dropout(
      rate = 0.5
      )
  )
  model.add(Dense(
      units = 1,
      activation = 'linear',
      )
  )

  model.compile(loss = loss, optimizer = optimizer, metrics = [metrics])

  return model

"""### Model Initialization"""

optimizers = Adam(learning_rate=0.00001)
loss = Huber(delta=1.0)
metrics = 'mae'

Predictor1 = initialize_model('Predictor1', loss, optimizers, metrics)

"""## Part V: Train Model

### Define Callbacks
"""

es1 = EarlyStopping(monitor='mae', mode='min', verbose=1, patience=10)
mc1 = ModelCheckpoint('best_model1.h5', monitor='val_mae', mode='min', verbose=1, save_best_only=True)

"""### Train Process"""

history1 = Predictor1.fit(train_set, validation_data = validation_set, epochs = 100,  callbacks = [es1, mc1], verbose=1)

"""### Training Results"""

plt.plot(history1.history['mae'], label='mae')
plt.plot(history1.history['val_mae'], label='val_mae')

plt.title("Plot Loss and MAE")
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.show()