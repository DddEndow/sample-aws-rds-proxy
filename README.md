# sample-aws-rds-proxy

# デプロイ方法
### デプロイ先リージョンのEC2のAMIを取得し、Mappingsに追加する。
```
$ aws ssm get-parameter \ 
  --name /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 \
  --region eu-west-1
```

### SAMのセットアップ
1. `sam build`を実行。
2. `sam deploy --guided`を実行し`samconfig.toml`を作成する。
3. `samconfig.toml`内の設定でパラメータを上書きする。
※ EC2のキーはあらかじめ作成する。

```
上書き必須のパラメータ
parameter_overrides = [
    "RDSRootUserPwd=rootpass",
    "RDSLambdaUserPwd=lambdapass",
    "EC2KeyName=sample-aws-rds-proxy-ec2-key",
    "EC2CidrIp=0.0.0.0/0" # EC2の踏み台サーバーへのアクセスを許可するIP
]
```

4. `sam deploy`でデプロイを実行

# 環境のセットアップ
### 踏み台サーバーにアクセス

```
$ ssh -i ".ssh/sample-aws-rds-proxy-ec2-key.pem" {EC2のエンドポイント}
```

### RDSにアクセス

```
$ mysql -h {RDSのエンドポイント} -P 3306 -u root -p
```

### MySQLのセットアップ
1. ルートユーザーでログインし、データベースとテーブルを作成する。
```sql
CREATE DATABASE sample_rds_proxy;
CREATE TABLE sample_rds_proxy.users (
    id INT NOT NULL,
    name VARCHAR(30),
    PRIMARY KEY (id)
);
```

2. 適当なデータを挿入。
```sql
USE sample_rds_proxy;
INSERT INTO users (id, name)
VALUES
    (1, 'Hoge User'),
    (2, 'Fuga User'),
    (3, 'Piyo User');
```

3. 現在のユーザーを確認し、lambdaユーザーが存在しないことを確認。
```sql
select user, host from mysql.user;

+---------------+-----------+
| user          | host      |
+---------------+-----------+
| rdsproxyadmin | %         |
| root          | %         |
| mysql.sys     | localhost |
| rdsadmin      | localhost |
+---------------+-----------+
```

4. lambdaユーザーを登録する。
```sql
grant all on sample_rds_proxy.* to lambda@'%' identified by 'lambdapass';
```

# RDS Proxyでのアクセス
1. 踏み台サーバーにアクセス。
2. RDS Proxy経由でアクセス。
```
# rootとlambdaのどちらでもログイン可能
mysql -h {RDS Proxyのエンドポイント} -P 3306 -u root -p
```
