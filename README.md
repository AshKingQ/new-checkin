# 学生签到系统 (Student Check-in System)

一个基于 Flask 的学生签到管理系统，支持管理员创建签到任务和学生使用动态签到码完成签到。

## 功能特点

- **用户角色管理**
  - 管理员/老师：创建和管理签到任务
  - 学生：注册登录并完成签到

- **签到管理**
  - 动态签到码生成
  - 时间范围控制
  - 签到状态查询
  - 签到记录导出

- **安全性**
  - 密码使用 bcrypt 加密存储
  - SQL 注入防护（参数化查询）
  - Session 管理

## 技术栈

- **前端**: HTML5, CSS3, JavaScript
- **后端**: Python 3.8+, Flask 2.3.3
- **数据库**: SQLite
- **密码加密**: bcrypt

## 项目结构

```
new-checkin/
├── app.py                 # Flask 主应用
├── config.py              # 配置文件
├── database.py            # 数据库操作
├── models.py              # 数据模型
├── requirements.txt       # Python 依赖
├── static/                # 静态文件
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── main.js       # JavaScript 脚本
├── templates/             # HTML 模板
│   ├── base.html         # 基础模板
│   ├── login.html        # 登录页面
│   ├── register.html     # 注册页面
│   ├── student/          # 学生页面
│   │   ├── dashboard.html
│   │   └── checkin.html
│   └── admin/            # 管理员页面
│       ├── dashboard.html
│       ├── create_task.html
│       └── view_records.html
└── README.md             # 项目文档
```

## 安装说明

### 1. 克隆项目

```bash
git clone https://github.com/AshKingQ/new-checkin.git
cd new-checkin
```

### 2. 创建虚拟环境（推荐）

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

首次运行时，系统会自动创建数据库和管理员账号。

## 使用说明

### 启动应用

```bash
python app.py
```

应用将在 `http://127.0.0.1:5000` 启动。

### 默认管理员账号

- **用户名**: `admin`
- **密码**: `admin`

**重要**: 首次登录后请修改默认密码！

### 学生使用流程

1. **注册账号**
   - 访问注册页面
   - 填写学号、姓名和密码
   - 提交注册

2. **登录系统**
   - 使用学号和密码登录

3. **完成签到**
   - 在签到页面输入老师提供的签到码
   - 确认签到（需在规定时间内）

4. **查看签到记录**
   - 在学生主页查看所有签到任务和状态

### 管理员使用流程

1. **登录系统**
   - 使用 admin 账号登录

2. **创建签到任务**
   - 点击"创建签到任务"
   - 填写任务名称、开始时间和结束时间
   - 系统自动生成签到码
   - 将签到码告知学生

3. **查看签到记录**
   - 在管理员面板查看所有签到任务
   - 点击"查看详情"查看具体签到情况
   - 可以导出签到记录为 CSV 文件

## 数据库设计

### 用户表 (users)
- `id`: 主键
- `username`: 学号/用户名（唯一）
- `password`: 加密密码
- `name`: 姓名
- `role`: 角色（admin/student）
- `created_at`: 创建时间

### 签到任务表 (checkin_tasks)
- `id`: 主键
- `title`: 任务标题
- `code`: 签到码（唯一）
- `start_time`: 开始时间
- `end_time`: 结束时间
- `created_by`: 创建人ID
- `created_at`: 创建时间

### 签到记录表 (checkin_records)
- `id`: 主键
- `task_id`: 任务ID（外键）
- `user_id`: 学生ID（外键）
- `checkin_time`: 签到时间

## 配置选项

在 `config.py` 中可以配置：

- `SECRET_KEY`: Flask 密钥（生产环境请修改）
- `DATABASE`: 数据库文件名
- `FLASK_DEBUG`: 调试模式（生产环境设为 False）

## 环境变量

可以通过环境变量覆盖配置：

```bash
# 设置 SECRET_KEY
export SECRET_KEY='your-secret-key'

# 关闭调试模式
export FLASK_DEBUG='False'
```

## 注意事项

1. **安全性**
   - 生产环境请修改默认管理员密码
   - 修改 SECRET_KEY 为随机字符串
   - 关闭调试模式（FLASK_DEBUG=False）

2. **数据备份**
   - 定期备份 `checkin.db` 数据库文件

3. **浏览器兼容性**
   - 推荐使用现代浏览器（Chrome, Firefox, Safari, Edge）

## 常见问题

### 1. 无法启动应用

确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

### 2. 数据库错误

删除现有数据库文件重新初始化：
```bash
rm checkin.db
python app.py
```

### 3. 签到码无效

检查：
- 签到码是否正确
- 当前时间是否在签到时间范围内
- 是否已经签到过

## 开发与贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。