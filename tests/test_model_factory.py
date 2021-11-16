# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.
#
# This source code is licensed under the BSD license found in the
# LICENSE file in the root directory of this source tree.

import pytest
import torch

from xformers.factory.model_factory import xFormer, xFormerConfig

BATCH = 20
SEQ = 512
EMB = 384
DEVICES = (
    [torch.device("cpu")]
    if not torch.cuda.is_available()
    else [
        torch.device("cuda")
    ]  # save a bit on CI for now, we have seperate cpu and gpu jobs
)

test_configs = [
    [
        {
            "reversible": False,
            "block_type": "encoder",
            "dim_model": 384,
            "position_encoding_config": {
                "name": "vocab",
                "seq_len": SEQ,
                "vocab_size": 64,
                "dim_model": EMB,
            },
            "num_layers": 3,
            "multi_head_config": {
                "num_heads": 4,
                "residual_dropout": 0,
                "attention": {
                    "name": "linformer",
                    "dropout": 0,
                    "causal": True,
                    "seq_len": 512,
                },
                "dim_model": EMB,
            },
            "feedforward_config": {
                "name": "MLP",
                "dropout": 0,
                "activation": "relu",
                "hidden_layer_multiplier": 4,
                "dim_model": EMB,
            },
        },
        {
            "block_type": "decoder",
            "dim_model": 384,
            "position_encoding_config": {
                "name": "vocab",
                "seq_len": SEQ,
                "vocab_size": 64,
                "dim_model": EMB,
            },
            "num_layers": 2,
            "multi_head_config_masked": {
                "num_heads": 4,
                "residual_dropout": 0,
                "dim_model": EMB,
                "attention": {
                    "name": "linformer",
                    "dropout": 0,
                    "causal": True,
                    "seq_len": 512,
                },
            },
            "multi_head_config_cross": {
                "num_heads": 4,
                "residual_dropout": 0,
                "dim_model": EMB,
                "attention": {
                    "name": "linformer",
                    "dropout": 0,
                    "causal": True,
                    "seq_len": 512,
                },
            },
            "feedforward_config": {
                "name": "MLP",
                "dropout": 0,
                "activation": "relu",
                "hidden_layer_multiplier": 4,
                "dim_model": EMB,
            },
        },
    ]
]


""" Test all the model configurations saved in model_presets. """


@pytest.mark.parametrize("config", test_configs)
@pytest.mark.parametrize("reversible", [True, False])
@pytest.mark.parametrize("device", DEVICES)
def test_presets(config, reversible, device):
    # Build the model
    config[0]["reversible"] = reversible
    model = xFormer.from_config(xFormerConfig(config)).to(device)

    # Dummy inputs, test a forward
    inputs = (torch.rand((BATCH, SEQ), device=device) * 10).abs().to(torch.int)

    input_mask = torch.randn(SEQ, dtype=torch.float, device=device)
    input_mask[input_mask < 0.0] = -float("inf")
    _ = model(inputs, encoder_input_mask=input_mask, decoder_input_mask=input_mask)
