class ModelHyperparameters(object):
    def __init__(self, data: dict):
        self.type = data["type"]
        self.src_window_len = data["src_window_len"]
        self.tgt_window_len = data["tgt_window_len"]
        self.n_time_features = data["n_time_features"]
        self.n_linear_features = data["n_linear_features"]
        self.n_out_features = data["n_out_features"]
        self.d_time_embed = data["d_time_embed"]
        self.d_linear = data["d_linear"]
        self.n_head = data["n_head"]
        self.num_encoder_layers = data["num_encoder_layers"]
        self.dropout = data["dropout"]
        self.use_pos_enc = data["use_pos_enc"]


class TrainingHyperparameters(object):
    def __init__(self, data: dict):
        self.batch_size = data["batch_size"]
        self.n_epochs = data["n_epochs"]
        self.learning_rate = data["learning_rate"]
