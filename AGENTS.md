# Okyou2 Agent Notes

この repo は、完了済み `Okyou` の clone ではなく、先行成果を参照して作る新規の後継プロジェクトである。先行 `Okyou` はリリース済みで閉じているため、絶対に変更しない。

## 作業姿勢

- まず `README.md`、`docs/okyou1-reading-notes.md`、`docs/development-brief.md` を読む。
- 先行 repo `../Okyou` は参照元として読むだけにし、編集・整形・commit・branch 作成・remote 操作をしない。
- 先行 repo に対して実行してよいのは、`git status`、`git log`、`rg`、`sed`、`ls` などの読み取り確認だけである。
- `Okyou` の Git 履歴、remote、公開済み Pages 成果物を `Okyou2` の継続物として扱わない。
- 研究上の問い、対象文献、解釈、公開判断は人間の研究判断を前提にし、AI は実装・可視化・検証・文書化を補助する。

## 持ち込まないもの

- `.env`、API key、token、秘密情報。
- SAT、J-SOKEN、84000 などから取得した raw/processed 本文。
- embedding cache、outputs、ローカル preview 用生成物。
- 先行 repo の旧ローカル探索フォルダ `お経/`、`埋め込みお経/`、`埋め込みテスト/`。

## 発展作業の優先順

1. 問いを明確にする。
2. 対象文献と利用条件を manifest に書く。
3. 本文取得・前処理・派生データの公開境界を決める。
4. まず API 不要の baseline を作る。
5. 必要な段階で embedding を生成する。
6. 結果、未検証点、検証コマンドを `memory.md` と `docs/` に残す。

## 検証

Python を追加したら、最低限 `python3 -m py_compile` を通す。ビューアやHTMLを作ったら、ローカルまたは in-app browser で表示確認する。公開や push は、ユーザーが明示したときだけ行う。
