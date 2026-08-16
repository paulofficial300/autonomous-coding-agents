import os
import json
import subprocess
import time
import re
from datetime import datetime
from openai import OpenAI

# Terminal color codes
RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Initialize client for Google Gemini
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MODEL = "gemini-2.0-flash"

# ==========================================
# FAYETTE MARKET INTELLIGENCE SERVICE TIERS
# ==========================================

SERVICE_PROMPTS = {
    "tier1": """You are an autonomous market research agent for Fayette Market Intelligence.
    
TASK: Competitor Gap Snapshot Analysis
GOAL: Audit 10 local {industry} contractors in {location} and deliver:
1. Emergency response times (if available)
2. Online booking availability (yes/no)
3. Review sentiment analysis (positive/neutral/negative breakdown)
4. Identified service gaps (pricing transparency, availability windows, specializations)

OUTPUT FORMAT: Structured markdown table with columns:
| Contractor Name | Response Time | Online Booking | Review Sentiment | Service Gap |

Search for each contractor's website, Google Business, Yelp, and recent reviews.
Compile findings into a clean, professional report suitable for client delivery.""",

    "tier2": """You are an autonomous market research agent for Fayette Market Intelligence.

TASK: Verified B2B Prospect Database Generation
GOAL: Identify and validate 50 local commercial prospects in {location} within the {industry} sector.
Gather for each prospect:
1. Business name
2. Decision-maker name (owner/manager)
3. Verified email address
4. Direct phone line
5. Business type/classification

OUTPUT FORMAT: CSV with headers:
business_name,decision_maker,email,phone,business_type

Priority: Target mid-market commercial entities likely to need {industry} services.
Ensure all contact information is publicly available and current.""",

    "tier3": """You are an autonomous market research agent for Fayette Market Intelligence.

TASK: Bi-Weekly Market Intelligence Monitoring
GOAL: Track competitive landscape changes for {industry} in {location}:
1. Competitor pricing updates (if publicly listed)
2. New market entrants (new business registrations)
3. Review sentiment trends (aggregate scoring changes)
4. Local SEO ranking shifts (top 5 positions for key search terms)

OUTPUT FORMAT: Executive summary with key metrics and trend indicators.
This will be run bi-weekly and compared against baseline metrics."""
}

# ==========================================
# TOOL IMPLEMENTATIONS
# ==========================================

def web_search(query, num_results=10):
    """Simulate or execute web search using system tools."""
    print(f"{BLUE}[SEARCHING] {query}{RESET}")
    # In production, integrate with Tavily API or similar
    # For now, return structured placeholder
    return f"Web search executed for: {query}. (Results would be fetched from Tavily/Perplexity API)"

def write_file(filepath, content):
    """Write research output to file."""
    with open(filepath, 'w') as f:
        f.write(content)
    return f"Success: Report written to {filepath}"

def execute_python(filepath):
    """Execute Python scripts for data processing."""
    try:
        result = subprocess.run(['python', filepath], capture_output=True, text=True, timeout=30)
        return f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
    except Exception as e:
        return str(e)

def human_approval(action_description):
    """Human-in-the-loop guardrail for sensitive operations."""
    print(f"\n{YELLOW}⚠️  HUMAN APPROVAL REQUIRED{RESET}")
    print(f"Action: {action_description}")
    response = input(f"{YELLOW}Approve? (yes/no): {RESET}").strip().lower()
    return response == 'yes'

def validate_email(email):
    """Simple email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_report_header(service_tier, industry, location, client_name=""):
    """Generate professional report header."""
    timestamp = datetime.now().strftime("%B %d, %Y")
    header = f"""
{'='*70}
FAYETTE MARKET INTELLIGENCE - RESEARCH REPORT
{'='*70}

SERVICE TIER: {service_tier}
INDUSTRY FOCUS: {industry}
GEOGRAPHIC AREA: {location}
REPORT DATE: {timestamp}
{"CLIENT: " + client_name if client_name else ""}

{'='*70}

"""
    return header

# ==========================================
# TOOL DISPATCHER (Safe Pattern)
# ==========================================

TOOL_MAP = {
    "web_search": web_search,
    "write_file": write_file,
    "execute_python": execute_python,
    "human_approval": human_approval,
}

# ==========================================
# AUTONOMOUS AGENT EXECUTION
# ==========================================

def run_market_research_agent(service_tier, industry, location, client_name=""):
    """
    Execute autonomous market research for one of three service tiers.
    
    Args:
        service_tier: 'tier1', 'tier2', or 'tier3'
        industry: e.g., 'HVAC', 'Plumbing', 'Roofing', 'Electrical'
        location: e.g., 'Tyrone, GA' or 'Fayette County, GA'
        client_name: Optional client name for personalization
    """
    
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}FAYETTE MARKET INTELLIGENCE - AUTONOMOUS AGENT{RESET}")
    print(f"{CYAN}Service Tier: {service_tier.upper()} | Industry: {industry} | Location: {location}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")
    
    # Get service-specific prompt
    if service_tier not in SERVICE_PROMPTS:
        print(f"{RED}Error: Unknown service tier '{service_tier}'{RESET}")
        return
    
    system_prompt = SERVICE_PROMPTS[service_tier]
    user_goal = system_prompt.format(industry=industry, location=location)
    
    # Add rate limit handling metadata
    max_attempts = 8
    attempt = 0
    backoff_time = 1
    
    messages = [
        {
            "role": "system",
            "content": """You are an autonomous AI market research agent for Fayette Market Intelligence.
You operate under strict security guardrails:
1. Only use publicly available data sources
2. Respect robot.txt and rate limiting
3. Call human_approval before executing any shell commands
4. Format all output as clean markdown or CSV
5. Validate email addresses before including them
6. If you encounter rate limits, request exponential backoff delays

Always explain your reasoning before taking actions."""
        },
        {"role": "user", "content": user_goal}
    ]
    
    # Define tools for this agent
    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for business information, reviews, and contact details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for market research"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write research findings to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Output file path"},
                        "content": {"type": "string", "description": "Report content"}
                    },
                    "required": ["filepath", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "human_approval",
                "description": "Request human approval for sensitive operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_description": {"type": "string", "description": "Description of action requiring approval"}
                    },
                    "required": ["action_description"]
                }
            }
        }
    ]
    
    # Main agentic loop
    while attempt < max_attempts:
        attempt += 1
        print(f"\n{CYAN}[Agent Loop {attempt}/{max_attempts}]{RESET}")
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                temperature=0.7,
                max_tokens=4096
            )
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                print(f"{RED}Rate limit hit. Exponential backoff: {backoff_time}s{RESET}")
                time.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, 60)  # Cap at 60 seconds
                continue
            else:
                print(f"{RED}Error: {e}{RESET}")
                break
        
        msg = response.choices[0].message
        messages.append(msg)
        
        # Display agent reasoning
        if msg.content:
            print(f"{CYAN}[Thought]{RESET}\n{msg.content}\n")
        
        # Process tool calls
        if msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"{YELLOW}[Tool Call] {tc.function.name}{RESET}")
                
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    print(f"{RED}Failed to parse tool arguments{RESET}")
                    continue
                
                # Dispatch to tool
                if tc.function.name in TOOL_MAP:
                    tool_func = TOOL_MAP[tc.function.name]
                    result = tool_func(**args)
                else:
                    result = f"Unknown tool: {tc.function.name}"
                
                print(f"{GREEN}[Result]{RESET}\n{result}\n")
                
                # Append tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.function.name,
                    "content": result
                })
        else:
            # No more tool calls - agent has completed
            print(f"\n{GREEN}🎯 Research Complete{RESET}")
            break
    
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{GREEN}Report generation finished. Check output files for deliverable.{RESET}")
    print(f"{GREEN}{'='*70}{RESET}\n")

# ==========================================
# ORDER INTAKE & ROUTING
# ==========================================

def intake_order():
    """Simple CLI interface for order intake."""
    print(f"\n{YELLOW}{'='*70}{RESET}")
    print(f"{YELLOW}FAYETTE MARKET INTELLIGENCE - ORDER INTAKE{RESET}")
    print(f"{YELLOW}{'='*70}{RESET}\n")
    
    print("Select Service Tier:")
    print("  1) Competitor Gap Snapshot ($150) - 24hr turnaround")
    print("  2) B2B Prospect Database ($250) - 48hr turnaround")
    print("  3) Monthly Intelligence Retainer ($200/mo) - Bi-weekly updates")
    
    tier_choice = input("\nEnter choice (1-3): ").strip()
    
    tier_map = {"1": "tier1", "2": "tier2", "3": "tier3"}
    if tier_choice not in tier_map:
        print(f"{RED}Invalid choice{RESET}")
        return
    
    service_tier = tier_map[tier_choice]
    
    industry = input("\nIndustry (HVAC/Plumbing/Roofing/Electrical/etc): ").strip()
    location = input("Geographic Area (e.g., Tyrone, GA or Fayette County): ").strip()
    client_name = input("Client Name (optional): ").strip()
    
    print(f"\n{GREEN}Order received. Starting agent...{RESET}\n")
    
    run_market_research_agent(service_tier, industry, location, client_name)

# ==========================================
# MAIN ENTRY POINT
# ==========================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        # Interactive order intake mode
        intake_order()
    else:
        # Demo mode: Run a sample tier 1 audit
        print(f"{YELLOW}Running DEMO: Competitor Gap Snapshot for HVAC contractors in Tyrone, GA{RESET}\n")
        run_market_research_agent(
            service_tier="tier1",
            industry="HVAC",
            location="Tyrone, GA",
            client_name="Demo Client"
        )
