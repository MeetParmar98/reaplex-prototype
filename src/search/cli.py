#!/usr/bin/env python3
# cli.py
# Reaplex Search CLI
#
# Clean, modern CLI powered by Typer + Rich
# Logic unchanged — presentation & structure improved only

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add src to path (for F5 execution and direct module imports)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from advanced_search import AdvancedSearcher
from execution.serpapi_formatter import SerpAPIFormatter

app = typer.Typer(
    help="🔍 Reaplex Search — Google Scraper with Multi-Layer Anti-Bot Evasion",
    add_completion=False,
)

console = Console()


# -----------------------------
# UI helpers
# -----------------------------

def header():
    console.print(
        Panel.fit(
            "[bold cyan]REAPLEX SEARCH[/bold cyan]\n"
            "[white]Google Scraper with 4-Layer Anti-Bot Evasion[/white]",
            border_style="cyan",
        )
    )


def step(title: str):
    console.print(f"\n[bold cyan]➤ {title}[/bold cyan]")


def success(msg: str):
    console.print(f"[green]✔ {msg}[/green]")


def info(msg: str):
    console.print(f"[dim]• {msg}[/dim]")


def error(msg: str):
    console.print(f"[bold red]✖ {msg}[/bold red]")


# -----------------------------
# Main command
# -----------------------------

@app.command()
def search(
    query: Optional[str] = typer.Argument(
        None, help="Search query (e.g. 'coffee shops nyc')"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output JSON file"
    ),
    engine: str = typer.Option(
        "google", "--engine", "-e", help="Search engine (google | bing)"
    ),
    country: str = typer.Option("us", "--country", "-c", help="Country code"),
    language: str = typer.Option("en", "--language", "-l", help="Language code"),
    headless: bool = typer.Option(
        False, "--headless", help="Run browser headless (not recommended)"
    ),
    no_headless: bool = typer.Option(
        False, "--no-headless", help="Run browser with visible window"
    ),
    debug: bool = typer.Option(False, "--debug", help="Save raw HTML"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Perform a Google search and return SerpAPI-formatted JSON results.
    """

    header()

    if not query:
        query = typer.prompt("Enter search query")

    final_headless = headless and not no_headless

    async def run():
        try:
            # -----------------------------
            # Pillar 1 — Stealth
            # -----------------------------
            step("Initializing stealth layers")
            info("TLS: Chrome124 BoringSSL fingerprint")
            info("Behavior: Human biometrics with jitter")

            # -----------------------------
            # Pillar 2 — Browser execution
            # -----------------------------
            step(f"Connecting to {engine.capitalize()}")

            searcher = AdvancedSearcher(
                headless=final_headless,
                engine=engine,
            )
            await searcher.start()
            success("Browser session established")

            # -----------------------------
            # Pillar 3 — Search
            # -----------------------------
            step(f"Searching for '{query}'")

            html = await searcher.search(query)
            success(f"Fetched {len(html)} bytes")

            if debug:
                debug_file = Path(
                    f"debug_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
                debug_file.write_text(html, encoding="utf-8")
                info(f"Debug HTML saved to {debug_file.name}")

            await searcher.close()

            # -----------------------------
            # Pillar 4 — Formatting
            # -----------------------------
            step("Formatting results (SerpAPI compatible)")

            formatter = SerpAPIFormatter(
                query=query,
                location=country,
                device="desktop" if final_headless else "mobile",
            )

            results = formatter.format(html)

            organic = results.get("organic_results", [])
            urls = results.get("all_result_links", [])

            success(f"Organic results: {len(organic)}")
            success(f"Total URLs: {len(urls)}")

            # -----------------------------
            # Save output
            # -----------------------------
            output_path = output or Path(
                f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            output_path.write_text(
                formatter.to_json(results, pretty=True),
                encoding="utf-8",
            )

            success(f"Saved results to {output_path.absolute()}")

            # -----------------------------
            # Summary table
            # -----------------------------
            table = Table(title="Results Summary", show_header=False)
            table.add_row("Query", query)
            table.add_row("Engine", engine)
            table.add_row("Organic Results", str(len(organic)))
            table.add_row("Total URLs", str(len(urls)))
            table.add_row(
                "Knowledge Graph",
                "Yes" if results.get("knowledge_graph") else "No",
            )
            table.add_row(
                "Local Places",
                str(len(results.get("local_results", {}).get("places", []))),
            )
            table.add_row(
                "Related Questions",
                str(len(results.get("related_questions", []))),
            )
            table.add_row(
                "Products",
                str(len(results.get("immersive_products", []))),
            )

            console.print("\n", table)

            # -----------------------------
            # Preview top results
            # -----------------------------
            if organic:
                console.print("\n[bold cyan]Top 3 Organic Results[/bold cyan]")
                for i, r in enumerate(organic[:3], 1):
                    console.print(
                        f"\n[bold]{i}. {r.get('title')}[/bold]\n"
                        f"[blue]{r.get('displayed_link')}[/blue]\n"
                        f"{r.get('snippet', '')[:120]}..."
                    )

        except Exception as e:
            error(str(e))
            if verbose:
                raise

    asyncio.run(run())


def main():
    app()


if __name__ == "__main__":
    main()
