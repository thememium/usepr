# Changelog

## v0.1.4 (2026-06-21)

[Compare changes](https://github.com/thememium/usepr/compare/v0.1.3...v0.1.4)

### 🏡 Chore

- **pyproject**: bump usecli to 0.1.68 ([9f31317](https://github.com/thememium/usepr/commit/9f31317ea82a8ab604a8fe5a69f03f377789b4b0))

### Contributors

- Edward Boswell <thememium@gmail.com>

## v0.1.3 (2026-06-21)

[Compare changes](https://github.com/thememium/usepr/compare/v0.1.2...v0.1.3)

### 🏡 Chore

- **pyproject**: bump usecli to 0.1.68 ([9f31317](https://github.com/thememium/usepr/commit/9f31317ea82a8ab604a8fe5a69f03f377789b4b0))

### Contributors

- Edward Boswell <thememium@gmail.com>

## v0.1.2 (2026-06-21)

[Compare changes](https://github.com/thememium/usepr/compare/v0.1.1...v0.1.2)

### 💅 Refactors

- **test**: clean up unused imports and formatting in test files ([2dd4527](https://github.com/thememium/usepr/commit/2dd452742e0e1b6e0caa534357a527ce6a602f54))

### 📖 Documentation

- add usepr logo with dark background to documentation ([47bf9e3](https://github.com/thememium/usepr/commit/47bf9e39fb8f2027bf90753334570061b75607a3))
- **README**: replace title header with logo image ([392a4c9](https://github.com/thememium/usepr/commit/392a4c91222f87ae7ff484534373204b3069f83b))
- add bug report issue template ([4100957](https://github.com/thememium/usepr/commit/410095745ee577c666962b2e09b1190236a59763))
- **.github**: add comprehensive contributing guide ([e53b3dd](https://github.com/thememium/usepr/commit/e53b3dd169b5f626d7b8520dd8308baa1b1a3ad7))
- **SECURITY**: add vulnerability reporting guidelines ([6647cfa](https://github.com/thememium/usepr/commit/6647cfacfb09fed8b00caaa81a16c2a20e24607f))

### 🏡 Chore

- add license file and pyproject metadata ([06d62df](https://github.com/thememium/usepr/commit/06d62df146113cf4899cd7709ab1b7004880766b))

### ✅ Tests

- **smoke**: add smoke test for usepr CLI and import ([2aaaac7](https://github.com/thememium/usepr/commit/2aaaac7e3572f9986ac979b04246703a654c7920))

### Contributors

- Edward Boswell <thememium@gmail.com>

## v0.1.1 (2026-06-19)

### 🚀 Enhancements

- add services layer for PR summary generation ([149bb57](https://github.com/thememium/usepr/commit/149bb57d92c07682ae51a95aaefcbdd5f6203578))
- **cli**: allow overriding the default LLM model in the generate command ([91fdcc4](https://github.com/thememium/usepr/commit/91fdcc400abc06475d6d2fc4c99e896694416563))
- **usepr/configs**: add dspy configuration utilities ([1776684](https://github.com/thememium/usepr/commit/17766844ce3f11f3231d8ecf8e468d9fe5138290))
- **pull_request_summary_generator**: add template support ([c1124ec](https://github.com/thememium/usepr/commit/c1124ec193c666ebcb1e382d1f5b8eec7dbdda1b))
- **cli/generate**: add PR template selection ([8d57054](https://github.com/thememium/usepr/commit/8d57054f31203f465724d24f636a9b581b42c1a8))
- **pull_request_summary_generator**: enable template‑based summary ([a15a300](https://github.com/thememium/usepr/commit/a15a300924e2b67ebb9721986e4fa1fd50516c86))
- **usepr**: add GitHub PR template utilities ([27d3dc6](https://github.com/thememium/usepr/commit/27d3dc68e6201bd51a525fe1147cf5f56b16bafc))
- **generate**: add pull request summary generator ([3520ece](https://github.com/thememium/usepr/commit/3520ece54c3c794f0d6e2bb87666052e7534c98f))
- **pull_request_summary_generator**: add module to generate PR summaries ([32ffc9b](https://github.com/thememium/usepr/commit/32ffc9b7ec9fd66d09594faa7c8593adc7d9c4c5))
- **utils**: add git helper utilities ([f3fb1e6](https://github.com/thememium/usepr/commit/f3fb1e6617bca86756d3f167d31bc1207402e646))
- **signatures**: add PullRequestSummaryGeneratorSignature ([f0217e4](https://github.com/thememium/usepr/commit/f0217e4e175d811defaaf1cd1d571e9e82597ff7))
- **cli**: add new title artwork and update config to use it ([538f201](https://github.com/thememium/usepr/commit/538f2012944690f737af93d9dfd3f181f39765c9))
- **cli**: add usecli configuration file ([e75c7cb](https://github.com/thememium/usepr/commit/e75c7cb4332f717c6609ad7e22d14260eff0e1f3))
- **cli**: Add generate command to provide an example CLI flow ([3f7574e](https://github.com/thememium/usepr/commit/3f7574e2b32c303f6e31e7bd30997fbc77af1133))
- **cli**: add command template ([c3e0520](https://github.com/thememium/usepr/commit/c3e052044d7ae74693de8ff16486ed633553bf5b))
- add default theme and logo ([c5333f2](https://github.com/thememium/usepr/commit/c5333f26be800fceb0c8fef3a69aa8056c7bb5a0))

### 🩹 Fixes

- **pull_request_summary_generator**: adjust rules selection logic ([ea02966](https://github.com/thememium/usepr/commit/ea02966076f1a74f0134ba79a0c98c07db38d661))

### 💅 Refactors

- **generate_command.py**: move summary logic to services and simplify CLI ([4caa022](https://github.com/thememium/usepr/commit/4caa0220893bab31a064ac0ac8da5a68d3a5bb46))
- **generate_command**: unify theme usage and handle empty prompts correctly ([7dcb3c8](https://github.com/thememium/usepr/commit/7dcb3c892e0aef0b5c474a4020f17c30e9b52da4))
- **pull_request_summary_generator**: fix dspy import and field formatting ([211a2a2](https://github.com/thememium/usepr/commit/211a2a23487cffd92292475ab94d0efdf0bbf9a2))
- **usepr**: remove example main function from package init ([b378a8d](https://github.com/thememium/usepr/commit/b378a8db4e1d59673b572bc59885cd02d224adc5))

### 📖 Documentation

- update installation instructions for usepr ([846f45a](https://github.com/thememium/usepr/commit/846f45a78a3b21c54533008a32a0f088cde8bc17))
- **readme**: add comprehensive README with usage and dev info ([d3a1cab](https://github.com/thememium/usepr/commit/d3a1cab4195f53e123a3b598046367f66375a7eb))

### 📦 Build

- **pyproject.toml**: add usecli dependency ([084d532](https://github.com/thememium/usepr/commit/084d532c25ab93f8f6384f5e58be3bd9ebcc857a))

### 🏡 Chore

- **usepr**: add empty configs package __init__.py ([38301bf](https://github.com/thememium/usepr/commit/38301bf955bbb683bbc03694707aa4141455faf4))
- **deps**: add pyyaml and typer to pyproject.toml ([303d12f](https://github.com/thememium/usepr/commit/303d12fd50e0f517b0f3306c94c716ed4672d827))
- **.gitignore**: ignore .omo ([ed2bde2](https://github.com/thememium/usepr/commit/ed2bde2ae69c131c19a7d83faf81b6aff23f2b82))
- **deps**: add rich for improved console formatting ([6852411](https://github.com/thememium/usepr/commit/685241117ba7bee96f3b168d0d31d3c46848d006))
- **modules**: add empty __init__ to enable package imports ([5be456c](https://github.com/thememium/usepr/commit/5be456c0681224dba6aac842d3403a47dd23d972))
- **deps**: add dspy and pyperclip ([fa1e004](https://github.com/thememium/usepr/commit/fa1e004e51b5997c7039466f96d52fe53e473595))
- **config**: hide inspire messages by default ([25a0b94](https://github.com/thememium/usepr/commit/25a0b9483f9c655da09f82e5ea0ff56d39512b63))
- **usepr/cli**: add __init__.py to make cli a package ([97b2a5d](https://github.com/thememium/usepr/commit/97b2a5daa75b0788894db8cf8b733c50dea4fd9d))
- **pyproject**: rename script entry and add src package discovery ([4048942](https://github.com/thememium/usepr/commit/4048942855952bdbb4a96a34e5326e5d2f71dc59))

### ✅ Tests

- add comprehensive tests for usepr utilities and modules ([54648d3](https://github.com/thememium/usepr/commit/54648d38d02c38aefbc715ab0185189fcd021993))

### 🎨 Styles

- **pyproject**: tidy formatting and add pytest filterwarnings ([3f4bc5d](https://github.com/thememium/usepr/commit/3f4bc5d056e568e69e6c307e47409ba5d7248aab))

### Other Changes

- Merge pull request #1 from thememium/eboswell/feat/github-template (#1) ([6f79a80](https://github.com/thememium/usepr/commit/6f79a804dc9c68afd7c0a8dc293ba7ac9a006425))

### Contributors

- Edward Boswell <thememium@gmail.com>
