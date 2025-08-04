import re
import sys
from pathlib import Path
import argparse
from dataclasses import dataclass, field
from typing import Set, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
except ImportError:
    print("rich library not found. Please install it using 'pip install rich'", file=sys.stderr)
    sys.exit(1)

console = Console()

@dataclass
class ManuscriptStats:
    name: str
    path: Path
    citations: Set[str] = field(default_factory=set)

    @property
    def count(self) -> int:
        return len(self.citations)

def get_citations_from_file(file_path: Path) -> Set[str]:
    try:
        content = file_path.read_text(encoding='utf-8')
        # Corrected regex: only matches alphanumeric characters and hyphens.
        # This prevents capturing trailing punctuation (like '.') or parts of emails/imports.
        # It also filters out false positives like '@preview/' from import statements.
        citations = set(re.findall(r'@([a-zA-Z0-9-]+)', content))
        # Further filter out known non-citation patterns that might be caught
        known_false_positives = {'preview', 'proton'}
        return citations - known_false_positives
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}", style="error")
        return set()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Could not read file {file_path}: {e}", style="error")
        return set()

def get_bib_keys(bib_path: Path) -> Set[str]:
    try:
        bib_content = bib_path.read_text(encoding='utf-8')
        return set(re.findall(r'@\w+{([^,]+),', bib_content))
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File not found: {bib_path}", style="error")
        return set()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Could not read file {bib_path}: {e}", style="error")
        return set()

def compare_references(manuscript_paths: List[Path], bib_path: Path):
    manuscripts = [ManuscriptStats(path.name, path, get_citations_from_file(path)) for path in manuscript_paths]
    bib_keys = get_bib_keys(bib_path)
    
    if not bib_keys:
        return

    all_manuscript_citations = set().union(*(m.citations for m in manuscripts))

    # --- Summary Table ---
    summary_table = Table(title="[bold cyan]Citation and Bibliography Summary[/bold cyan]", title_justify="left")
    summary_table.add_column("Item", style="magenta")
    summary_table.add_column("Count", justify="right", style="bold green")
    
    for m in manuscripts:
        summary_table.add_row(f'Unique citations in "{m.name}"', str(m.count))
    summary_table.add_row("Total unique citations across all manuscripts", str(len(all_manuscript_citations)))
    summary_table.add_row(f'Total keys in "{bib_path.name}"', str(len(bib_keys)))
    
    console.print(summary_table)

    # --- Comparison Logic ---
    missing_in_bib = all_manuscript_citations - bib_keys
    uncited_in_manuscripts = bib_keys - all_manuscript_citations

    # --- Manuscript vs. Manuscript Comparison ---
    if len(manuscripts) == 2:
        m1, m2 = manuscripts[0], manuscripts[1]
        diff1 = m1.citations - m2.citations
        diff2 = m2.citations - m1.citations

        if not diff1 and not diff2:
             rprint(Panel("[bold green]Perfect Match![/bold green] Both manuscripts have the exact same citations.", title="Manuscript Comparison", border_style="green"))
        else:
            diff_table = Table(title="[bold cyan]Manuscript to Manuscript Comparison[/bold cyan]", title_justify="left")
            diff_table.add_column(f'Only in "{m1.name}" ({len(diff1)})', style="yellow")
            diff_table.add_column(f'Only in "{m2.name}" ({len(diff2)})', style="blue")
            max_len = max(len(diff1), len(diff2))
            diff1_list, diff2_list = sorted(list(diff1)), sorted(list(diff2))
            for i in range(max_len):
                item1 = diff1_list[i] if i < len(diff1_list) else ""
                item2 = diff2_list[i] if i < len(diff2_list) else ""
                diff_table.add_row(item1, item2)
            console.print(diff_table)

    # --- Manuscript vs. Bib Comparison ---
    rprint(Panel("[bold cyan]Manuscript vs. Bibliography (.bib) Analysis[/bold cyan]", style="cyan"))
    if not missing_in_bib and not uncited_in_manuscripts:
        rprint(Panel("[bold green]Perfect Match![/bold green] All manuscript citations are in the .bib file, and all .bib keys are cited.", title="Analysis Result", border_style="green"))
    else:
        if missing_in_bib:
            missing_table = Table(title=f"[bold red]Warning: {len(missing_in_bib)} Missing Keys in .bib File[/bold red]", title_justify="left")
            missing_table.add_column("Missing Key", style="red")
            missing_table.add_column("Cited In", style="yellow")
            for item in sorted(list(missing_in_bib)):
                sources = [m.name for m in manuscripts if item in m.citations]
                missing_table.add_row(item, ", ".join(sources))
            console.print(missing_table)
        else:
            rprint("[green]Check complete: All manuscript citations are present in the .bib file.[/green]")

        if uncited_in_manuscripts:
            uncited_table = Table(title=f"[bold yellow]Notice: {len(uncited_in_manuscripts)} Uncited Keys in Manuscripts[/bold yellow]", title_justify="left")
            uncited_table.add_column("Uncited Key", style="yellow")
            for item in sorted(list(uncited_in_manuscripts)):
                uncited_table.add_row(item)
            console.print(uncited_table)
        else:
            rprint("[green]Check complete: All keys in the .bib file are cited in the manuscripts.[/green]")


def main():
    parser = argparse.ArgumentParser(description="Compare citations in manuscript files against a .bib library and against each other.")
    parser.add_argument('manuscripts', nargs='+', help="Paths to the manuscript .typ files.")
    parser.add_argument('--bib', required=True, help="Path to the .bib file.")
    
    args = parser.parse_args()

    manuscript_paths = [Path(p) for p in args.manuscripts]
    bib_file = Path(args.bib)
    
    compare_references(manuscript_paths, bib_file)

if __name__ == '__main__':
    # To run from command line:
    # python src/compare_refs.py src-typ/manuscript_cn.typ src-typ/manuscript_en.typ --bib src-typ/references.bib
    # For direct execution within an environment that doesn't pass args, we can hardcode them.
    if len(sys.argv) == 1:
        # Hardcoded paths for simple execution (e.g., pressing 'play' in VS Code)
        MANUSCRIPT_FILES = [Path('src-typ/manuscript_cn.typ'), Path('src-typ/manuscript_en.typ')]
        BIB_FILE = Path('src-typ/references.bib')
        compare_references(MANUSCRIPT_FILES, BIB_FILE)
    else:
        main()
