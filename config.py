import os
from dotenv import load_dotenv

load_dotenv()

# TokenTerminal API Configuration
BEARER_TOKEN = "c0e5035a-64f6-4d2c-b5f6-ac1d1cb3da2f"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcm9udEVuZCI6InRlcm1pbmFsIGRhc2hib2FyZCIsImlhdCI6MTc1MDU1MjY4MSwiZXhwIjoxNzUxNzYyMjgxfQ.En08kB85vgE7yG2mA-Xo_1mrlABTlusl_ehsfMDDc34"

# API Endpoints
FINANCIAL_STATEMENT_API = "https://api.tokenterminal.com/trpc/projects.getFinancialStatement"
TIMESERIES_API = "https://api.tokenterminal.com/trpc/metrics.postTimeseries"
BREAKDOWN_API = "https://api.tokenterminal.com/trpc/metrics.postBreakdown"

# OpenAI API Key (optional - for AI summaries)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Database
DB_PATH = "raydium_data.db"

# Cache duration (in hours)
CACHE_DURATION = 1