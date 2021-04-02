import argparse
from typing import Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
import yaml
from torch import Tensor

from hyperparameters import ModelHyperparameters, TrainingHyperparameters
from time_transformer import AbbreviatedTimeTransformer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_rand_data(
    mp: ModelHyperparameters, tp: TrainingHyperparameters
) -> Tuple[Tensor, Tensor]:
    r"""Returns random data for testing the model.

    Shapes
        src: (S, N, F)
        tgt: (S, N)
    """
    src = torch.randn(
        mp.src_window_len, tp.batch_size, mp.n_time_features + mp.n_linear_features
    ).to(device)

    tgt = torch.randint(
        low=0, high=mp.n_out_features, size=(mp.src_window_len, tp.batch_size)
    ).to(device)

    return src, tgt


def get_encoder_decoder_rand_data(
    mp: ModelHyperparameters, tp: TrainingHyperparameters
) -> Tuple[Tensor, Tensor]:
    r"""Returns random data for testing the model.

    Shapes
        src: (S, N, F)
        tgt: (T, N)
    """
    src = torch.randn(
        mp.src_window_len, tp.batch_size, mp.n_time_features + mp.n_linear_features
    ).to(device)

    tgt = torch.randint(
        low=0, high=mp.n_out_features, size=(mp.tgt_window_len, tp.batch_size)
    ).to(device)

    return src, tgt


def get_data(
    mp: ModelHyperparameters, tp: TrainingHyperparameters
) -> Tuple[Tensor, Tensor]:
    if mp.type == "abbreviated":
        return get_rand_data(mp, tp)
    elif mp.type == "variable":
        return get_encoder_decoder_rand_data(mp, tp)
    else:
        raise ValueError("Model type must be one of abbreviated or variable.")


def get_model(mp: ModelHyperparameters):
    if mp.type == "abbreviated":
        return AbbreviatedTimeTransformer.model_from_mp(mp, device)
    elif mp.type == "variable":
        return VariableTimeTransformer.model_from_mp(mp, device)
    else:
        raise ValueError("Model type must be one of abbreviated or variable.")


def print_progress(epoch: int, n_epochs: int, loss: float):
    print(
        f"\r[Overfit Epoch {epoch + 1} / {n_epochs}] Loss: {loss}", end="", flush=True
    )


def debug(cfg: dict):
    mp = ModelHyperparameters(cfg["model"])
    tp = TrainingHyperparameters(cfg["training"])

    src, tgt = get_data(mp, tp)

    model = get_model(mp)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=tp.learning_rate)

    start_loss, end_loss = 0, 0
    writer = SummaryWriter(f"runs/debug")
    step = 0

    for epoch in range(tp.n_epochs):
        out = model(src)

        out = out.reshape(-1, mp.n_out_features)

        loss = criterion(out, tgt.reshape(-1))

        optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)
        optimizer.step()

        num_correct = (out.argmax(dim=-1) == tgt.reshape(-1)).sum()
        running_train_acc = float(num_correct) / float(tgt.shape[0])

        writer.add_scalar("Training Loss", loss, global_step=step)
        writer.add_scalar("Training Accuracy", running_train_acc, global_step=step)
        step += 1

        if epoch == 0:
            start_loss = loss.item()
        else:
            end_loss = loss.item()

        print_progress(epoch, tp.n_epochs, loss.item())

    print(f"\nStart Loss: {start_loss} | End Loss: {end_loss}")


def main(cfg: dict):
    mp = ModelHyperparameters(cfg["model"])
    tp = TrainingHyperparameters(cfg["training"])

    src, tgt = get_rand_data(mp, tp)

    model = get_model(mp)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=tp.learning_rate)

    start_loss, end_loss = 0, 0

    for epoch in range(tp.n_epochs):
        out = model(src)
        out = out.reshape(-1, mp.n_out_features)

        loss = criterion(out, tgt.reshape(-1))

        optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)
        optimizer.step()

        if epoch == 0:
            start_loss = loss.item()
        else:
            end_loss = loss.item()

        print_progress(epoch, tp.n_epochs, loss.item())

    print(f"\nStart Loss: {start_loss} | End Loss: {end_loss}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", required=True, type=str, help="Path to .yaml config file"
    )
    parser.add_argument(
        "-d", "--debug", default=False, type=bool, help="Flag to run in debug mode."
    )

    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    if args.debug:
        debug(config)
    else:
        main(config)
