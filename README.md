# WETHAP

実験室の温度・湿度・気圧を教えてくれるツステム

- POSTメソッドでAPIにJSON形式でリクエストすると、そのkeyとvalueがローカルのデータベースに追加される。
- GETメソッドでリクエストすると、データベースの全データがおなじみのAPIの形式で返ってくる。

POSTはPythonファイルから`requests.post()`でリクエストする。GETはいつも通りブラウザからでOK。
