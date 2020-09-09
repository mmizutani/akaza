from logging import Logger
from typing import List, Any

import os

import jaconv

from comb import combromkan

from comb.system_dict import SystemDict
from comb.user_dict import UserDict
from comb.graph import graph_construct, viterbi, lookup, Node
from comb.config import MODEL_DIR
import logging
import marisa_trie

from datetime import date


class Candidate:
    def __init__(self, word: str):
        self.word = word


class Comb:
    logger: Logger
    dictionaries: List[Any]

    def __init__(self, logger: Logger, user_dict: UserDict, system_dict: SystemDict):
        self.logger = logger
        self.dictionaries = []
        self.user_dict = user_dict
        self.system_dict = system_dict

        self.unigram_score = marisa_trie.RecordTrie('@f')
        self.unigram_score.load(f"{MODEL_DIR}/jawiki.1gram")

        self.bigram_score = marisa_trie.RecordTrie('@f')
        self.bigram_score.load(f"{MODEL_DIR}/jawiki.2gram")

    # 連文節変換するバージョン。
    def convert2(self, src: str) -> List[List[Node]]:
        hiragana: str = combromkan.to_hiragana(src)
        katakana: str = jaconv.hira2kata(hiragana)
        self.logger.info(f"convert: src={src} hiragana={hiragana} katakana={katakana}")

        ht = dict(lookup(hiragana, self.system_dict))
        graph = graph_construct(hiragana, ht, self.unigram_score, self.bigram_score)
        clauses = viterbi(graph)
        return clauses

    # 連文節しないバージョン(しばらくのあいだ、残しておく。)
    # TODO: remove this.
    def convert(self, src):
        hiragana: str = combromkan.to_hiragana(src)
        katakana: str = jaconv.hira2kata(hiragana)

        self.logger.info(f"convert: src={src} hiragana={hiragana} katakana={katakana}")

        candidates = [[hiragana, hiragana]]

        for e in self.user_dict.get_candidates(src, hiragana):
            if e not in candidates:
                candidates.append(e)

        if hiragana == 'きょう':
            # こういう類の特別なワードは、そのまま記憶してはいけない。。。
            today = date.today()
            for dt in [today.strftime(fmt) for fmt in ['%Y-%m-%d', '%Y年%m月%d日']]:
                candidates.append([dt, dt])

        try:
            ht = dict(lookup(hiragana, self.system_dict))
            graph = graph_construct(hiragana, ht, self.unigram_score, self.bigram_score)
            got = viterbi(graph)

            phrase = ''.join([x.word for x in got if not x.is_eos()])

            self.logger.info(f"Got phrase: {phrase}")

            if [phrase, phrase] not in candidates:
                candidates.append([phrase, phrase])
        except:
            self.logger.error(f"Cannot convert: {hiragana} {katakana}",
                              exc_info=True)

        if [katakana, katakana] not in candidates:
            candidates.append([katakana, katakana])

        for e in [[x, x] for x in self.system_dict.get_candidates(src, hiragana)]:
            if e not in candidates:
                candidates.append(e)

        if src[0].isupper():
            # 先頭が大文字の場合、それを先頭にもってくる。
            candidates.insert(0, [src, src])
        else:
            # そうじゃなければ、末尾にいれる。
            candidates.append([src, src])

        return candidates


if __name__ == '__main__':
    from gi.repository import GLib
    import pathlib
    import logging

    logging.basicConfig(level=logging.DEBUG)

    configdir = os.path.join(GLib.get_user_config_dir(), 'ibus-comb')
    pathlib.Path(configdir).mkdir(parents=True, exist_ok=True)
    d = SystemDict()
    u = UserDict(os.path.join(configdir, 'user-dict.txt'))
    comb = Comb(logging.getLogger(__name__), u, d)
    # print(comb.convert('henkandekiru'))
    print(comb.convert('watasi'))
    # print(comb.convert('hituyoudayo'))
    # print(list(d.get_candidates('henkandekiru', 'へんかんできる')))
    # print(list(d.get_candidates('warudakumi', 'わるだくみ')))
    # print(list(d.get_candidates('subarasii', 'すばらしい')))
    # print(list(d.get_candidates('watasi', 'わたし')))
    # print(list(d.get_candidates('hiragana', 'ひらがな')))
    # print(list(d.get_candidates('buffer', 'ぶっふぇr')))