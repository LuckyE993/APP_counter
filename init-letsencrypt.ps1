# PowerShell 版本�?SSL 证书初始化脚�?

# 替换为你的域名和邮箱
$domains = @("beancount.qixuantech.xyz")
$email = "luckyeureka52@gmail.com"
$staging = 0  # 设置�?1 使用测试环境

$data_path = "./certbot"
$rsa_key_size = 4096

# 创建必要的目�?
New-Item -ItemType Directory -Force -Path "$data_path/conf" | Out-Null
New-Item -ItemType Directory -Force -Path "$data_path/www" | Out-Null

# 下载推荐�?TLS 参数
if (!(Test-Path "$data_path/conf/options-ssl-nginx.conf") -or !(Test-Path "$data_path/conf/ssl-dhparams.pem")) {
    Write-Host "### Downloading recommended TLS parameters ..."
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf" -OutFile "$data_path/conf/options-ssl-nginx.conf"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem" -OutFile "$data_path/conf/ssl-dhparams.pem"
    Write-Host ""
}

# 创建临时自签名证�?
Write-Host "### Creating dummy certificate for $($domains[0]) ..."
$path = "/etc/letsencrypt/live/$($domains[0])"
New-Item -ItemType Directory -Force -Path "$data_path/conf/live/$($domains[0])" | Out-Null
docker compose run --rm --entrypoint "openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 -keyout '$path/privkey.pem' -out '$path/fullchain.pem' -subj '/CN=localhost'" certbot
Write-Host ""

# 启动 nginx
Write-Host "### Starting nginx ..."
docker compose up --force-recreate -d nginx
Write-Host ""

# 删除临时证书
Write-Host "### Deleting dummy certificate for $($domains[0]) ..."
docker compose run --rm --entrypoint "rm -Rf /etc/letsencrypt/live/$($domains[0]) && rm -Rf /etc/letsencrypt/archive/$($domains[0]) && rm -Rf /etc/letsencrypt/renewal/$($domains[0]).conf" certbot
Write-Host ""

# 请求真实证书
Write-Host "### Requesting Let's Encrypt certificate for $($domains[0]) ..."
$domain_args = ($domains | ForEach-Object { "-d $_" }) -join " "
$staging_arg = if ($staging -eq 1) { "--staging" } else { "" }

docker compose run --rm --entrypoint "certbot certonly --webroot -w /var/www/certbot $staging_arg $domain_args --email $email --rsa-key-size $rsa_key_size --agree-tos --force-renewal" certbot
Write-Host ""

# 重新加载 nginx
Write-Host "### Reloading nginx ..."
docker compose exec nginx nginx -s reload
