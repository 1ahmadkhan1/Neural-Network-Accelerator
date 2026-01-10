import numpy as np, chainer, chainer.functions as F, chainer.links as L
from chainer import training, serializers
from chainer.training import extensions

import chainer.dataset.download as dl

_orig_cached_download = dl.cached_download

def _cached_download_with_mirror(url, *args, **kwargs):
    old = "http://yann.lecun.com/exdb/mnist/"
    if url.startswith(old):
        url = "https://ossci-datasets.s3.amazonaws.com/mnist/" + url[len(old):]
    return _orig_cached_download(url, *args, **kwargs)

dl.cached_download = _cached_download_with_mirror

class DNN(chainer.Chain):
    def __init__(self):
        super(DNN, self).__init__()
        with self.init_scope():
            self.l1 = L.Linear(None, 1000)
            self.l2 = L.Linear(None, 1000) 
            self.l3 = L.Linear(None, 10)
    def forward(self, x):
        o1 = F.relu(self.l1(x))
        o2 = F.relu(self.l2(o1))
        o3 = self.l3(o2)
        return o3

nn = L.Classifier(DNN())

optimizer = chainer.optimizers.Adam()
optimizer.setup(nn)

train, test = chainer.datasets.get_mnist()

train_iter = chainer.iterators.SerialIterator(train, 100)
test_iter = chainer.iterators.SerialIterator(test, 100, repeat=False, shuffle=False)

updater = training.updaters.StandardUpdater(train_iter, optimizer)
trainer = training.Trainer(updater, (20, 'epoch'))

trainer.extend(extensions.Evaluator(test_iter, nn))
trainer.extend(extensions.LogReport())
trainer.extend(extensions.PrintReport(['epoch', 'main/loss', 'validation/main/loss', 'main/accuracy', 'validation/main/accuracy', 'elapsed_time']))
trainer.extend(extensions.ProgressBar())

trainer.run()
serializers.save_npz('trained_dnn.npz', nn)