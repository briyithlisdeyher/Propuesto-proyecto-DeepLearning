"""MLP de la Fase 1 del Proyecto Centinela (mismo código que la sección 6 del notebook).

La salida es un LOGIT: no hay nn.Sigmoid dentro del modelo. Se entrena con
nn.BCEWithLogitsLoss y torch.sigmoid se aplica solo al evaluar.
"""
import torch.nn as nn


class MLP(nn.Module):
    def __init__(self, n_feat, ocultas=(16, 8), p_dropout=0.0):
        super().__init__()
        capas, entrada = [], n_feat
        for h in ocultas:
            capas += [nn.Linear(entrada, h), nn.ReLU(), nn.Dropout(p_dropout)]
            entrada = h
        capas.append(nn.Linear(entrada, 1))  # salida: logit
        self.red = nn.Sequential(*capas)

    def forward(self, x):
        return self.red(x)
