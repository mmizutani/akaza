# ibus-akaza

Yet another kana-kanji-converter on IBus, written in Rust.

統計的かな漢字変換による日本語IMEです。
Rust で書いています。

**現在、開発途中のプロダクトです。非互換の変更が予告なくはいります**

## モチベーション

いじりやすくて **ある程度** UIが使いやすいかな漢字変換があったら面白いなと思ったので作ってみています。
「いじりやすくて」というのはつまり、Hack-able であるという意味です。

モデルデータを自分で生成できて、特定の企業に依存しない自由なかな漢字変換エンジンを作りたい。

## 特徴

* UI/Logic をすべて Rust で書いてあるので、拡張が容易です。
* 統計的かな漢字変換モデルを採用しています
    * 言語モデルの生成元は日本語 Wikipedia と青空文庫です。
        * 形態素解析器 Vibrato で分析した結果をもとに 2gram 言語モデルを構築しています。
        * 利用者の環境で 1 から言語モデルを再生成することが可能です。
* ユーザー環境で、利用者の変換結果を学習します(unigram, bigramの頻度を学習します)

## Dependencies

### Runtime dependencies

* ibus
* marisa-trie

### Build time dependencies

* rust

### Supported environment

* Linux 6.0 以上
* ibus 1.5 以上

## Install 方法

モデルファイルをダウンロードして展開してください。

    mkdir /usr/share/akaza/
    curl -L https://github.com/tokuhirom/akaza/releases/download/<<VERSION>>/akaza-data.tar.gz | tar xzv --strip-components=1 -C /usr/share/akaza/

ibus-akaza をインストールしてください。

    sudo rustup install stable
    sudo make install
    ibus restart
    ibus engine akaza

## 設定方法

### config.yml

XDG の設定ファイルディレクトリ以下、通常であれば `$HOME/.config/akaza/config.yml` に設定ファイルを書くことができます。

設定可能な項目は以下のもの。

* ユーザー辞書の設定

サンプルの設定は以下のような感じになります。
akaza が提供しているシステム辞書は偏りがすごくあるので、SKK-JISYO.L を読み込むことをおすすめします。たとえば以下のように設定すると良いでしょう。

    ---
    dicts:
      - path: /usr/share/skk/SKK-JISYO.L
        encoding: euc-jp
        dict_type: skk
      - path: /usr/share/skk/SKK-JISYO.jinmei
        encoding: euc-jp
        dict_type: skk
    single_term:
      - path: /usr/share/akaza/SKK-JISYO.dynamic
        encoding: utf-8
        dict_type: skk

akaza に付属する SKK-JISYO.dynamic を利用すると、「きょう」を変換すると、今日の日付がでるという機能が利用可能です。

ローマ字変換テーブルの変更などもここでできるようにしたいと思っていますが、 _未実装_ です。

↓ かな入力したい場合は以下のように設定してください。

    romkan: kana

## THANKS TO

* [ibus-uniemoji](https://github.com/salty-horse/ibus-uniemoji) を参考に初期の実装を行いました。
* [日本語入力を支える技術](https://gihyo.jp/book/2012/978-4-7741-4993-6) を読み込んで実装しました。この本がなかったら実装しようと思わなかったと思います。

