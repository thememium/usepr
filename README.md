<a name="readme-top"></a>

<div align="center">
  <a href="https://github.com/thememium/usepr">
    <img src="https://raw.githubusercontent.com/thememium/usepr/refs/heads/master/docs/images/usepr-logo-dark-bg.png" alt="usePR" width="360" height="162">
  </a>

  <p align="center">
    <em>AI-powered PR summary generator for Git repositories</em>
  </p>

  <p align="center">
    <a href="#table-of-contents"><strong>Explore the Documentation »</strong></a>
    <br />
    <a href="https://github.com/thememium/usepr/issues">Report Bug</a>
    ·
    <a href="https://github.com/thememium/usepr/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->

<a name="table-of-contents"></a>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about">About</a></li>
    <li><a href="#quick-start">Quick Start</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- ABOUT -->

## About

usepr (`usepr`) is a Python CLI that generates pull request summaries from your git commits using AI (DSPy). It analyzes your commit history and produces well-structured, meaningful PR descriptions.

- **AI-powered summaries** - Uses DSPy ChainOfThought to understand and summarize your changes
- **Template support** - Automatically detects and uses PR templates from your repository
- **Flexible diffing** - Generate summaries between any branches, tags, or commits
- **Interactive prompts** - Guided workflow with base branch and issue selection
- **Clipboard integration** - Copy generated summaries directly to clipboard
- **Model override** - Use different LLM models via the `-m` flag

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- QUICK START -->

## Quick Start

### Install usepr with uv (recommended)

```sh
uv tool install usepr
```

### Install with pipx (alternative)

```sh
pipx install usepr
```

### Generate a PR summary

```sh
usepr generate
```

This will prompt you to select a base branch, optionally link related issues, and generate a summary from your commits.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->

## Usage

### Generate a PR Summary

```sh
usepr generate
```

The interactive workflow will:

1. Detect your repository's default branch
2. Prompt for a base branch to diff against
3. Gather commits between base and HEAD
4. Ask for related issues (optional)
5. Detect and offer PR templates (if any)
6. Generate and display the summary
7. Offer to copy to clipboard

### Use a Custom Model

Set your API key as an environment variable for the provider you're using:

```sh
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

Then run with the `provider/model` format:

```sh
usepr generate -m openai/gpt-4o
usepr generate -m anthropic/claude-sonnet-4-20250514
usepr generate -m openrouter/google/gemini-2.5-flash
```

### Use the Short Alias

```sh
usepr gen
```

### Available Commands

```
generate (gen)  Generate a PR summary from commits
help            Show help
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DEVELOPMENT -->

## Development

Common tasks:

```sh
uv run poe clean-full
uv run poe test
uv run poe lint
uv run poe format
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Quick workflow:

1. Fork and branch: `git checkout -b feature/name`
2. Make changes
3. Run checks: `uv run poe clean-full`
4. Commit and push
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

License information has not been added yet.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<div align="center">
  <p>
    <sub>Built by <a href="https://github.com/thememium">thememium</a></sub>
  </p>
</div>
