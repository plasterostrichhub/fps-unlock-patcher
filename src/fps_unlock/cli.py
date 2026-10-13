"""Entry/bootstrap layer. Thin — parses args, delegates to services."""
from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from fps_unlock.services.patch_service import PatchService
from fps_unlock.services.profile_service import ProfileService
from fps_unlock.services.scan_service import ScanService
from fps_unlock.config.loader import load_config

console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=None)
@click.pass_context
def main(ctx: click.Context, config_path: Path | None) -> None:
    """fps-unlock-patcher — unlock frame limiters, patch FPS caps."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)


@main.command()
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def scan(ctx: click.Context, target: Path) -> None:
    """Fingerprint a game binary — engine, frame limiter, cap source."""
    report = ScanService(ctx.obj["config"]).scan(target)
    console.print(report.render())


@main.command()
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.option("--fps", "target_fps", type=int, default=0, help="0 = uncapped")
@click.option("--profile", "profile_name", default="default")
@click.pass_context
def patch(ctx: click.Context, target: Path, target_fps: int, profile_name: str) -> None:
    """Apply a frame-limiter patch to a game binary."""
    result = PatchService(ctx.obj["config"]).patch(target, target_fps, profile_name)
    console.print(result.render())
    sys.exit(0 if result.ok else 1)


@main.command("list-profiles")
@click.pass_context
def list_profiles(ctx: click.Context) -> None:
    """List installed frame-limiter profiles."""
    for profile in ProfileService(ctx.obj["config"]).list_profiles():
        console.print(f"[bold]{profile.name}[/bold]  fps={profile.target_fps}  engine={profile.engine}")


if __name__ == "__main__":
    main()