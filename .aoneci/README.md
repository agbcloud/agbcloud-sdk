# AGB SDK CI/CD 配置说明

## 文件结构

```
.aoneci/
├── pipeline.yml        # 主要的CI/CD流水线配置
└── README.md          # 本说明文档

# 项目根目录下的相关配置文件
.bandit                   # Bandit安全扫描配置
```

## CI/CD 流水线概览

### 触发条件
- **合并请求 (MR)**: 针对所有分支的开启和更新
- **推送 (Push)**: 针对 `master` 分支和所有 `release_v*` 分支

### 流水线任务

#### 1. 环境准备 (setup)
- 代码统计分析
- Python环境设置 (默认Python 3.10)

#### 2. 代码质量扫描 (code-quality-scan)
- **代码格式检查**: Black, isort
- **代码质量检查**: Flake8
- **类型检查**: MyPy

#### 3. 安全扫描 (security-scan)
- **Bandit**: Python安全漏洞静态分析
- **pip-audit**: 依赖包漏洞扫描
- **Safety**: 已知安全漏洞检查

#### 4. 构建测试 (build-test)
- Python包构建
- 包完整性检查

#### 5. 单元测试 (unit-tests) - **暂时注释**
- 待添加测试用例后启用
- 包含测试覆盖率报告

## 配置参数

### 主要参数
- `python_enabled`: 启用Python代码扫描 (默认: true)
- `python_version`: Python版本 (默认: "3.10")
- `security_scan_enabled`: 启用安全扫描 (默认: true)
- `unit_test_enabled`: 启用单元测试 (默认: false)

### 资源配置
- `runs_on_resources`: 运行时容器资源规格 (默认: "4-16Gi")

## 通知配置

### 钉钉通知
- **触发条件**: 流水线失败时
- **通知用户**: 指定用户ID列表
- **群组通知**: 指定钉钉群组ID

## 环境要求

### 必需工具
- Python 3.10+
- pip
- Git

### 开发依赖
```bash
pip install -e .[dev,test]
```

### 安全扫描工具
- bandit[toml]
- pip-audit
- safety

### 构建工具
- build
- twine


## 安全扫描配置

### Bandit
- 配置文件: `.bandit`
- 扫描目录: `agb/`
- 报告格式: JSON
- 置信度: MEDIUM

### pip-audit
- 扫描已安装的依赖包
- 输出格式: JSON, CycloneDX

### Safety
- 检查已知安全漏洞
- 基于安全数据库

## 启用单元测试

当添加测试用例后，需要：

1. **取消注释** `pipeline.yml` 中的 `unit-tests` 任务
2. 设置 `unit_test_enabled: true`

## 报告和产物

### 保留时间
- **代码质量报告**: 7天
- **安全扫描报告**: 30天
- **构建产物**: 7天

### 产物路径
- Bandit报告: `bandit-report.json`, `bandit-report.txt`
- pip-audit报告: `pip-audit-report.json`
- Safety报告: `safety-report.json`, `safety-report.txt`
- 构建产物: `dist/**/*`

## 故障排除

### 常见问题
1. **依赖安装失败**: 检查 `pyproject.toml` 中的依赖配置
2. **代码格式检查失败**: 运行 `black .` 和 `isort .` 修复
3. **类型检查失败**: 检查MyPy配置和类型注解
4. **安全扫描误报**: 在 `.bandit` 配置中添加跳过规则

### 调试建议
- 检查具体任务的日志输出
- 下载相关的报告文件进行分析
- 确保本地环境与CI环境一致

## 维护

### 定期更新
- Python版本
- 依赖包版本
- 安全扫描工具版本

### 监控指标
- 代码质量得分
- 安全漏洞数量
- 构建成功率
- 测试覆盖率（待启用）