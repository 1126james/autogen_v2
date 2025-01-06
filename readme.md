# Usage
1. pip install -r requirements.txt
2. use virtual env please
3. make sure you have a /sheets/sample.csv (or edit under if __name__ == "__main__")
4. python main.py

# Dataset used
https://www.kaggle.com/datasets/priyamchoksi/credit-card-transactions-dataset

Cant upload the file to github cuz of filesize, just download and put it into sheets/

## BUG
I have set the below termination condition, but sometimes the agents would infinitely loop, just ctrl+c to escape.

text_term = TextMentionTermination("TERMINATE")
len_term = MaxMessageTermination(9)
termination = text_term | len_term

## Findings
XML prompt with markdown table as data dict generates best results in terms of consistency and time.
