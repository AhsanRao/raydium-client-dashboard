from openai import OpenAI
from typing import Dict, Any, Optional

class AISummaryGenerator:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_summary(self, metrics_data: Dict[str, Any]) -> str:
        """Generate AI summary of the metrics data"""
        if not self.api_key:
            return self._generate_simple_summary(metrics_data)

        try:
            # Prepare data summary for AI
            data_summary = self._prepare_data_for_ai(metrics_data)

            response = self.client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a DeFi analyst. Analyze the provided Raydium DEX metrics and provide insights on performance, trends, and key observations. Be concise but informative."
                },
                {
                    "role": "user",
                    "content": f"Analyze these Raydium metrics and provide key insights:\n\n{data_summary}"
                }
            ],
            max_tokens=500,
            temperature=0.7)

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"AI Summary Error: {e}")
            return self._generate_simple_summary(metrics_data)

    def _prepare_data_for_ai(self, metrics_data: Dict[str, Any]) -> str:
        """Prepare metrics data for AI analysis"""
        summary_lines = []

        key_metrics = [
            'fees', 'revenue', 'trading_volume', 'user_dau', 'user_mau', 
            'tvl', 'active_developers', 'price', 'market_cap_circulating'
        ]

        for metric in key_metrics:
            if metric in metrics_data:
                data = metrics_data[metric]
                latest = data.get('latest', 0)
                change = data.get('change', 0) * 100

                summary_lines.append(f"{metric.replace('_', ' ').title()}: {latest:,.0f} ({change:+.1f}%)")

        return "\n".join(summary_lines)

    def _generate_simple_summary(self, metrics_data: Dict[str, Any]) -> str:
        """Generate simple rule-based summary"""
        summary_parts = []

        # Revenue analysis
        if 'revenue' in metrics_data:
            revenue_change = metrics_data['revenue'].get('change', 0) * 100
            if revenue_change > 50:
                summary_parts.append("🚀 Exceptional revenue growth indicates strong business momentum.")
            elif revenue_change > 10:
                summary_parts.append("📈 Solid revenue growth shows healthy business expansion.")
            elif revenue_change < -20:
                summary_parts.append("⚠️ Revenue decline suggests challenges in monetization.")

        # User growth analysis
        if 'user_mau' in metrics_data:
            user_change = metrics_data['user_mau'].get('change', 0) * 100
            if user_change > 100:
                summary_parts.append("🔥 Explosive user growth demonstrates strong product-market fit.")
            elif user_change > 20:
                summary_parts.append("✅ Strong user acquisition indicates growing adoption.")

        # TVL analysis
        if 'tvl' in metrics_data:
            tvl_change = metrics_data['tvl'].get('change', 0) * 100
            if tvl_change > 20:
                summary_parts.append("💰 Rising TVL shows increased confidence and capital inflow.")
            elif tvl_change < -20:
                summary_parts.append("📉 Declining TVL may indicate capital outflow or competitive pressure.")

        # Development activity
        if 'active_developers' in metrics_data:
            dev_change = metrics_data['active_developers'].get('change', 0) * 100
            if dev_change > 20:
                summary_parts.append("👨‍💻 Increasing developer activity suggests active protocol development.")

        if not summary_parts:
            summary_parts.append("📊 Raydium continues to operate as a leading DEX on Solana with consistent metrics.")

        return " ".join(summary_parts)