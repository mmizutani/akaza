import logging
import math
import os
from typing import List, Dict, Optional

from atomicwrites import atomic_write

from comb.node import Node


# ユーザー辞書。
#
# カタカナなどの単語の追加辞書。
# unigram score
# bigram score
class UserDict:
    unigram: Dict[str, int]

    def __init__(self, path, logger=logging.getLogger(__name__)):
        self.path = path
        self.logger = logger

        self.unigram = {}
        if os.path.exists(self.unigram_path()):
            self.read_unigram()
        else:
            self.total = 0

        self.bigram = {}
        self.bigram_total = {}
        if os.path.exists(self.bigram_path()):
            self.read_bigram()

    def unigram_path(self):
        return os.path.join(self.path, 'unigram.txt')

    def bigram_path(self):
        return os.path.join(self.path, 'bigram.txt')

    def read_unigram(self):
        total = 0
        with open(self.unigram_path()) as fp:
            for line in fp:
                m = line.rstrip().split("\t")
                if len(m) == 2:
                    kanji_kana, count = m
                    count = int(count)
                    self.unigram[kanji_kana] = count
                    total += count
            self.total = total

    def read_bigram(self):
        with open(self.bigram_path()) as fp:
            for line in fp:
                m = line.rstrip().split("\t")
                if len(m) == 3:
                    word1, word2, count = m
                    count = int(count)
                    self.bigram[f"{word1}\t{word2}"] = count
                    self.bigram_total[word1] = self.bigram_total.get(word1, 0) + 1

    def add_entry(self, nodes: List[Node]):
        # unigram
        for node in nodes:
            kanji = node.word
            kana = node.yomi

            self.logger.info(f"add user_dict entry: kana='{kana}' kanji='{kanji}'")

            key = node.get_key()
            self.unigram[key] = self.unigram.get(key, 0) + 1
            self.total += 1

        # bigram
        for i in range(1, len(nodes)):
            node1 = nodes[i - 1]
            node2 = nodes[i]
            key = node1.get_key() + "\t" + node2.get_key()
            self.bigram[key] = self.bigram.get(key, 0) + 1
            self.bigram_total[node1.get_key()] = self.bigram_total.get(node1.get_key(), 0) + 1

    def save(self):
        with atomic_write(self.unigram_path(), overwrite=True) as f:
            for kanji_kana in sorted(self.unigram.keys()):
                count = self.unigram[kanji_kana]
                f.write(f"{kanji_kana}\t{count}\n")

        with atomic_write(self.bigram_path(), overwrite=True) as f:
            for words in sorted(self.bigram.keys()):
                count = self.bigram[words]
                f.write(f"{words}\t{count}\n")

        self.logger.info(f"SAVED {self.path}")

    def get_unigram_cost(self, key: str) -> Optional[float]:
        if key in self.unigram:
            count = self.unigram[key]
            return math.log10(count / self.total)
        return None

    def get_bigram_cost(self, node1: Node, node2: Node) -> Optional[float]:
        key1 = node1.get_key()
        key2 = node2.get_key()
        key = key1 + "\t" + key2
        if key in self.bigram:
            count = self.bigram[key]
            return math.log10(count / self.bigram_total[key1])
        return None
