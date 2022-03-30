import torch
from torch import nn


class FeedforwardNeuralNetModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(FeedforwardNeuralNetModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim) 
        self.sigmoid = nn.Sigmoid()
        self.fc2 = nn.Linear(hidden_dim, output_dim)  

    def forward(self, x):
        x = torch.tensor(x)
        x = x.float()
        out = self.fc1(x)

        out = self.sigmoid(out)
        out = self.fc2(out)
        return out

    def fit(
        self,
        X_train,
        y_train,
        optimizer,
        loss_fn,
    ):
        self.train()

        total_loss = 0
        for (x, y) in zip(X_train, y_train):
            out = self(x)
            loss = loss_fn(out, torch.tensor(y))
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            total_loss += float(loss)
        
        return total_loss / len(y_train)

    @torch.no_grad()
    def test(self, X_test, y_test):
        self.eval()

        correct = 0
        for (x, y) in zip(X_test, y_test):
            out = self(x)
            # dim -1 instead of 1
            pred = out.argmax(dim=-1)
            correct += int((pred == y).sum())

        return correct / len(y_test)