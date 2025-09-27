"""Updated command-line interface for the three-tier strategy architecture."""

import json
import sys
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import tostring

import click
from rich.console import Console
from rich.table import Table
from rich import print as rich_print

from .core.strategy_manager import get_global_strategy_manager
from .core.pipeline import TripleStrategyPipeline
from .llm_clients.openwebui_client import OpenWebUIClient
from .llm_clients.anthropic_client import AnthropicClient
from .llm_clients.ollama_client import OllamaClient
from .core.exceptions import ValidationError, PipelineError


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """PromptXML Framework - Three-tier structured prompt generation with JSON-to-XML transformation."""
    pass


@main.command()
def list_strategies() -> None:
    """List all available strategies by type."""
    manager = get_global_strategy_manager()
    
    # Prompt strategies
    prompt_strategies = manager.list_prompt_strategies()
    if prompt_strategies:
        table = Table(title="Prompt Creation Strategies", style="cyan")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        for name in prompt_strategies:
            strategy = manager.get_prompt_strategy(name)
            info = strategy.get_strategy_info()
            table.add_row(name, info.get("description", ""))
        
        console.print(table)
        console.print()
    
    # Response strategies
    response_strategies = manager.list_response_strategies()
    if response_strategies:
        table = Table(title="Response Processing Strategies", style="green")
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Description", style="white")
        
        for name in response_strategies:
            strategy = manager.get_response_strategy(name)
            info = strategy.get_strategy_info()
            table.add_row(name, info.get("description", ""))
        
        console.print(table)
        console.print()
    
    # XML strategies
    xml_strategies = manager.list_xml_strategies()
    if xml_strategies:
        table = Table(title="XML Output Strategies", style="magenta")
        table.add_column("Name", style="magenta", no_wrap=True)
        table.add_column("Description", style="white")
        
        for name in xml_strategies:
            strategy = manager.get_xml_strategy(name)
            info = strategy.get_strategy_info()
            table.add_row(name, info.get("description", ""))
        
        console.print(table)


@main.command()
@click.option("--prompt-strategy", "-p", default="simple", help="Prompt creation strategy")
@click.option("--response-strategy", "-r", default="simple", help="Response processing strategy")
@click.option("--xml-strategy", "-x", default="simple", help="XML output strategy")
@click.option("--llm-client", "-c", type=click.Choice(["openwebui", "anthropic", "ollama"]),
              default="openwebui", help="LLM client to use")
@click.option("--base-url", help="Base URL for OpenWebUI/OLLAMA (default: http://localhost:11434)")
@click.option("--api-key", help="API key for the LLM client")
@click.option("--model", "-m", help="Model to use")
@click.option("--data", "-d", type=click.Path(exists=True, path_type=Path), required=True,
              help="Path to input data JSON file")
@click.option("--context", type=click.Path(exists=True, path_type=Path),
              help="Path to context data JSON file")
@click.option("--output", "-o", type=click.Path(path_type=Path),
              help="Path to save XML output (default: stdout)")
@click.option("--save-all", is_flag=True, help="Save all intermediate outputs")
def execute_pipeline(
    prompt_strategy: str,
    response_strategy: str,
    xml_strategy: str,
    llm_client: str,
    base_url: Optional[str],
    api_key: Optional[str],
    model: Optional[str],
    data: Path,
    context: Optional[Path],
    output: Optional[Path],
    save_all: bool
) -> None:
    """Execute the complete three-tier pipeline."""
    try:
        # Load input data
        with open(data, 'r') as f:
            input_data = json.load(f)
        
        # Load context if provided
        context_data = None
        if context:
            with open(context, 'r') as f:
                context_data = json.load(f)
        
        # Get strategy manager and strategies
        manager = get_global_strategy_manager()
        prompt_strat = manager.get_prompt_strategy(prompt_strategy)
        response_strat = manager.get_response_strategy(response_strategy)
        xml_strat = manager.get_xml_strategy(xml_strategy)
        
        # Create LLM client
        if llm_client == "openwebui":
            client = OpenWebUIClient(
                api_key=api_key,
                base_url=base_url or "http://localhost:11434"
            )
            default_model = model or "llama3.2"
        elif llm_client == "anthropic":
            if not api_key:
                console.print("[red]✗[/red] API key required for Anthropic client")
                sys.exit(1)
            client = AnthropicClient(api_key=api_key)
            default_model = model or "claude-3-sonnet-20240229"
        elif llm_client == "ollama":
            client = OllamaClient(
                api_key=api_key,
                base_url=base_url or "http://localhost:11434"
            )
            default_model = model or "llama3.2"
        
        # Create pipeline
        pipeline = TripleStrategyPipeline(
            prompt_strategy=prompt_strat,
            response_strategy=response_strat,
            xml_strategy=xml_strat,
            llm_client=client
        )
        
        # Validate pipeline
        pipeline.validate_pipeline()
        console.print("[green]✓[/green] Pipeline validated successfully")
        
        # Execute pipeline
        console.print("[yellow]⏳[/yellow] Executing pipeline...")
        result = pipeline.execute(
            input_data=input_data,
            context=context_data,
            model=default_model
        )
        
        # Save or display results
        if save_all:
            base_name = output.stem if output else "pipeline_output"
            base_dir = output.parent if output else Path(".")
            
            # Save prompt
            prompt_file = base_dir / f"{base_name}_prompt.txt"
            with open(prompt_file, 'w') as f:
                f.write(result["prompt"])
            console.print(f"[green]✓[/green] Prompt saved to: {prompt_file}")
            
            # Save raw response
            raw_response_file = base_dir / f"{base_name}_raw_response.txt"
            with open(raw_response_file, 'w') as f:
                f.write(result["raw_response"])
            console.print(f"[green]✓[/green] Raw response saved to: {raw_response_file}")
            
            # Save structured response
            structured_file = base_dir / f"{base_name}_structured.json"
            with open(structured_file, 'w') as f:
                json.dump(result["structured_response"], f, indent=2)
            console.print(f"[green]✓[/green] Structured response saved to: {structured_file}")
        
        # Save XML output
        xml_output = result["xml_string"]
        if output:
            with open(output, 'w') as f:
                f.write(xml_output)
            console.print(f"[green]✓[/green] XML output saved to: {output}")
        else:
            console.print("[bold]XML Output:[/bold]")
            console.print("-" * 50)
            console.print(xml_output)
        
        # Show pipeline info
        info = result["pipeline_info"]
        console.print(f"\n[bold]Pipeline Info:[/bold]")
        console.print(f"  Prompt Strategy: {info['prompt_strategy']['name']}")
        console.print(f"  Response Strategy: {info['response_strategy']['name']}")
        console.print(f"  XML Strategy: {info['xml_strategy']['name']}")
        console.print(f"  LLM Client: {info['llm_client']['client_type']}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Pipeline execution failed: {e}")
        sys.exit(1)


@main.command()
@click.option("--strategy", "-s", required=True, help="Strategy name")
@click.option("--type", "-t", type=click.Choice(["prompt", "response", "xml"]), 
              required=True, help="Strategy type")
@click.option("--data", "-d", type=click.Path(exists=True, path_type=Path), required=True,
              help="Path to input data JSON file")
@click.option("--context", type=click.Path(exists=True, path_type=Path),
              help="Path to context data JSON file")
@click.option("--output", "-o", type=click.Path(path_type=Path),
              help="Path to save output (default: stdout)")
def test_strategy(
    strategy: str,
    type: str,
    data: Path,
    context: Optional[Path],
    output: Optional[Path]
) -> None:
    """Test a specific strategy in isolation."""
    try:
        # Load input data
        with open(data, 'r') as f:
            input_data = json.load(f)
        
        # Load context if provided
        context_data = None
        if context:
            with open(context, 'r') as f:
                context_data = json.load(f)
        
        # Get strategy manager
        manager = get_global_strategy_manager()
        
        # Execute based on strategy type
        if type == "prompt":
            strategy_instance = manager.get_prompt_strategy(strategy)
            result = strategy_instance.create_prompt(input_data, context_data)
            result_type = "Prompt"
        elif type == "response":
            strategy_instance = manager.get_response_strategy(strategy)
            # For response strategies, treat input_data as raw response
            if isinstance(input_data, dict) and "raw_response" in input_data:
                raw_response = input_data["raw_response"]
            else:
                raw_response = json.dumps(input_data)
            result = strategy_instance.process_response(raw_response, context_data)
            result_type = "Structured Response"
        elif type == "xml":
            strategy_instance = manager.get_xml_strategy(strategy)
            xml_element = strategy_instance.transform_to_xml(input_data, context_data)
            result = tostring(xml_element, encoding='unicode')
            result_type = "XML Output"
        
        # Save or display result
        if output:
            if type == "response":
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                with open(output, 'w') as f:
                    f.write(result)
            console.print(f"[green]✓[/green] {result_type} saved to: {output}")
        else:
            console.print(f"[bold]{result_type}:[/bold]")
            console.print("-" * 50)
            if type == "response":
                console.print(json.dumps(result, indent=2))
            else:
                console.print(result)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Strategy test failed: {e}")
        sys.exit(1)


@main.command()
@click.option("--strategy", "-s", required=True, help="Strategy name")
@click.option("--type", "-t", type=click.Choice(["prompt", "response", "xml"]), 
              required=True, help="Strategy type")
def strategy_info(strategy: str, type: str) -> None:
    """Get detailed information about a specific strategy."""
    try:
        manager = get_global_strategy_manager()
        
        if type == "prompt":
            strategy_instance = manager.get_prompt_strategy(strategy)
        elif type == "response":
            strategy_instance = manager.get_response_strategy(strategy)
        elif type == "xml":
            strategy_instance = manager.get_xml_strategy(strategy)
        
        info = strategy_instance.get_strategy_info()
        
        console.print(f"[bold cyan]Strategy: {strategy} ({type})[/bold cyan]")
        for key, value in info.items():
            console.print(f"[bold]{key.title()}:[/bold] {value}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error getting strategy info: {e}")
        sys.exit(1)


@main.command()
@click.option("--client", "-c", type=click.Choice(["openwebui", "anthropic", "ollama"]),
              required=True, help="LLM client type")
@click.option("--base-url", help="Base URL for OpenWebUI/OLLAMA (default: http://localhost:11434)")
@click.option("--api-key", help="API key for the client")
def test_llm_client(client: str, base_url: Optional[str], api_key: Optional[str]) -> None:
    """Test LLM client connection and capabilities."""
    try:
        if client == "openwebui":
            llm_client = OpenWebUIClient(
                api_key=api_key,
                base_url=base_url or "http://localhost:11434"
            )
        elif client == "anthropic":
            if not api_key:
                console.print("[red]✗[/red] API key required for Anthropic client")
                sys.exit(1)
            llm_client = AnthropicClient(api_key=api_key)
        elif client == "ollama":
            llm_client = OllamaClient(
                api_key=api_key,
                base_url=base_url or "http://localhost:11434"
            )
        
        # Test connection
        console.print("[yellow]⏳[/yellow] Testing connection...")
        llm_client.validate_connection()
        console.print("[green]✓[/green] Connection successful")
        
        # Get client info
        info = llm_client.get_client_info()
        console.print(f"\n[bold]Client Information:[/bold]")
        for key, value in info.items():
            if key != "available_models":
                console.print(f"  {key}: {value}")
        
        # Test models
        console.print(f"\n[bold]Available Models:[/bold]")
        models = llm_client.get_available_models()
        for model in models:
            console.print(f"  • {model}")
        
        # Test generation
        console.print(f"\n[yellow]⏳[/yellow] Testing response generation...")
        response = llm_client.generate_response(
            "Hello! Please respond with a simple greeting.",
            model=models[0] if models else "default"
        )
        console.print(f"[green]✓[/green] Generation test successful")
        console.print(f"Response: {response}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Client test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()