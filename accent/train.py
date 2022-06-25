import torch
import pytorch_lightning as pl
from accent.accent_dataset import AccentDataset
from pytorch_lightning.loggers import WandbLogger
from accent.model import Model
import torch

def main(max_epochs=20, max_steps=100_000, max_chars=32, load_checkpoint=None, resume=False, save_checkpoint='model.ckpt'):

    datamodule = AccentDataset()
    datamodule.prepare_data()

    model = Model(datamodule.vocab_size, max_chars)
    if load_checkpoint is not None:
        if not resume:
            # here I load only model weights, but not optimizer state - because
            # I want to be able to update LR and scheduler in code and still start
            # training from a checkpoint
            x = torch.load(load_checkpoint)
            model.load_state_dict(x['state_dict'])
        else:
            model = Model.load_from_checkpoint(load_checkpoint, vocab_size=datamodule.vocab_size, max_seq_len=max_chars)

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        max_steps=max_steps,
        logger=WandbLogger(log_model=True, project='hyphenator'),
        # resume_from_checkpoint=load_checkpoint,
        callbacks=[pl.callbacks.LearningRateMonitor(logging_interval='step')],
    )
    trainer.fit(model, datamodule)

    trainer.save_checkpoint(save_checkpoint)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='train the model')
    parser.add_argument('-e', '--epochs', type=int, default=20, help='How many epochs to train')
    parser.add_argument('-t', '--steps', type=int, default=100_000, help='How many steps to train')
    parser.add_argument('-m', '--max_chars', type=int, default=32, help='Max chars in a word')
    parser.add_argument('-l', '--load', help='Load a checkpoint')
    parser.add_argument('-r', '--resume', action='store_true', help='Resume training (restore model AND optimizer state)')
    parser.add_argument('-s', '--save', default='model-accent.ckpt', help='Save trained model as (default is "model.ckpt")')

    args = parser.parse_args()

    parser.exit(main(
        max_epochs=args.epochs,
        max_steps=args.steps,
        max_chars=args.max_chars,
        load_checkpoint=args.load,
        resume=args.resume,
        save_checkpoint=args.save,
    ))
