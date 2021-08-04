###
# source
# https://towardsdatascience.com/fine-tuning-pretrained-nlp-models-with-huggingfaces-trainer-6326a4456e7b
#

import os
import pandas as pd
import numpy as np
import argparse
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from transformers import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from transformers import EarlyStoppingCallback


from utils import read_imdb_test, read_imdb_train, IMDbDataset


def compute_metrics(p):
    pred, labels = p
    pred = np.argmax(pred, axis=1)

    accuracy = accuracy_score(y_true=labels, y_pred=pred)
    recall = recall_score(y_true=labels, y_pred=pred)
    precision = precision_score(y_true=labels, y_pred=pred)
    f1 = f1_score(y_true=labels, y_pred=pred)

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='bert-base-uncased')
    parser.add_argument('--gpu-id', default='gpu0')
    parser.add_argument('--data-dir', default="./../../asset/imdb/", type=str)
    parser.add_argument('--lr', default=2e-5, type=float)
    parser.add_argument('--seed', default=0, type=int)
    parser.add_argument('--train-bs', default=8, type=int)
    parser.add_argument('--weight-decay', default=0.01, type=float)

    return parser.parse_args()
    

def main() :

    args = get_args()
    
    DATA_DIR = args.data_dir

    train_texts, train_labels = read_imdb_train(DATA_DIR)

    # check_data()

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        train_texts, train_labels, test_size=.2)

    train_texts = list(train_texts)
    val_texts = list(val_texts)
    train_labels = list(train_labels)
    val_labels = list(val_labels)

    model_name = args.model
    gpu_id = args.gpu_id
    # model_name = "bert-base-cased"
    # gpu_id = "gpu0"
    # model_name = "roberta-base"
    # model_name = "microsoft/deberta-large-mnli"
    # model_name = "bert-base-uncased"
    # gpu_id = "gpu1"

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # check_data()

    train_encodings = tokenizer(
        train_texts, truncation=True, padding=True, max_length=512)
    val_encodings = tokenizer(
        val_texts, truncation=True, padding=True, max_length=512)

    train_dataset = IMDbDataset(train_encodings, train_labels)
    val_dataset = IMDbDataset(val_encodings, val_labels)

    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    training_args = TrainingArguments(
        # output directory
        output_dir=f'./results/{model_name}/{gpu_id}/',
        num_train_epochs=10,              # total number of training epochs
        per_device_train_batch_size=args.train_bs,  # batch size per device during training
        per_device_eval_batch_size=64,   # batch size for evaluation
        warmup_steps=500,                # number of warmup steps for learning rate scheduler
        weight_decay=0.01,               # strength of weight decay
        # directory for storing logs
        logging_dir=f'./logs/{model_name}/{gpu_id}/',
        logging_steps=500,
        learning_rate=2e-5,
        seed=0,
        evaluation_strategy="steps",
        load_best_model_at_end=True
    )

    # trainer = Trainer(
    #     # the instantiated 🤗 Transformers model to be trained
    #     model=model,
    #     args=training_args,                  # training arguments, defined above
    #     train_dataset=train_dataset,         # training dataset
    #     eval_dataset=val_dataset,             # evaluation dataset
    #     compute_metrics=compute_metrics,
    # )

    trainer = Trainer(
        # the instantiated 🤗 Transformers model to be trained
        model=model,
        args=training_args,                  # training arguments, defined above
        train_dataset=train_dataset,         # training dataset
        eval_dataset=val_dataset,             # evaluation dataset
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(
            early_stopping_patience=5)],

    )

    trainer.train()


if __name__ == "__main__" :
    main()
