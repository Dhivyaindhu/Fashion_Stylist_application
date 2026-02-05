import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, Flatten
import numpy as np

def build_model():
    model = Sequential([
        Conv1D(32, 2, activation='relu', input_shape=(4,1)),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(4, activation='softmax')  # S, M, L, XL
    ])

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def predict_size(model, features):
    features = features.reshape(1, 4, 1)
    pred = model.predict(features)
    sizes = ["S", "M", "L", "XL"]
    return sizes[np.argmax(pred)]
