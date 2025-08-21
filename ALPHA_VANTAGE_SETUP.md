# 🚀 Alpha Vantage 快速设置指南

## 步骤 1: 获取 Alpha Vantage API 密钥

1. 访问 [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. 点击 "GET YOUR FREE API KEY TODAY" 
3. 填写简单的注册表单
4. 获得免费的 API 密钥（500次请求/天）

## 步骤 2: 配置 API 密钥

在项目根目录下的 `.env` 文件中，替换：

```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

为：

```env
ALPHA_VANTAGE_API_KEY=你的实际API密钥
```

## 步骤 3: 测试集成

运行测试脚本验证配置：

```bash
python test_alpha_vantage.py
```

## 步骤 4: 运行项目

```bash
python examples/interactive_demo.py
```

## 🆓 免费额度说明

**Alpha Vantage 免费版本：**
- 500 次请求/天
- 5 次请求/分钟
- 支持所有主要股票市场
- 包含实时报价、历史数据、技术指标

**足够用于：**
- 个人学习和研究
- 小型项目开发
- 日常股票分析

## 🔄 相比 Yahoo Finance 的优势

| 特性 | Alpha Vantage | Yahoo Finance |
|------|---------------|---------------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 速率限制 | 明确定义 | 隐藏限制 |
| 数据质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 技术支持 | 官方支持 | 社区支持 |
| 免费额度 | 500/天 | 无保证 |

## 🛠️ 故障排除

**如果遇到网络问题：**
- 项目已配置代理绕过
- 确保网络连接正常
- 检查防火墙设置

**如果 API 密钥无效：**
- 确认密钥复制正确
- 检查 .env 文件格式
- 确认 Alpha Vantage 账户已激活

**如果超出速率限制：**
- 免费版：5次/分钟，500次/天
- 程序会自动等待和重试
- 考虑升级到付费版本
