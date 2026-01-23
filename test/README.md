# 测试说明

## 单元测试（Mock）

使用 Mock 技术测试，无需真实数据库：

```bash
python3 -m unittest test/mysql.py
```

## 集成测试（真实 MySQL）

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MYSQL_HOST | MySQL 服务器地址 | localhost |
| MYSQL_PORT | MySQL 服务器端口 | 3306 |
| MYSQL_USER | MySQL 用户名 | root |
| MYSQL_PASSWORD | MySQL 密码 | (空) |
| MYSQL_DATABASE | 测试数据库名 | test_pyanalysis |

### 使用 Docker 启动 MySQL 8.4

**1. 启动容器**

```bash
docker run -d \
  --name mysql-test-84 \
  -e MYSQL_ROOT_PASSWORD=testpass \
  -e MYSQL_DATABASE=test_pyanalysis \
  -p 3306:3306 \
  mysql:8.4
```

**2. 等待 MySQL 启动完成（约 30 秒）**

```bash
# 查看启动日志
docker logs -f mysql-test-84

# 看到 "ready for connections" 后按 Ctrl+C 退出
```

**3. 运行集成测试**

```bash
MYSQL_HOST=127.0.0.1 \
MYSQL_USER=root \
MYSQL_PASSWORD=testpass \
MYSQL_DATABASE=test_pyanalysis \
python3 -m unittest test/mysql_integration.py
```

**4. 测试完成后清理**

```bash
docker stop mysql-test-84 && docker rm mysql-test-84
```

### 使用 Docker 启动 MySQL 5.7

**1. 启动容器**

```bash
docker run -d \
  --name mysql-test-57 \
  -e MYSQL_ROOT_PASSWORD=testpass \
  -e MYSQL_DATABASE=test_pyanalysis \
  -p 3307:3306 \
  mysql:5.7
```

**2. 等待 MySQL 启动完成（约 30 秒）**

```bash
# 查看启动日志
docker logs -f mysql-test-57

# 看到 "ready for connections" 后按 Ctrl+C 退出
```

**3. 运行集成测试**

```bash
MYSQL_HOST=127.0.0.1 \
MYSQL_PORT=3307 \
MYSQL_USER=root \
MYSQL_PASSWORD=testpass \
MYSQL_DATABASE=test_pyanalysis \
python3 -m unittest test/mysql_integration.py
```

**4. 测试完成后清理**

```bash
docker stop mysql-test-57 && docker rm mysql-test-57
```

### 一行命令（启动 + 测试）

**MySQL 8.4:**

```bash
docker run -d --name mysql-test-84 -e MYSQL_ROOT_PASSWORD=testpass -e MYSQL_DATABASE=test_pyanalysis -p 3306:3306 mysql:8.4 && \
sleep 30 && \
MYSQL_HOST=127.0.0.1 MYSQL_USER=root MYSQL_PASSWORD=testpass python3 -m unittest test/mysql_integration.py
```

**MySQL 5.7:**

```bash
docker run -d --name mysql-test-57 -e MYSQL_ROOT_PASSWORD=testpass -e MYSQL_DATABASE=test_pyanalysis -p 3307:3306 mysql:5.7 && \
sleep 30 && \
MYSQL_HOST=127.0.0.1 MYSQL_PORT=3307 MYSQL_USER=root MYSQL_PASSWORD=testpass python3 -m unittest test/mysql_integration.py
```

### 连接已有 MySQL 服务器

如果已有 MySQL 服务器，直接设置环境变量运行：

```bash
MYSQL_HOST=your-mysql-host \
MYSQL_PORT=3306 \
MYSQL_USER=your-user \
MYSQL_PASSWORD=your-password \
MYSQL_DATABASE=test_pyanalysis \
python3 -m unittest test/mysql_integration.py
```

## 其他模块测试

```bash
python3 -m unittest test/logger.py
python3 -m unittest test/moment.py
python3 -m unittest test/mail.py
```
