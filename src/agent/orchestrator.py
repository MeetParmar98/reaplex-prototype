import asyncio
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel

# Add project root and src to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from src.agent.llm import OllamaClient
from src.agent.tools import AgentTools
from src.classifier.classifier import classify
from src.scraper.executor import ScraperExecutor

console = Console()


class AgentOrchestrator:
    def __init__(self):
        # Allow user to specify model via env var or input, default provided
        self.llm = OllamaClient(model="gemma:2b")
        self.tools = AgentTools()

    async def run(self):
        self.print_banner()

        # 1. Setup Phase
        model_name = Prompt.ask("Enter Ollama Model Name", default="gemma3:1b")
        self.llm.model = model_name

        goal = Prompt.ask("\n[bold green]What is your mission?[/bold green]")

        with console.status("[bold green]Consulting the Brain..."):
            try:
                plan = self.llm.generate_plan(goal)
            except Exception as e:
                console.print(f"[bold red]LLM Error:[/bold red] {e}")
                return

        # 2. Review Phase
        self.print_plan(plan)

        if not Confirm.ask("Do you want to proceed with this plan?"):
            console.print("[yellow]Mission Aborted.[/yellow]")
            return

        # 3. Execution Phase: Discovery
        console.print("\n[bold cyan]Phase 1: Discovery[/bold cyan]")
        queries = plan.get("search_queries", [])

        with console.status(f"Searching Google for {len(queries)} queries..."):
            urls = await self.tools.discover_urls(queries)

        if not urls:
            console.print(
                "[yellow]No URLs found via search. Falling back to LLM knowledge...[/yellow]"
            )
            try:
                answer = self.llm.chat(
                    [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. The search engine failed to find external sources. Answer the user's request based on your internal knowledge.",
                        },
                        {"role": "user", "content": goal},
                    ]
                )
                console.print(
                    Panel(
                        answer,
                        title="LLM Internal Knowledge Answer",
                        border_style="yellow",
                    )
                )
            except Exception as e:
                console.print(f"[red]LLM Fallback failed:[/red] {e}")
            return

        console.print(f"[green]Found {len(urls)} potential URLs[/green]")
        
        # Save discovered URLs to JSON file
        self._save_discovered_urls(urls, queries, goal)

        # 4. Execution Phase: Classify & Scrape
        console.print("\n[bold cyan]Phase 2: Classifying & Scraping[/bold cyan]")
        force_js = plan.get("force_js", False)
        
        # Initialize scraper
        scraper_executor = ScraperExecutor()
        
        # Process each URL
        successful = 0
        failed = 0
        skipped = 0
        
        for i, url in enumerate(urls, 1):
            console.print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
            
            # Classify URL
            classification = classify({"url": url, "render_js": force_js})
            
            if classification == "skip":
                console.print(f"  [yellow]⏭️  Skipped (non-HTML resource)[/yellow]")
                skipped += 1
                continue
            
            # Determine if we need JS scraping
            needs_js = (classification == "browser") or force_js
            
            try:
                # Scrape the URL
                payload = {
                    "url": url,
                    "force_js": needs_js,
                    "job_id": f"job_{i}_{int(time.time())}"
                }
                
                scraper_executor.run(payload)
                console.print(f"  [green]✅ Scraped successfully ({'JS' if needs_js else 'HTML'})[/green]")
                successful += 1
                
            except Exception as e:
                console.print(f"  [red]❌ Failed: {str(e)[:50]}[/red]")
                failed += 1
                continue
        
        # Summary
        console.print(f"\n[bold cyan]Scraping Complete![/bold cyan]")
        console.print(f"[green]✅ Successful: {successful}[/green]")
        console.print(f"[red]❌ Failed: {failed}[/red]")
        console.print(f"[yellow]⏭️  Skipped: {skipped}[/yellow]")
        console.print(f"\n[green]💾 All scraped content saved to: data/raw/ and data/structured/[/green]")

    def print_banner(self):
        console.print(
            Panel.fit(
                "[bold purple]REAPLEX AGENT[/bold purple]\n"
                "[white]Autonomous Scraping Orchestrator[/white]",
                border_style="purple",
            )
        )

    def print_plan(self, plan):
        console.print("\n[bold]Proposed Mission Plan:[/bold]")
        console.print(f"[blue]Interpretation:[/blue] {plan.get('interpretation')}")
        console.print(f"[blue]Target:[/blue] {plan.get('target_description')}")
        console.print(f"[blue]Force JS:[/blue] {plan.get('force_js')}")
        console.print("[blue]Search Queries:[/blue]")
        for q in plan.get("search_queries", []):
            console.print(f"  - {q}")
        console.print("")

    def _save_discovered_urls(self, urls: list, queries: list, goal: str):
        """
        Save discovered URLs to a JSON file for reference.
        """
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        discovered_dir = data_dir / "discovered_urls"
        discovered_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = discovered_dir / f"urls_{timestamp}.json"
        
        # Prepare data structure
        data = {
            "mission": goal,
            "search_queries": queries,
            "discovered_at": datetime.now().isoformat(),
            "total_urls": len(urls),
            "urls": urls
        }
        
        # Save to JSON file
        filename.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        console.print(f"[green]💾 Discovered URLs saved to: {filename.absolute()}[/green]")


if __name__ == "__main__":
    asyncio.run(AgentOrchestrator().run())
