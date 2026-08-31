# agent-
从零开始使用vibe coding去开发agent


准备搭建的目录结构如下：
multi_agent_collab/
│
├── backend/
│   ├── api/
│   │   └── websocket/              # ← 保留，加一个 __init__.py 占位
│   │       ├── __init__.py
│   │       └── stream.py           # 可选，先不写
│   └── ...（其他不变）
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js           # ← 🔧 新增（Tailwind需要）
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── routes/
│   │   │   ├── Home.tsx
│   │   │   └── Session.tsx
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Loading.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   ├── workflow/
│   │   │   │   ├── GoalInput.tsx
│   │   │   │   ├── ClarifyQuestions.tsx
│   │   │   │   ├── InsightsBoard.tsx
│   │   │   │   ├── ConsensusZone.tsx
│   │   │   │   ├── DivergenceZone.tsx
│   │   │   │   ├── ChoiceSelector.tsx
│   │   │   │   ├── CollisionHistory.tsx
│   │   │   │   └── FinalReview.tsx
│   │   │   └── ui/                # shadcn/ui 组件
│   │   ├── stores/
│   │   │   ├── sessionStore.ts
│   │   │   ├── workflowStore.ts
│   │   │   └── uiStore.ts
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── sessions.ts
│   │   │   └── analysis.ts
│   │   ├── types/
│   │   │   ├── session.ts
│   │   │   ├── insight.ts
│   │   │   ├── report.ts
│   │   │   └── api.ts              # ← 🔧 新增（API 请求/响应类型）
│   │   ├── hooks/
│   │   │   ├── useWorkflow.ts
│   │   │   └── useWebSocket.ts     # 可选，先占位
│   │   ├── utils/
│   │   │   └── formatters.ts
│   │   └── styles/
│   │       └── globals.css
│   └── public/
│       └── favicon.ico
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # ← 🔧 新增（pytest 全局配置）
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_orchestrator.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_workflow.py
│   └── fixtures/
│       └── mock_data.py
│
├── scripts/
│   ├── init_db.py
│   ├── seed_data.py
│   ├── run_dev.sh
│   └── cleanup.sh                  # ← 🔧 新增（清缓存/临时文件）
│
└── data/
    ├── sessions.db
    ├── reports/
    └── uploads/                    # 可选，占位