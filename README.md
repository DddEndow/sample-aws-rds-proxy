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
