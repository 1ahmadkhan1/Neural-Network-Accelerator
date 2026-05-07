####
# This script is used to run inference on the trained DNN using the actual weights and biases and converted weights and biases.
# Then compare accuracy of the two and check if there is any significant difference.
# Point is to verify that the conversion to Q2.14 does not cause a significant drop in accuracy.
####

import numpy as np
import chainer
import chainer.dataset.download as dl

####
# MNIST mirror fix
####
_orig_cached_download = dl.cached_download

def _cached_download_with_mirror(url, *args, **kwargs):
    old = "http://yann.lecun.com/exdb/mnist/"
    if url.startswith(old):
        url = "https://ossci-datasets.s3.amazonaws.com/mnist/" + url[len(old):]
    return _orig_cached_download(url, *args, **kwargs)

dl.cached_download = _cached_download_with_mirror


####
# Q2.14 conversion
####
SCALE = 2 ** 14
Q_MIN = -32768
Q_MAX = 32767

def quantize_q2_14(x):
    """
    Convert float array to signed Q2.14 integer array.
    """
    q = np.sign(x) * np.floor(np.abs(x) * SCALE + 0.5)
    q = np.clip(q, Q_MIN, Q_MAX)
    return q.astype(np.int16)

def dequantize_q2_14(q):
    """
    Convert signed Q2.14 integer array back to float.
    """
    return q.astype(np.float32) / SCALE


####
# DNN forward pass using NumPy
# Chainer Linear stores W as shape: (out_features, in_features)
# Therefore forward is: x @ W.T + b
####
def relu(x):
    return np.maximum(x, 0)

def forward_numpy(x, W1, b1, W2, b2, W3, b3):
    h1 = relu(x @ W1.T + b1)
    h2 = relu(h1 @ W2.T + b2)
    logits = h2 @ W3.T + b3
    return logits


####
# Accuracy function
####
def compute_accuracy(x, y, W1, b1, W2, b2, W3, b3, batch_size=100):
    correct = 0
    total = 0

    for i in range(0, len(x), batch_size):
        xb = x[i:i + batch_size]
        yb = y[i:i + batch_size]

        logits = forward_numpy(xb, W1, b1, W2, b2, W3, b3)
        preds = np.argmax(logits, axis=1)

        correct += np.sum(preds == yb)
        total += len(yb)

    return correct / total


####
# Load trained weights and biases
# Expected keys:
# predictor/l1/W, predictor/l1/b, predictor/l2/W, predictor/l2/b, predictor/l3/W, predictor/l3/b
####
data = np.load("training/trained_dnn.npz")

W1 = data["predictor/l1/W"].astype(np.float32)
b1 = data["predictor/l1/b"].astype(np.float32)
W2 = data["predictor/l2/W"].astype(np.float32)
b2 = data["predictor/l2/b"].astype(np.float32)
W3 = data["predictor/l3/W"].astype(np.float32)
b3 = data["predictor/l3/b"].astype(np.float32)

print("Loaded weights:")
print("W1:", W1.shape, "b1:", b1.shape)
print("W2:", W2.shape, "b2:", b2.shape)
print("W3:", W3.shape, "b3:", b3.shape)


####
# Quantize then dequantize weights/biases
# This simulates the values after conversion to Q2.14
####
W1_q = dequantize_q2_14(quantize_q2_14(W1))
b1_q = dequantize_q2_14(quantize_q2_14(b1))

W2_q = dequantize_q2_14(quantize_q2_14(W2))
b2_q = dequantize_q2_14(quantize_q2_14(b2))

W3_q = dequantize_q2_14(quantize_q2_14(W3))
b3_q = dequantize_q2_14(quantize_q2_14(b3))


####
# Load MNIST test data
####
_, test = chainer.datasets.get_mnist()

x_test = np.array([example[0] for example in test], dtype=np.float32)
y_test = np.array([example[1] for example in test], dtype=np.int64)

print("Test data:", x_test.shape, y_test.shape)


####
# Compute accuracies
####
float_acc = compute_accuracy(
    x_test, y_test,
    W1, b1, W2, b2, W3, b3
)

q214_acc = compute_accuracy(
    x_test, y_test,
    W1_q, b1_q, W2_q, b2_q, W3_q, b3_q
)

print()
print("======================================")
print("Accuracy Comparison")
print("======================================")
print(f"Float weights accuracy:       {float_acc * 100:.2f}%")
print(f"Q2.14 converted accuracy:     {q214_acc * 100:.2f}%")
print(f"Accuracy difference:          {(float_acc - q214_acc) * 100:.4f}%")
print("======================================")


####
# Quantization error stats
####
def print_error_stats(name, original, quantized):
    error = quantized - original
    print(f"{name}:")
    print(f"  max abs error:  {np.max(np.abs(error)):.8f}")
    print(f"  mean abs error: {np.mean(np.abs(error)):.8f}")
    print(f"  saturated high: {np.sum(original * SCALE > Q_MAX)}")
    print(f"  saturated low:  {np.sum(original * SCALE < Q_MIN)}")

print()
print("======================================")
print("Q2.14 Quantization Error Stats")
print("======================================")
print_error_stats("W1", W1, W1_q)
print_error_stats("b1", b1, b1_q)
print_error_stats("W2", W2, W2_q)
print_error_stats("b2", b2, b2_q)
print_error_stats("W3", W3, W3_q)
print_error_stats("b3", b3, b3_q)
print("======================================")