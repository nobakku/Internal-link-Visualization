import sys
import re
import requests
from bs4 import BeautifulSoup
# URLからドメインを取得するため
from urllib.parse import urlparse
# ネットワーク図を作成のため
import networkx as nx
# ネットワーク図を描画するため
import matplotlib.pyplot as plt





def main():
    """
    メインの実行部分:調べたいURLはsearch_urlに入力する
    """
    # 空のセットを用意
    pages = set()
    # 内部リンクを調べたいURL
    search_url = 'https://xxxxxx.com/xxxxxx'
    # https://またはhttp://からはじまる基準のホームページのURL
    match_url = re.match(r'https?://.*?/', search_url)
    # match_urlはマッチオブジェクトだからURLだけを取り出す
    base_url = match_url.group()
    # ドメイン名の取得（ドメイン名: xxxxxx.com）
    base_domain = urlparse(search_url).netloc


    # 内部リンクの取得
    inner_links = get_links(search_url, pages, base_url, base_domain)
    # 内部リンクが存在するなら
    if inner_links:
        print(f'内部リンクは全部で{len(inner_links)}個あります｡')
        print(inner_links) # 内部リンクの表示
        # 関数内で使われるshort_linksを定義 # 内部リンクとして価値の薄いものの除外
        short_links = shape_url(inner_links, base_url, base_domain)
        print(f'価値が高い内部リンクは全部で{len(short_links)}個あります｡')
        print(short_links)
        # ネットワーク図を表示
        show_network(short_links)
    else:
        print('内部リンクが取得できませんでした｡')
        sys.exit() # 内部リンクが存在しない場合はプログラムの終了




# 内部リンクの収集
def get_links(search_url, pages, base_url, base_domain):
    """
    /で始まるものと、base_urlから始まるもの//ドメインから始まるもの
    全ての内部リンクを取得して、重複を除去してpagesに収集する + 内部リンク数を出力
    """
    # ①/で始まって//を含まないURLと、②https://ドメインから始まるもの、③//ドメインから始まるもの
    #+ 該当箇所: ②^https://xxxxxxx.com.*|①^/[^/].*|③^//xxxxxxx.com.*
    pattern = rf'^{base_url}.*|^/[^/].*|^//{base_domain}.*'

    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # URLがパターンに一致するaタグを取得
    for link in soup.find_all('a', href=re.compile(pattern)): # re.compileによる正規表現パターンの生成
        link.get('href')
        # pagesの中にリンクが入っていないことを確認(重複を避けるため)
        if link.get('href') not in pages:
            # なければpagesの中に内部リンクとして追加
            pages.add(link.get('href'))
    return pages




# ネットワーク図の作成
def show_network(pages):
    """
    調査URL(search_url)を中心としたネットワーク図の作成
    """
    # setのpagesをリストにする
    pages = list(pages)
    # indexの0（リストの最初の要素）に文字列"start_url"を追加
    pages.insert(0, 'start_url')
    # 空のグラフの作成 有向グラフ
    G = nx.DiGraph()
    # リストの最初の要素を中心として放射状に頂点と辺の追加
    nx.add_star(G, pages)
    # レイアウトを決める スプリングレイアウト
    pos = nx.spring_layout(G, k=0.3)
    # ノードの様式
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='c', alpha=0.6)
    # ラベル文字の様式
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='DejaVu Sans')
    # エッジの様式
    nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color='c')

    # 座標軸の非表示
    plt.axis('off')
    # 図の描画
    plt.show()




# ネットワーク図の調整
def shape_url(pages, base_url, base_domain):
    """
    URLのhttp://を省略してネットワーク図を見やすくするための調整
    """
    short_links = []
    # 内部リンクのURLから効果の薄い内部リンクをre.sub()で消していく
    for url in pages:
        left_link = re.sub(rf'^{base_url}|^//{base_domain}|.*tag.*|.*feed.*|.*about.*', '', url)
        # short_links（空のリスト）に追加
        short_links.append(left_link)
        # 重複を削除
        s_links = set(short_links)
        # ""を削除
        s_links.discard('')
    return s_links


if __name__ == '__main__':
    main()
