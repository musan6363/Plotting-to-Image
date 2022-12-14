# アノテーション結果の確認
- 3名が行った画像上へクリックするアノテーションの結果を確認  

<img src='doc/preview_sample.png' width=600px>

## 機能
- 歩行者のBBoxを描画
- 3名分のクリックを画像上に赤マーカーでプロット
- eyecontactフラグ，difficultフラグが付与されている場合には，マーカーの色を変える(eyecontact:ピンク，difficult:紫)
- 3名の評価がバラけている順に表示
  1. 3名のアノテーション座標から三角形を考え，その重心を求める
  2. 重心から各点への距離の分散を求める
  3. 距離分散の大きい順に画像を表示
- Next, Prevボタンを押すことで各レコードを順に表示（双方向リストによる実装）
- レコードの収録順，もしくは歩行者tokenをテキストボックスに入力することで，任意のレコードを表示可能
- プレビューツール上で生成した画像を保存するボタン
- 表示中画像のアノテーション情報を別のjsonファイルに書き出すボタン
  - 良い例(Good)と悪い例(Bad)を想定し，2つのボタンを用意

## 使い方
`python preview.py <アノテーション情報を含むjsonファイル> <歩行者画像の参照先> <JSONと画像の書き出し先>`

### 例
`python preview.py ann_records/nuimages_ped_1017_v1.0-train.json img_ped/nuimages_ped/v1.0-train/img output/nuimages_ped/v1.0-train`