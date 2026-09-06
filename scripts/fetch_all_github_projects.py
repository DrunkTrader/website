#!/usr/bin/env python3

"""
Fetch all public GitHub repositories for a user and generate TOML entries.
Sorts repositories by last updated date in descending order.

Edit `project_settings` below to control which repositories are visible and featured.
"""

import json
import os
import subprocess
import sys
import ssl
import time
from datetime import datetime
from urllib.parse import urlencode
from urllib.error import URLError
from urllib.request import Request, urlopen


# Set the GitHub account and control project visibility here.
github_username = "drunktrader"
project_settings = {
    # Featured
    "FixEngine": {"visible": True, "featured": True},   #1
    "discord-vault": {"visible": True, "featured": True},   #2
    "redisCLI": {"visible": True, "featured": True},    #3
    "options-pricing-model": {"visible": True, "featured": True},   #4
    
    # Non-featured & visible
    "zyn": {"visible": True, "featured": False},                        #5
    "website": {"visible": True, "featured": False},                    #6
    "yt-focustube": {"visible": True, "featured": False},               #7
    "clipIt": {"visible": True, "featured": False},                     #8
    "aStar-algorithm": {"visible": True, "featured": False},            #9
    "tradingview-data-fetcher": {"visible": True, "featured": False},   #10
    "black-scholes-model": {"visible": True, "featured": False},        #11
    "blochain": {"visible": True, "featured": False},        #12
    
    # Non-featured & hidden
    "drunktrader": {"visible": False, "featured": False},       #13
    "auto-git-committer": {"visible": False, "featured": False},    #14
    "what-im-learning": {"visible": False, "featured": False},  #15
    "OOPS_cpp": {"visible": False, "featured": False},          #16
    "amazon-scraper": {"visible": False, "featured": False},    #17
    "enso": {"visible": False, "featured": False},              #18
    "nse-scraper": {"visible": False, "featured": False},      #19
    "tail_hunterBot": {"visible": False, "featured": False},     #20
    "missile-defense-game": {"visible": False, "featured": False},  #21
    "coke-project": {"visible": False, "featured": False},      #22
    # "old-project": {"visible": False, "featured": False},
}


def create_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()

    if sys.platform == "win32" and hasattr(ssl, "enum_certificates"):
        for certificate, encoding, trust in ssl.enum_certificates("ROOT"):
            if encoding == "x509_asn" and trust:
                context.load_verify_locations(
                    cadata=ssl.DER_cert_to_PEM_cert(certificate)
                )

    return context


def fetch_json(url: str, ssl_context: ssl.SSLContext) -> list:
    request = Request(url, headers={"User-Agent": "website-project-fetcher"})

    try:
        with urlopen(request, context=ssl_context) as response:
            return json.load(response)
    except (URLError, ssl.SSLError):
        curl = "curl.exe" if os.name == "nt" else "curl"
        result = subprocess.run(
            [curl, "--fail", "--silent", "--show-error", "--location", "--user-agent", "website-project-fetcher", url],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

def fetch_all_repos(username: str) -> list:
    """
    Fetch all public repositories for a GitHub user.
    
    Args:
        username: GitHub username
        
    Returns:
        List of repository data
    """
    repos = []
    page = 1
    per_page = 100
    ssl_context = create_ssl_context()
    
    print(f"Fetching repositories for {username}...", file=sys.stderr)
    
    while True:
        params = urlencode({
            'page': page,
            'per_page': per_page,
            'type': 'owner',
            'sort': 'pushed',
            'direction': 'desc'
        })
        url = f"https://api.github.com/users/{username}/repos?{params}"
        
        try:
            data = fetch_json(url, ssl_context)
            
            if not data:
                break
                
            repos.extend(data)
            
            print(f"  Fetched page {page} ({len(data)} repos)", file=sys.stderr)
            
            if len(data) < per_page:
                break
                
            page += 1
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"Error fetching repos: {e}", file=sys.stderr)
            break
    
    return repos

def format_date(date_str: str) -> str:
    """
    Format ISO date string to Month Year format.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Formatted date string (e.g., "Jan 2024")
    """
    if not date_str:
        return ""
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %Y")
    except:
        return ""

def should_include_repo(repo: dict) -> bool:
    """
    Filter to determine if a repository should be included.
    
    Args:
        repo: Repository data from GitHub API
        
    Returns:
        True if the repo should be included
    """
    # Skip forks
    if repo.get('fork', False):
        return False
    
    # Skip repos with no description
    if not repo.get('description'):
        return False
    
    # Skip archived repos
    if repo.get('archived', False):
        return False
    
    return True

def generate_toml_entry(repo: dict) -> str:
    """
    Generate a TOML entry for a repository.
    
    Args:
        repo: Repository data from GitHub API
        
    Returns:
        TOML formatted string
    """
    lines = []
    lines.append("[[project]]")
    lines.append(f'name = "{repo["name"]}"')
    settings = project_settings.get(repo["name"], {})
    visible = str(settings.get("visible", True)).lower()
    featured = str(settings.get("featured", False)).lower()
    lines.append(f"visible = {visible}")
    lines.append(f"featured = {featured}")
    
    # Clean up description
    description = repo.get("description", "").replace('"', '\\"')
    lines.append(f'description = "{description}"')
    
    # Add created and pushed dates
    created_date = format_date(repo.get("created_at", ""))
    pushed_date = format_date(repo.get("pushed_at", ""))
    
    if created_date:
        lines.append(f'created = "{created_date}"')
    if pushed_date:
        lines.append(f'pushed = "{pushed_date}"')
    
    # Add star count if significant
    stars = repo.get("stargazers_count", 0)
    if stars > 10:
        lines.append(f'stars = {stars}')
    
    # Add language if present
    language = repo.get("language", "")
    if language:
        lines.append(f'language = "{language}"')
    
    lines.append('links = [')
    
    # Add homepage if exists
    homepage = repo.get("homepage", "")
    if homepage and homepage.strip():
        lines.append(f'  {{ name = "Homepage", url = "{homepage}" }},')
    
    # Add GitHub link
    lines.append(f'  {{ name = "GitHub", url = "{repo["html_url"]}" }},')
    lines.append(']')
    
    return '\n'.join(lines)

def main():
    """Main function to process repositories."""

    username = github_username
    
    # Fetch all repositories
    repos = fetch_all_repos(username)
    
    if not repos:
        print("No repositories found", file=sys.stderr)
        sys.exit(1)
    
    # Fetch every eligible repository; visibility is controlled by project_settings.
    filtered_repos = [repo for repo in repos if should_include_repo(repo)]
    
    # Sort by pushed_at in descending order (most recently pushed first)
    filtered_repos.sort(key=lambda x: x.get('pushed_at', ''), reverse=True)
    
    print(
        f"Found {len(repos)} total repos, including {len(filtered_repos)} eligible projects",
        file=sys.stderr,
    )
    
    # Generate TOML output
    print("# GitHub Projects")
    print(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# Total projects: {len(filtered_repos)}")
    print("")
    
    for repo in filtered_repos:
        print(generate_toml_entry(repo))
        print()

if __name__ == "__main__":
    main()