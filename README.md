# Apache_log_profiler

Apacheのログをプロファイリングできます

# Features

任意の期間を指定してApacheのログをプロファイリングできます。  
for_big_memory.pyの方が早いですがメモリを使うので、メモリがあんまりないよ！っていう人はfor_mini_memory.pyを使いましょう  
気分でコーディングしたので若干できることが異なりますが、おおよそfor_mini_memory.pyの方が上位互換です
```
通常syslogみたいな物はログローテートされて予め決められたサイズで固められていると思ったので、1ファイルがメモリ容量を超えるような場合はサポートしていません。
大人しく分割しましょう。
```

# Environment

* Python 3.8.0

# Installation

```bash
pip install -r requirements.txt
```

# Usage

```bash
git clone https://github.com/1234567890Joe/Apache_log_profiler.git
python for_mini_memory.py -f hoge -d huga --start 0000/00/00 --end 9999/99/99
```
### optionについて
- -f 入力するファイルを指定してください
- -d 入力するファイルのみが入ったディレクトリを指定してください
    - 余分な画像とかが入っていると読み込み時にエラーを吐きます
    - 一旦別のディレクトリに動かすか、 `for_mini_memory.py` の119行目の `for file_path in tqdm(glob.glob(dir_path + "*"), desc='file loading...'):` の `+ "*"` 部分を変更しましょう
-  --start 計測したい区間の始まりを入れてください
-  --end 計測したい区間の終わりを入力してください  
    -  最終日は含まれません、2020年の5月のデータを参照したい場合はendには2020/06/01と入れましょう

# Note

1時間ごとのアクセス件数がresult_time.csvに、リモートホスト別のアクセス件数がresult_host.csvに出力されます。result_time.csvは時系列順で、result_host.csvは辞書順にsortされています。また、リモートホスト別のアクセス件数はアクセスが多い順に標準出力に表示されます。おまけで1時間ごとのアクセス件数ランキングの上位10件はtop10_time.pngに出力されます  
また、数PBみたいな大きいログはこんなコード使わずに素直にBigQueryに投げましょう
