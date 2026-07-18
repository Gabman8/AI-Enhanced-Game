import torch

class AIManager:
    def load_model(self, model_name):
        return torch.load(f"models/{model_name}",
                   map_location=torch.device("cpu"),
                   weights_only=True)
        




    