import os

import torch
from dataset import PhishingDataset
from torch_geometric.loader import DataLoader

from visualization import visualize
from models import GCN, GIN, MemPool


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

    # model = MemPool(
    #     in_channels=dataset.num_features,
    #     hidden_channels=32,
    #     out_channels=dataset.num_classes,
    #     device=device,
    # )
    # model = GIN(
    #     in_channels=dataset.num_features,
    #     hidden_channels=32,
    #     out_channels=dataset.num_classes,
    #     device=device,
    # ).to(device)
    model = GCN(
        in_channels=dataset.num_node_features,
        hidden_channels=64,
        out_channels=dataset.num_classes,
        device=device,
    ).to(device)
    print(model)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=4e-5)
    loss_fn = torch.nn.CrossEntropyLoss()


    for epoch in range(1, 171):
        loss = model.fit(train_loader, optimizer, loss_fn, device)
        train_acc = model.test(train_loader)
        test_acc = model.test(test_loader)
        print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}, Train Acc: {train_acc:.4f}, Test Acc: {test_acc:.4f}')
