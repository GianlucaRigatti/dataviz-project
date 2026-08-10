import torch
from torch import nn
import pytorch_lightning as pl

class VehicleAutoencoder(pl.LightningModule):
    def __init__(
        self, 
        input_dim: int = 5, 
        latent_dim: int = 2, 
        lr: float = 1e-3, 
        weight_decay: float = 1e-4
    ):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8),
            nn.GELU(),
            nn.Linear(8, latent_dim)
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 8),
            nn.GELU(),
            nn.Linear(8, input_dim)
        )
        
        self.loss_fn = nn.MSELoss()
        self.lr = lr
        self.weight_decay = weight_decay

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return x_hat

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)

    def training_step(self, batch: tuple, batch_idx: int) -> torch.Tensor:
        x = batch[0]
        x_hat = self(x)
        loss = self.loss_fn(x_hat, x)
        self.log("train_loss", loss, prog_bar=True, on_epoch=True, on_step=False)
        return loss

    def validation_step(self, batch: tuple, batch_idx: int) -> torch.Tensor:
        x = batch[0]
        x_hat = self(x)
        loss = self.loss_fn(x_hat, x)
        self.log("val_loss", loss, prog_bar=True, on_epoch=True, on_step=False)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(
            self.parameters(), 
            lr=self.lr, 
            weight_decay=self.weight_decay
        )
        
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, 
            mode="min", 
            factor=0.5, 
            patience=15
        )
        
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val_loss",
                "interval": "epoch",
                "frequency": 1
            },
        }