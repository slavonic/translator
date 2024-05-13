import lightning as L
import torch
import torch.nn.functional as F


class Model(L.LightningModule):

    def __init__(self, vocab_size, max_seq_len, *,
        emb_dim=64,
        hidden_dim=128,
        dropout=0.1,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.emb_dim = emb_dim
        self.hidden_dim = hidden_dim

        self.embed = torch.nn.Embedding(self.vocab_size, self.emb_dim)
        self.lstm = torch.nn.GRU(self.emb_dim, self.hidden_dim, bidirectional=True, batch_first=True, num_layers=3, dropout=dropout)

        self.ff1 = torch.nn.Linear(self.hidden_dim * 2, self.hidden_dim * 4)
        self.dropout = torch.nn.Dropout(dropout)
        self.ff2 = torch.nn.Linear(self.hidden_dim * 4, 2)

        self.loss = torch.nn.NLLLoss()

    def forward(self, x, lengths=None):
        '''
        x: batch of sequences: [B, S] int64
        lengths: [B] int64
        '''
        x = self.embed(x)  # [B, S, E]
        x = self.dropout(x)
        x, _ = self.lstm(x)
        x = self.ff1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.ff2(x)   # [B, 3S, V]
        x = F.log_softmax(x, dim=-1)
        return x

    def training_step(self, batch, batch_idx):
        logits = self.forward(batch['in'], batch['len'])
        logits = logits.transpose(1, 2)
        loss = self.loss(logits, batch['out'])
        self.log('train_loss', loss, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        logits = self.forward(batch['in'], batch['len'])
        logits = logits.transpose(1, 2)
        loss = self.loss(logits, batch['out'])
        self.log('val_loss', loss, prog_bar=True)

    def configure_optimizers(self):
        opt = torch.optim.Adam(self.parameters(), lr=0.001)
        sch = torch.optim.lr_scheduler.CyclicLR(opt, base_lr=0.0001, max_lr=0.005, step_size_up=1000, cycle_momentum=False)
        return [opt], [{
            'scheduler': sch,
            'interval' : 'step',
            'frequency': 1,
        }]