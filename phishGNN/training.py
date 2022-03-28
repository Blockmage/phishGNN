import os
import itertools
import json
from collections import defaultdict
from pprint import pprint

import torch
import torch_geometric.nn as nn
from dataset import PhishingDataset
from torch_geometric.loader import DataLoader

from visualization import visualize, plot_embeddings
from models import GCN, GIN, GAT, GraphSAGE, ClusterGCN, MemPool
from utils.utils import mean_std_error


def fit(
    train_loader,
    optimizer,
    loss_fn,
    device,
):
    model.train()

    total_loss = 0
    for data in train_loader:
        data = data.to(device)
        out = model(data.x, data.edge_index, data.batch)
        loss = loss_fn(out, data.y.long())
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += float(loss) * data.num_graphs
    
    return total_loss / len(train_loader.dataset)


@torch.no_grad()
def test(loader):
    model.eval()

    correct = 0
    for data in loader:
        out = model(data.x, data.edge_index, data.batch)  
        pred = out.argmax(dim=1)
        correct += int((pred == data.y).sum())

    return correct / len(loader.dataset)


if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "data")
    dataset = PhishingDataset(root=path, use_process=False, visulization_mode=False)
    dataset = dataset.shuffle()

    train_test = 0.8
    train_dataset = dataset[:int(len(dataset) * train_test)]
    test_dataset = dataset[int(len(dataset) * train_test):]

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    models = [
        GAT,
        GIN,
        GCN,
        ClusterGCN,
        GraphSAGE,
        MemPool,
    ]

    poolings = [
        nn.global_mean_pool,
        nn.global_max_pool,
        nn.global_add_pool,
    ]

    hidden_neurons = [
        32,
        64,
        128,
    ]

    lr = 0.01
    weight_decay = 4e-5
    epochs = 10
    
    accuracies = defaultdict(lambda: [])
    for (model, pooling, neurons) in itertools.product(
        models,
        poolings,
        hidden_neurons,
    ):
        model = model(
            in_channels=dataset.num_features,
            hidden_channels=neurons,
            out_channels=dataset.num_classes,
            pooling_fn=pooling,
            device=device,
        )
        print(f"\n{model.__class__.__name__}, {pooling.__name__}, {neurons}")

        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        loss_fn = torch.nn.CrossEntropyLoss()

        fit_fn = model.fit if hasattr(model, 'fit') else fit
        test_fn = model.test if hasattr(model, 'test') else test

        train_accs, test_accs = [], []
        for epoch in range(epochs):
            loss = fit_fn(train_loader, optimizer, loss_fn, device)
            train_acc = test_fn(train_loader)
            test_acc = test_fn(test_loader)

            train_accs.append(train_acc)
            test_accs.append(test_acc)
            print(f'Epoch: {(epoch+1):03d}, Loss: {loss:.4f}, Train Acc: {train_acc:.4f}, Test Acc: {test_acc:.4f}')

        accuracies[model.__class__.__name__].append({
            f'{pooling.__name__}, {neurons}': {
                'train': mean_std_error(train_accs),
                'test':  mean_std_error(test_accs),
            }
        })

        with open('training.logs', 'w') as logs:
            formatted = json.dumps(accuracies, indent=2)
            logs.write(formatted)
        
        # loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
        # plot_embeddings(model, loader)
    
    pprint(accuracies)
