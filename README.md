# website

Visit at [drunktrader.dev](https://drunktrader.dev)

---

## Stack

- Framework: [Zola](https://www.getzola.org/)
- Theme: Adapted [zola-bearblog](https://codeberg.org/alanpearce/zola-bearblog) with some custom styles.
- Deployment: Caddy + Hetzner VPS + Cloudflare
- Analytics: Plausible Analytics


---
## Commands
- `zola serve` - Run a local development server
- `zola build` - Build the static site
- `zola check` - Check for errors in the site
- 'python scripts/fetch_all_github_projects.py > content/projects/data.toml; zola build'