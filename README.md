# Q3 Chatbot Platform

[English](#english) | [中文](#chinese)

<a name="english"></a>
# Intelligent Chatbot Platform (English)

A production-ready chatbot platform built with Python, featuring intent recognition, session management, and extensible architecture for future AI/LLM integration.

## 🎯 Core Features

### Intent & Dialog Management
- **Smart Intent Recognition**: Pattern-based and ML-ready intent classification
- **Context-Aware Responses**: Maintains conversation context and history
- **Session Management**: Redis-backed session handling with configurable TTL
- **Slot Filling**: Entity extraction and parameter tracking
- **Emotion Analysis**: Real-time sentiment detection
- **Urgency Detection**: Multi-level urgency classification

### API & Integration
- **RESTful API**: FastAPI-powered endpoints with automatic OpenAPI docs
- **Health Monitoring**: Comprehensive health checks and system status
- **Database Integration**: SQLAlchemy ORM with migration support
- **Real-time Analytics**: Interactive dashboard with KPIs
- **Message Insights**: Volume heatmap and trend analysis
- **Performance Metrics**: Response time and throughput tracking

### Architecture & Design
- **Modular Design**: Clear separation of concerns for easy extension
- **Scalable Architecture**: Ready for horizontal scaling
- **Error Handling**: Comprehensive error management
- **Testing & Quality**: Extensive test coverage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- (Optional) MySQL 5.7+ for persistent storage

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd q3Demo
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Verify installation:**
   - Health check: `GET http://localhost:8000/health`
   - API docs: `http://localhost:8000/docs`
   - Chat endpoint: `POST http://localhost:8000/api/v1/chat`

## 📁 System Architecture

### Component Overview
```
app/
├── api/          # REST API endpoints
│   ├── chat.py   # Main chat interface
│   ├── health.py # System health
│   └── models.py # API schemas
├── database/     # Data persistence
│   ├── models.py # DB schemas
│   └── crud.py   # DB operations
├── nlp/          # NLP processing
│   ├── intent_classifier.py
│   └── semantic_search.py
├── policy/       # Response generation
├── state/        # Session management
└── config.py     # System configuration
```

### Key Components
1. **API Layer** (`app/api/`)
   - Request/response handling
   - Input validation
   - Rate limiting
   - Error handling

2. **NLP Engine** (`app/nlp/`)
   - Intent classification
   - Entity extraction
   - Semantic understanding
   - Extensible for ML models

3. **State Management** (`app/state/`)
   - Session tracking
   - Context management
   - User state persistence
   - Conversation history

4. **Database Layer** (`app/database/`)
   - Data models
   - CRUD operations
   - Migration support
   - Analytics storage

## 🔧 Configuration

### Environment Variables
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
SESSION_TTL_MINUTES=30
MAX_SESSION_TURNS=10
DB_URL=mysql+pymysql://user:pass@localhost:3306/dbname
```

### Intent Configuration
Edit `app/data/intents.json` to customize:
- Intent patterns
- Response templates
- Confidence thresholds
- Slot definitions

## 📊 API Documentation

### Main Endpoints

#### Chat API
```http
POST /api/v1/chat
Content-Type: application/json

{
  "user_text": "string",
  "session_id": "string (optional)"
}
```

#### Session Management
```http
GET /api/v1/session/{session_id}/stats
DELETE /api/v1/session/{session_id}
```

#### System Status
```http
GET /health
GET /metrics
```

## 🔮 Future Roadmap

### Phase 1: Enhanced NLP ✅
- [x] Rule-based emotion analysis
- [x] Urgency level detection
- [x] Pattern-based intent classification
- [ ] ML-based intent classification (planned)
- [ ] Multi-language support (planned)

### Phase 2: Analytics & Monitoring ✅
- [x] Real-time analytics dashboard
- [x] Message volume heatmap
- [x] Sentiment trends tracking
- [x] Performance monitoring
- [ ] Advanced analytics features (planned)

### Phase 3: AI Integration (Upcoming)
- [ ] LLM integration
- [ ] RAG capabilities
- [ ] Knowledge base expansion

## 📄 License

MIT License - see LICENSE file for details

---

<a name="chinese"></a>
# 智能聊天机器人平台 (中文)

一个基于 Python 构建的生产级聊天机器人平台，具备意图识别、会话管理和可扩展架构，支持未来 AI/LLM 集成。

## 🎯 核心功能

### 意图和对话管理
- **智能意图识别**：基于模式匹配和机器学习就绪的意图分类
- **上下文感知响应**：维护对话上下文和历史
- **会话管理**：基于 Redis 的会话处理，支持可配置 TTL
- **槽位填充**：实体提取和参数跟踪
- **情感分析**：实时情感检测
- **紧急程度识别**：多级紧急程度分类

### API 和集成
- **RESTful API**：基于 FastAPI 的端点，自动生成 OpenAPI 文档
- **健康监控**：全面的健康检查和系统状态
- **数据库集成**：支持迁移的 SQLAlchemy ORM
- **实时分析**：交互式仪表板和 KPI 展示
- **消息洞察**：消息量热力图和趋势分析
- **性能指标**：响应时间和吞吐量跟踪

### 架构和设计
- **模块化设计**：关注点分离，便于扩展
- **可扩展架构**：支持水平扩展
- **错误处理**：全面的错误管理
- **测试和质量**：广泛的测试覆盖

## 🚀 快速开始

### 前置要求
- Python 3.8+
- pip 包管理器
- (可选) MySQL 5.7+ 用于持久化存储

### 安装步骤

1. **克隆和设置：**
   ```bash
   git clone <仓库地址>
   cd q3Demo
   pip install -r requirements.txt
   ```

2. **配置环境：**
   ```bash
   cp env.example .env
   # 编辑 .env 设置你的配置
   ```

3. **运行应用：**
   ```bash
   python main.py
   ```

4. **验证安装：**
   - 健康检查：`GET http://localhost:8000/health`
   - API 文档：`http://localhost:8000/docs`
   - 聊天端点：`POST http://localhost:8000/api/v1/chat`

## 📁 系统架构

### 组件概览
```
app/
├── api/          # REST API 端点
│   ├── chat.py   # 主聊天接口
│   ├── health.py # 系统健康
│   └── models.py # API 模式
├── database/     # 数据持久化
│   ├── models.py # 数据库模式
│   └── crud.py   # 数据库操作
├── nlp/          # NLP 处理
│   ├── intent_classifier.py
│   └── semantic_search.py
├── policy/       # 响应生成
├── state/        # 会话管理
└── config.py     # 系统配置
```

### 核心组件
1. **API 层** (`app/api/`)
   - 请求/响应处理
   - 输入验证
   - 速率限制
   - 错误处理

2. **NLP 引擎** (`app/nlp/`)
   - 意图分类
   - 实体提取
   - 语义理解
   - 可扩展的 ML 模型

3. **状态管理** (`app/state/`)
   - 会话跟踪
   - 上下文管理
   - 用户状态持久化
   - 对话历史

4. **数据库层** (`app/database/`)
   - 数据模型
   - CRUD 操作
   - 迁移支持
   - 分析存储

## 🔧 配置说明

### 环境变量
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
SESSION_TTL_MINUTES=30
MAX_SESSION_TURNS=10
DB_URL=mysql+pymysql://user:pass@localhost:3306/dbname
```

### 意图配置
编辑 `app/data/intents.json` 自定义：
- 意图模式
- 响应模板
- 置信度阈值
- 槽位定义

## 📊 API 文档

### 主要端点

#### 聊天 API
```http
POST /api/v1/chat
Content-Type: application/json

{
  "user_text": "string",
  "session_id": "string (可选)"
}
```

#### 会话管理
```http
GET /api/v1/session/{session_id}/stats
DELETE /api/v1/session/{session_id}
```

#### 系统状态
```http
GET /health
GET /metrics
```

## 🔮 未来路线图

### 第一阶段：增强 NLP
- [ ] 基于机器学习的意图分类
- [ ] 高级实体识别
- [ ] 多语言支持

### 第二阶段：AI 集成
- [ ] LLM 集成
- [ ] RAG 能力
- [ ] 知识库扩展

### 第三阶段：分析和监控
- [ ] 高级分析仪表板
- [ ] 实时监控
- [ ] 性能优化

## 📄 许可证

MIT 许可证 - 详见 LICENSE 文件

---

**Version:** 0.1.0  
**Last Updated:** 2024

For questions or support, please refer to the project documentation or create an issue.

如有问题或需要支持，请参考项目文档或创建 issue。
