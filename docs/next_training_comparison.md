# Next comparison: source_resnet 6x64

The Nov 5 batch `20261105T082917Z-d51bd7cc` downloaded fit checkpoints for chunks
0–4 and its final model. Its pasted summary still marks evaluation running, no
evaluation files were listed, and no runner process was found. Recover that
evaluation before submitting new work to the shared Kaggle slugs. File sizes
and successful fitting do not establish model quality or independent test accuracy.

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

## VPS sequence

Commit and push the required local changes before pulling; the runner pins
Kaggle imports to the VPS checkout's commit. Recover the old batch first:

```bash
source /opt/ludus-runner-venv/bin/activate
cd /opt/ludus_scacchi
git pull --ff-only origin main
kaggle kernels status paolomostardi/evaluate-model
python -m Backend.training_pipeline.run_batch --resume-dir /root/ludus-artifacts/training-batches/20261105T082917Z-d51bd7cc
```

If resume reports a failed evaluation, inspect the error before retrying. An old
saved `running` state is first changed to `failed`; a second resume can retry
evaluation without retraining. Do not overwrite the fit slug before recovery.
Accept recovery only with a complete summary and report referring to fit run
`212a6ef6444948fe9561cb3cfda52d7b`.

Preview and launch the comparison after successful recovery:

```bash
python -m Backend.training_pipeline.run_batch --config Backend/training_pipeline/configs/source_resnet_6x64.json --pipeline-mode training --plan-only
mkdir -p /root/ludus-artifacts/runner-logs
nohup /opt/ludus-runner-venv/bin/python -u -m Backend.training_pipeline.run_batch --config Backend/training_pipeline/configs/source_resnet_6x64.json --pipeline-mode training > /root/ludus-artifacts/runner-logs/source-resnet-6x64-$(date -u +%Y%m%dT%H%M%SZ).log 2>&1 < /dev/null &
pgrep -af '[B]ackend.training_pipeline.run_batch'
```

`nohup` protects this runner from SSH hangups; it does not survive a VPS reboot.
Review general and simple-set accuracy/loss, available top-3 accuracy, sample
counts and training time for both runs. Missing older metrics must be recorded
as unavailable, not zero. Confirm evaluation samples are independent of training
before treating their scores as generalization evidence.

Prepare the [endgame dataset](endgame_dataset.md) independently; do not change
both the architecture and training distribution in this depth comparison.
