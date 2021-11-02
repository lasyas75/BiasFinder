# BiasFinder: Uncovering Bias in Sentiment Analysis Systems through Metamorphic Testing

### Overview

Artificial Intelligence (AI) systems, such as Sentiment Analysis (SA) systems, typically learn from large amounts of data that may reflect human biases. Consequently, SA systems may exhibit unintended demographic bias based on specific characteristics (e.g., gender, occupation, country-of-origin, etc.)  Such biases manifest in an SA system when it predicts a different sentiment for similar texts that differ only in the characteristic of individuals described. Existing studies on revealing bias in SA systems rely on the production of sentences from a small set of
short, predefined templates. 

To address this limitation, we present **BiasFinder**, an approach to discover biased predictions in SA systems via metamorphic testing. A key feature of BiasFinder is the automatic curation of suitable templates based on the pieces of text from a large corpus, using various Natural Language Processing (NLP) techniques to identify words that describe demographic characteristics. Next, BiasFinder instantiates new text from these templates by filling in placeholders with words associated with a class of a characteristic (e.g., gender-specific words such as female names, “she”, “her”). These texts are used to tease out bias in an SA system. 

**BiasFinder** identifies a bias-uncovering test case (BTC) when it detects that the SA system exhibits demographic bias for a pair of texts, i.e., it predicts a different sentiment for texts that differ only in words associated with a different class (e.g., male vs. female) of a target characteristic (e.g., gender). Our empirical evaluation showed that BiasFinder can effectively create a large number of realistic and diverse test cases that uncover various biases in an SA system with a high true positive rate.

## Requirements

For fine-tuning SA, we use [HuggingFace](https://huggingface.co) library that provide many pre-trained language models, including BERT, RoBERTa, and XLNET.

For nlp task, please install thess libraries:
+ spacy (need `en_core_web_lg`)
+ pandas
+ numpy
+ scikit-learn
+ nltk
+ neuralcoref
+ fastNLP

For occupation bias, you need StanfordCoreNLP and several libraries:
+ inflect
+ pycorenlp -> [Stackoverflow Guide to serve StanfordCoreNLP as an API](https://stackoverflow.com/questions/32879532/stanford-nlp-for-python)


For preparing data from [genderComputer](https://github.com/tue-mdse/genderComputer), please install thess libraries:
+ python-nameparser
+ unidecode

**Tips**: you may use docker for faster implemention on your coding environment. https://hub.docker.com/r/pytorch/pytorch/tags provide several version of PyTorch containers. Please pull the appropiate pytorch container with the tag 1.9 version, using this command.

```
docker pull pytorch/pytorch:1.9.0-cuda10.2-cudnn7-devel
```


## Setup Dataset and BERT fine-tuning model

### 1) Prepare the dataset 

dataset | description
------------ | -------------
`asset/imdb/` | We use IMDB movie review dataset downloaded from [Google Drive](https://drive.google.com/drive/u/0/folders/0Bz8a_Dbh9Qhbfll6bVpmNUtUcFdjYmF2SEpmZUZUcVNiMUw1TWN6RDV3a0JHT3kxLVhVR2M) proposed by [Zhang et al. (2015)](https://papers.nips.cc/paper/5782-character-level-convolutional-networks-for-text-classification.pdf). 
`asset/gender_associated_word/` | It contains pre-determined values for Gender Associated Words
`asset/gender_computer/` | It contains a notebook `asset/gender_computer/genderComputer/prepare_male_female_names.ipynb` to prepare the names for **BiasFinder** experiment.
`asset/predefined_occupation_list/neutral-occupation.csv/` | It contains pre-determined words for neutral occupations 


### 2) Fine-Tune SA systems

Run this command inside the `codes/fine-tuning/` folder to fine-tune SA models.

```
bash fine-tune-imdb.sh
bash fine-tune-twitter-s140.sh
```

Then check the test accuracy of the fine-tuned models
```
bash test-imdb.sh
bash test-twitter-s140.sh
```

Check the accuracy in `codes/evaluation/Model-Performance.ipynb`


## Mutant Generation

Our framework, **BiasFinder**, can be instantiated to identify different kinds of bias. In this work, we show how BiasFinder can be instantiated to uncover bias in three different demographic characteristics: gender, occupation, and country-oforigin.

BiasFinder automatically identifies and curates suitable texts in a large corpus of reviews, and transforms these texts into templates. Each template can be used to produce a large number of mutant texts, by filling in placeholders with concrete values associated with a class (e.g., male vs. female) given a demographic characteristic (e.g., gender)(See Section III and IV). Using these mutant texts, **BiasFinder** then runs the SA system under test, checking if it predicts the same sentiment for two mutants associated with a different class (e.g. male vs. female) of the given characteristic (e.g. gender). A pair of such mutants are related through a metamorphic relation where they share the same predicted sentiment from a fair SA system (See Section V and VI).

### 1) Gender Bias
Run this command inside the `codes/gender/` folder

```
bash biasfinder-generate-mutant.sh
```

Some trouble shooting:

* If you face a problem with `neuralcoref`, please build the library from the source instead of installing using pip. Check [here](https://github.com/huggingface/neuralcoref).

* You also need to run the following commands if you meet problem `ModuleNotFoundError: No module named 'en_core_web_lg'`.

```
python -m spacy download en
python -m spacy download en_core_web_lg
```

This code will generate mutant texts for gender and saved the mutant texts inside a folder `data/biasfinder/gender/`

### 2) Occupation Bias

Run this command inside the `codes/occupation/` folder

```
python main.py
```

This code will generate mutant texts for occupation and saved the mutant texts inside a folder `data/biasfinder/occupation/`. **Important note:** Occupation bias need StanfordCoreNLP to detect occupation term in the text. Thus please make sure to serve StanfordCoreNLP as an API - [Stackoverflow Guide to serve StanfordCoreNLP as an API](https://stackoverflow.com/questions/32879532/stanford-nlp-for-python).

### 3) Country-of-origin Bias

Run this command inside the `codes/country/` folder

```
bash generate-country-mutant.sh
```

This code will generate mutant texts for country-of-origin and saved the mutant texts inside a folder `data/biasfinder/country/`

## Predict The Mutant Texts using Fine-tuned BERT

### 1) IMDB Experiments
Run this command inside the `codes/fine-tuning/` folder

```
bash predict-imdb.sh
```

This code will produce the prediction of mutant texts.

### 2) Twitter Experiments

Run this command inside the `codes/fine-tuning/` folder

```
bash predict-twitter-s140.sh
```

This code will produce the prediction of mutant texts.


## Measuring the Bias Uncovering Test Case (BTC)

Mutants of differing classes that are produced from the same template are expected to have the same sentiment. Therefore, if the SA predicts that two mutants of different classes to have different sentiments, they are an evidence of a biased prediction. Such pairs of mutants are output as **bias-uncovering test cases (BTC)**. Thus BTC is a pair that contains 2 different class (e.g. male female for gender bias) and their predictions, such that the Sentiment Analysis produce a different prediction. 
Example of BTC for gender bias: 

`<(male, prediction), (female, prediction)>`

`<(“He is angry”, "positive"), (“She is angry”, "negative")>`

### 1) Gender Bias

Notebook `evaluation/BTC-Gender.ipynb` contains the BTC calculation for gender bias targeting mutant texts.

### 2) Occupation Bias

Notebook `evaluation/BTC-Occupation.ipynb` contains the BTC calculation for occupation bias targeting mutant texts.

### 3) Country-of-origin Bias

Notebook `evaluation/BTC-Country.ipynb` contains the BTC calculation for country-of-origin bias targeting mutant texts.
