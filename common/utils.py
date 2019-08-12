import numpy as np
import os
import nibabel as nib
from scipy.ndimage import zoom
from keras.layers.convolutional import ZeroPadding3D, Cropping3D
from keras.backend import int_shape

def norm_to_uint8(data):
  max_value = data.max()
  if not max_value == 0:
    data = data / max_value

  data = 255 * data
  img = data.astype(np.uint8)
  return img

def convert_to_binary_3d(data, labels):
  binary_data = np.array(
    [[[0.0 if pixel in labels else 255.0 for pixel in row] for row in matrix] for matrix in data]
  ).astype(np.float32)

  return binary_data

def resize_3d(data, width, height, depth):
  in_width, in_height, in_depth = data.shape
  width_ratio = width / in_width
  height_ratio = height /in_height
  depth_ratio = depth / in_depth

  resized_data = zoom(data, (width_ratio, height_ratio, depth_ratio), order=0)

  return resized_data

def load_image_data(filename, path='.'):
  full_path = os.path.join(path, filename)
  img = nib.load(full_path)
  img_data = img.get_fdata(dtype=np.float32)

  return img_data

def calc_fit_pad(width, height, depth, n_layers):
  divider = 2 ** n_layers
  w_pad, h_pad, d_pad = 0, 0, 0

  w_rest = width % divider
  h_rest = height % divider
  d_rest = depth % divider

  if w_rest:
    w_pad = (divider - w_rest) // 2
  if h_rest:
    h_pad = (divider - h_rest) // 2
  if d_rest:
    d_pad = (divider - d_rest) // 2

  return w_pad, h_pad, d_pad

def pad_to_fit(inputs, n_layers=4):
  width = int_shape(inputs)[1]
  height = int_shape(inputs)[2]
  depth = int_shape(inputs)[3]

  w_pad, h_pad, d_pad = calc_fit_pad(width, height, depth, n_layers)

  x = ZeroPadding3D((w_pad, h_pad, d_pad))(inputs)
  return x

def crop_to_fit(inputs, outputs, n_layers=4):
  width = int_shape(inputs)[1]
  height = int_shape(inputs)[2]
  depth = int_shape(inputs)[3]

  w_pad, h_pad, d_pad = calc_fit_pad(width, height, depth, n_layers)

  x = Cropping3D((w_pad, h_pad, d_pad))(outputs)
  return x

