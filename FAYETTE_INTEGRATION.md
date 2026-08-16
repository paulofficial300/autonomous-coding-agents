# Fayette Market Intelligence - Agent Integration Guide

## Overview
This document describes how to run the autonomous market research agent for Fayette Market Intelligence business operations.

## Features Implemented

### Service Tiers
The agent supports all three core service offerings:

1. **Tier 1: Competitor Gap Snapshot** ($150, 24hr)
   - Audits 10 local contractors in target industry
   - Analyzes: response times, online booking, review sentiment, service gaps
   - Output: Markdown table report

2. **Tier 2: B2B Prospect Database** ($250, 48hr)
   - Generates list of 50+ commercial prospects
   - Captures: name, decision-maker, email, phone, business type
   - Output: CSV format suitable for CRM import

3. **Tier 3: Monthly Intelligence Retainer** ($200/mo)
   - Bi-weekly competitive monitoring
   - Tracks: pricing updates, new entrants, sentiment trends, SEO shifts
   - Output: Executive summary with trend metrics

### Security & Guardrails

✅ **Human-in-the-Loop Approval** - Sensitive operations require manual validation  
✅ **Safe Dispatcher Pattern** - Explicit function mapping, no eval/exec of untrusted input  
✅ **Rate Limit Handling** - Exponential backoff (1s → 60s max) on 429 errors  
✅ **Public Data Only** - Respects robots.txt and terms of service  
✅ **Email Validation** - Regex validation before prospect data inclusion  

---

## Installation & Setup

### 1. Prerequisites
```bash
pip install openai
```

### 2. API Configuration
Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

Set environment variable:
```bash
# Mac/Linux
export OPENAI_API_KEY="your_gemini_api_key"

# Windows PowerShell
$env:OPENAI_API_KEY="your_gemini_api_key"

# Or create .env file
echo 'OPENAI_API_KEY=your_gemini_api_key' > .env
```

---

## Usage

### Demo Mode (Pre-configured)
```bash
python fayette_market_agent.py
```
Runs a sample Tier 1 audit for HVAC contractors in Tyrone, GA.

### Interactive Order Intake Mode
```bash
python fayette_market_agent.py interactive
```
Prompts for:
- Service tier selection (1-3)
- Industry vertical
- Geographic location
- Client name (optional)

Example session:
```
Select Service Tier:
  1) Competitor Gap Snapshot ($150) - 24hr turnaround
  2) B2B Prospect Database ($250) - 48hr turnaround
  3) Monthly Intelligence Retainer ($200/mo) - Bi-weekly updates

Enter choice (1-3): 1
Industry (HVAC/Plumbing/Roofing/Electrical/etc): HVAC
Geographic Area (e.g., Tyrone, GA or Fayette County): Peachtree City, GA
Client Name (optional): Thompson HVAC Solutions

Order received. Starting agent...
```

### Programmatic Usage
```python
from fayette_market_agent import run_market_research_agent

run_market_research_agent(
    service_tier="tier1",
    industry="Plumbing",
    location="Fayetteville, GA",
    client_name="Fayette Plumbing Co"
)
```

---

## Agent Execution Flow

```
User Task → ReAct Reasoning Loop → Tool Dispatch → Output Formatting → Report Delivery
```

1. **User Input**: Service tier, industry, location
2. **Agent Reasoning**: Analyzes goal, identifies required data sources
3. **Tool Selection**: web_search, write_file, human_approval
4. **Human Guardrail**: Approves before sensitive operations
5. **Data Collection**: Gathers public information
6. **Report Generation**: Formats into markdown or CSV
7. **Output**: Professional-grade deliverable

---

## Tool Functions

| Tool | Purpose | Example |
|------|---------|---------|
| `web_search` | Query for business data, reviews, contact info | `web_search("HVAC contractors Tyrone GA reviews")` |
| `write_file` | Save research output to file | `write_file("report.md", content)` |
| `human_approval` | Request approval for risky operations | `human_approval("Execute shell command to validate phone")` |
| `execute_python` | Run Python scripts for data processing | Available for CSV processing, data cleaning |

---

## Output Examples

### Tier 1: Competitor Gap Report
```markdown
==================================================
FAYETTE MARKET INTELLIGENCE - RESEARCH REPORT
==================================================

SERVICE TIER: TIER 1
INDUSTRY FOCUS: HVAC
GEOGRAPHIC AREA: Tyrone, GA
REPORT DATE: August 16, 2024

==================================================

| Contractor Name | Response Time | Online Booking | Review Sentiment | Service Gap |
|---|---|---|---|---|
| Thompson HVAC | 2-4 hours | Yes | 4.8★ (92% positive) | Weekend premium pricing not advertised |
| Local Cool Air | 24+ hours | No | 3.2★ (45% positive) | No emergency line |
| Peachtree Climate | 4-6 hours | Yes | 4.3★ (78% positive) | Commercial HVAC expertise unclear |
```

### Tier 2: Prospect Database (CSV)
```csv
business_name,decision_maker,email,phone,business_type
Thompson Construction,Mike Thompson,mike@thompson-const.com,770-555-0101,General Contractor
Fayette Property Management,Sarah Chen,s.chen@fayetteprop.com,770-555-0102,Commercial Property Mgmt
Modern Renovations LLC,David Rodriguez,david@modernreno.com,770-555-0103,Residential Remodeling
```

### Tier 3: Monthly Intelligence Summary
```markdown
## Market Intelligence Summary - August 2024

### Key Metrics
- New Market Entrants: 3 (vs 1 baseline)
- Average Review Sentiment: 4.1★ (unchanged)
- Top SEO Position: "HVAC Emergency Tyrone" - Thompson HVAC (#1)
- Competitive Pricing Trend: +3% increase across market

### Notable Changes
1. AllCool HVAC opened new Tyrone location (Aug 12)
2. Review sentiment for Local Cool Air improved (3.0→3.2★)
3. SEO rankings shifted: Thompson HVAC gains position #1 (from #3)
```

---

## Rate Limiting & Resilience

The agent automatically handles API rate limits:
- **Initial backoff**: 1 second
- **Escalation**: Doubles on each 429 error (1s → 2s → 4s → 8s... → 60s cap)
- **Fallback**: Gracefully queues failed tasks for retry

---

## Future Enhancements

Per the business plan:
1. **Web Dashboard** - FastAPI + Next.js interface for client login
2. **Real-time Monitoring** - Continuous background monitoring of competitor changes
3. **White-label SaaS** - License agent to regional marketing agencies
4. **Integration APIs** - CRM/zapier hooks for prospect data sync

---

## Compliance & Ethics

✅ Public data sources only (no private/paywalled content)  
✅ Respects rate limiting and robot.txt directives  
✅ All scraping follows Terms of Service  
✅ Manual human approval for shell operations  
✅ Encrypted storage of prospect emails  

---

## Support & Debugging

### Check Gemini API connectivity:
```python
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), 
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
client.models.retrieve("gemini-2.0-flash")
print("API connection successful!")
```

### Common Issues

**"Model not found" error**
- Verify `OPENAI_API_KEY` is set correctly
- Check Gemini API key has been provisioned in Google Cloud

**Rate limit delays**
- Agent will auto-backoff; this is normal during high-volume scraping
- Monitor console output for backoff times

**Empty report output**
- Ensure industry/location combination has viable data sources
- Try alternative location names or industry verticals

---

## Cost Analysis

**Per-Report Costs:**
- Tier 1 (Competitor Audit): ~$0.15 API cost → $150 revenue = **99.9% margin**
- Tier 2 (Prospect Database): ~$0.25 API cost → $250 revenue = **99.9% margin**
- Tier 3 (Retainer): ~$1.00/month API → $200 revenue = **99.5% margin**

**Monthly Forecast (Year 1):**
- Q1: 8 audits + 2 retainers = $2,400 revenue
- Q4: 25 audits + 12 retainers = $10,950 revenue

See full financial projections in the Fayette Market Intelligence business plan.
