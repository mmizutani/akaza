from comb.combromkan import to_hiragana
import pytest
import marisa_trie
from comb.system_dict import SystemDict
from comb.graph import lookup, graph_construct, viterbi
import logging

unigram_score = marisa_trie.RecordTrie('@f')
unigram_score.load('model/jawiki.1gram')

bigram_score = marisa_trie.RecordTrie('@f')
bigram_score.load('model/jawiki.2gram')

system_dict = SystemDict()


logging.basicConfig(level=logging.DEBUG)


@pytest.mark.parametrize('src, expected', [
    # Wnn で有名なフレーズ。
    ('わたしのなまえはなかのです', '私の名前は中野です'),
    # カタカナ語の処理が出来ていること。
    ('わーど', 'ワード'),
    ('にほん', '日本'),
    ('ややこしい', 'ややこしい'),
    ('むずかしくない', '難しくない'),
    ('きぞん', '既存'),
    ('のぞましい', '望ましい'),
    ('こういう', 'こういう'),
    ('はやくち', '早口'),
    ('どっぐふーでぃんぐしづらい', 'ドッグフーディング仕辛い'),
])
def test_wnn(src, expected):
    ht = dict(lookup(src, system_dict))
    graph = graph_construct(src, ht, unigram_score, bigram_score)

    clauses = viterbi(graph)
    got = ''.join([clause[0].word for clause in clauses])

    assert got == expected
