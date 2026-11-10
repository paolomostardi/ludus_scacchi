# Architecture comparison: source_resnet 4x64 and 6x64

The candidate configuration is
`Backend/training_pipeline/configs/source_resnet_6x64.json`. It changes only the
residual block count from four to six. Dataset, row budget, epochs, batch size,
seed, optimizer and head stay the same. The default 4x64 config is unchanged.
The existing fit notebook reads the config; evaluation reconstructs from the
exported model config. Neither needs a separate copy for this variant.

Architecture source remains
`Backend/model_architecture/implementation/experimental/source_resnet.py`, with
factory `source_resnet` and variant `source_resnet_6x64`. Input is `(15,8,8)`,
transposed to channels-last, followed by a 3x3/64 stem, six two-convolution
residual blocks on the 8x8 grid, a 1x1/1 head, flattening and 64-way softmax.
The model name is `Ludus-Source-ResNet-6x64`. This tests extra capacity, not a
claim that the deeper network is already better. Residual connections make
depth experiments practical; see the [original ResNet paper](https://www.microsoft.com/en-us/research/publication/deep-residual-learning-for-image-recognition/).

Keras reports 306,497 total parameters for 4x64 and 455,233 for 6x64 (about 49%
more). Local verification covers staged configuration, input/output shapes and
a finite training step followed by save/reconstruction with matching predictions
on the Keras Torch CPU backend. This does not replace validation in Kaggle's
TensorFlow runtime or a comparison on independent evaluation data.

## Run the comparison

Use the same datasets, seed and training budget to isolate the effect of depth.
Before a new submission, finish or recover evaluation from any prior batch that
uses the same Kaggle kernel IDs. A new fit replaces the latest kernel output.

From a configured project checkout, preview and then run:

```bash
python -m Backend.training_pipeline.run_batch --config Backend/training_pipeline/configs/source_resnet_6x64.json --pipeline-mode training --plan-only
python -m Backend.training_pipeline.run_batch --config Backend/training_pipeline/configs/source_resnet_6x64.json --pipeline-mode training
```

To recover a completed fit's evaluation, use the saved batch directory:

```bash
python -m Backend.training_pipeline.run_batch --resume-dir /path/to/saved-batch
```

Keep host addresses, environment activation commands, service configuration,
background execution commands and operational batch histories in private operator
notes. Use a process supervisor appropriate to the deployment for unattended runs.

Compare general and simple-set accuracy/loss, available top-3 accuracy, sample
counts and training time. Record missing older metrics as unavailable. Confirm
that evaluation samples are independent of training before interpreting scores
as generalization evidence.

Prepare the [endgame dataset](endgame_dataset.md) independently so the effect of
a data change can be distinguished from the effect of changing model depth.
