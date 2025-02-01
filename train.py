import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import keras
import keras.api.layers as layers
import matplotlib.pyplot as plt

train_ds = keras.utils.image_dataset_from_directory(
    'dataset',
    validation_split=0.2,
    subset='training',
    seed=42,
    image_size=(100, 100),
    batch_size=32
)

val_ds = keras.utils.image_dataset_from_directory(
    'dataset',
    validation_split=0.2,
    subset='validation',
    seed=42,
    image_size=(100, 100),
    batch_size=32
)

class_names: list[str] = train_ds.class_names
num_classes = len(class_names)

data_augmentation = keras.Sequential(
  [
    layers.Input(shape=(100, 100, 3)),
    layers.RandomZoom(0.1),
    layers.RandomBrightness(0.1)
  ]
)

model = keras.models.Sequential([
    data_augmentation,
    layers.Rescaling(1./255),
    
    layers.Conv2D(32, 3, activation='relu'),
    layers.MaxPooling2D(),
    
    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Dropout(0.1),
    
    layers.Conv2D(128, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Dropout(0.1),
    
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dense(num_classes)
])


model.compile(optimizer='adam',
              loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

model.summary()

epochs=10

history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)

model.save('models/1.keras')

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()
