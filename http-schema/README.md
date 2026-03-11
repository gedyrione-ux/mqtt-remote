# EMQX HTTP编解码服务

用于EMQX规则引擎的自定义编解码HTTP服务，负责将设备地址码注入到指令模板中。

## 功能说明

- 接收Base64编码的二进制指令模板
- 从配置参数中获取设备地址码
- 将地址码写入模板的第二个字节位置
- 返回修改后的Base64编码字符串

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

### 方式1：使用启动脚本（Linux/Mac）

```bash
chmod +x start.sh
./start.sh
```

### 方式2：直接运行Python

```bash
python app.py
```

### 自定义端口

通过环境变量`PORT`指定端口：

```bash
PORT=8080 ./start.sh
# 或者
PORT=8080 python app.py
```

## 接口说明

### POST /serde

#### 请求头

```
Content-Type: application/json
```

#### 请求体

```json
{
  "payload": "RAJAAA0=",
  "opts": "{\"device_code\":2}"
}
```

- `payload`: Base64编码的二进制指令模板
- `opts`: JSON格式字符串，包含`device_code`字段（设备地址码，0-255）

#### 响应

成功时返回修改后的Base64字符串（纯文本），状态码200。

## 测试示例

使用curl测试服务：

```bash
curl -X POST http://localhost:9500/serde \
  -H "Content-Type: application/json" \
  -d '{
    "payload": "RAJAAA0=",
    "opts": "{\"device_code\":2}"
  }'
```

## 与EMQX规则引擎配合

在EMQX规则中配置HTTP Schema指向本服务，规则SQL示例：

```sql
FOREACH
    payload.targets as target
DO
    target.id as device_id,
    schema_encode('my_http_schema',
                  base64_decode(payload.cmd_template),
                  json_encode(#{device_code => target.code})) as cmd_payload
FROM
    "command"
```

## 注意事项

1. 确保防火墙已放行9500端口（或自定义端口）
2. 服务无状态，可部署多个实例做负载均衡
3. 仅用于内部网络，无需认证机制
4. 确保设备地址码在0-255范围内
