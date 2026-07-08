import torch from pytorch

class AIManager:
    def __init__(self,parameters=None):
        self.parameters = parameters
    def use_model(self, model):
        #Check if the model is loaded by checking that .parameters() is not None
        if model.parameters():
           #do whatever 
            return

    def load_model(self, model_name):
        return torch.load(model_name,
                   map_location=torch.device("cpu"),
                   weights_only=True)
        




    