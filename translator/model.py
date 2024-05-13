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
        self.embed_accent = torch.nn.Embedding(2, self.emb_dim)  # just yes/no
        self.upsample = torch.nn.Upsample(scale_factor=2, mode='nearest')
        self.lstm = torch.nn.GRU(self.emb_dim, self.hidden_dim, bidirectional=True, batch_first=True, num_layers=3, dropout=dropout)
        # self.conv1 = torch.nn.Conv1d(self.emb_dim, self.hidden_dim, 3, padding=1)
        # self.conv2 = torch.nn.Conv1d(self.hidden_dim, self.hidden_dim, 3, padding=1)
        # self.conv3 = torch.nn.Conv1d(self.hidden_dim, self.hidden_dim, 3, padding=1)

        self.ff1 = torch.nn.Linear(self.hidden_dim * 2, self.hidden_dim * 4)
        self.dropout = torch.nn.Dropout(dropout)
        self.ff2 = torch.nn.Linear(self.hidden_dim * 4, self.vocab_size)

        self.loss = torch.nn.CTCLoss()

    def forward(self, x, a, lengths=None):
        '''
        x: batch of sequences: [B, S] int64
        lengths: [B] int64
        '''
        x = self.embed(x) + self.embed_accent(a) # [B, S, E]
        x = self.upsample(x.transpose(1,2)).transpose(1,2)  # [B, 2S, E]
        x = self.dropout(x)
        x, _ = self.lstm(x)
        x = self.ff1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.ff2(x)   # [B, 3S, V]
        x = F.log_softmax(x, dim=-1)
        return x

    def training_step(self, batch, batch_idx):
        logits = self.forward(batch['ru'], batch['ru_acc'], batch['ru_len'])
        logits = logits.transpose(0, 1)
        input_lens = torch.full(size=(logits.shape[1],), fill_value=logits.shape[0], dtype=torch.long, device=logits.device)
        loss = self.loss(logits, batch['cu'], input_lens.detach(), batch['cu_len'].detach())
        self.log('train_loss', loss, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        logits = self.forward(batch['ru'], batch['ru_acc'], batch['ru_len'])
        logits = logits.transpose(0, 1)
        input_lens = torch.full(size=(logits.shape[1],), fill_value=logits.shape[0], dtype=torch.long, device=logits.device)
        loss = self.loss(logits, batch['cu'], input_lens.detach(), batch['cu_len'].detach())
        self.log('val_loss', loss, prog_bar=True)

    def configure_optimizers(self):
        opt = torch.optim.Adam(self.parameters(), lr=0.001)
        sch = torch.optim.lr_scheduler.CyclicLR(opt, base_lr=0.0001, max_lr=0.005, step_size_up=1000, cycle_momentum=False)
        return [opt], [{
            'scheduler': sch,
            'interval' : 'step',
            'frequency': 1,
        }]