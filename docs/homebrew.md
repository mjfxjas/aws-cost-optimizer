# Distribute your programs through Homebrew

Use one public GitHub repository, `mjfxjas/homebrew-tap`, with one Ruby formula
per command-line program in `Formula/`. Users can install each program directly:

```bash
brew install mjfxjas/tap/aws-cost-optimizer
```

That command becomes available after the tap and tested formula are published.
A personal tap does not need acceptance into Homebrew's core repository.

## Release the corrected Python package first

This checkout prepares version 0.1.4. Run its checks, commit the intended changes,
push them to GitHub, and publish a `v0.1.4` GitHub release. The existing
`.github/workflows/publish.yml` publishes to PyPI when a release is published;
it requires the configured `pypi` environment and `PYPI_API_TOKEN` secret.
Check that workflow succeeds and PyPI serves 0.1.4 before creating the formula.

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m pip check
aws-cost-optimizer --help
```

## Create the shared tap once

Run these outside the program's repository. `brew tap-new` creates a separate
local Git repository. `gh repo create` publishes it publicly using your GitHub
login.

```bash
brew tap-new mjfxjas/tap
cd "$(brew --repository mjfxjas/tap)"
gh repo create mjfxjas/homebrew-tap --public --source=. --push
```

## Add this program's formula

Get the **source distribution** (`sdist`, `.tar.gz`) URL from the PyPI 0.1.4
release's download files, then use that URL with `brew create`:

```bash
brew create --python --tap=mjfxjas/tap --set-name=aws-cost-optimizer --set-license=MIT 'PASTE_PYPI_SDIST_URL_HERE'
```

Keep the generated `url`, `sha256`, and supported versioned Python dependency.
Set the formula's description and homepage, use the virtualenv helper, and
replace any generated TODO install/test code with:

```ruby
# Inside class AwsCostOptimizer < Formula:
include Language::Python::Virtualenv

# Keep url, sha256, depends_on, and generated resource blocks here.

def install
  virtualenv_install_with_resources
end

test do
  assert_match "Analyze AWS resources", shell_output("#{bin}/aws-cost-optimizer analyze --help")
  assert_match version.to_s, shell_output("#{bin}/aws-cost-optimizer --version")
  system libexec/"bin/python", "-c", "import awscrt; from awscrt import crypto"
end
```

Generate all transitive Python dependency resources, explicitly including the
Boto3 CRT extra so its version constraint on `awscrt` is respected:

```bash
brew update-python-resources mjfxjas/tap/aws-cost-optimizer --package-name=aws-cost-optimizer --extra-packages='boto3[crt]' --install-dependencies
brew install --build-from-source mjfxjas/tap/aws-cost-optimizer
brew test mjfxjas/tap/aws-cost-optimizer
brew audit --strict --online mjfxjas/tap/aws-cost-optimizer
```

Resolve installation, test, and audit failures before publishing. Homebrew
installs the program in its own environment; users do not activate a venv.
The smoke test does not access AWS. Live analysis still needs AWS credentials
and the required IAM permissions.

Commit and publish the formula from the tap repository:

```bash
cd "$(brew --repository mjfxjas/tap)"
git add Formula/aws-cost-optimizer.rb
git commit -m "Add aws-cost-optimizer formula"
git push
```

For subsequent releases, update the formula's source URL and SHA256, regenerate
Python resources, run install/test/audit, and push the change. Users upgrade with
`brew update` and `brew upgrade mjfxjas/tap/aws-cost-optimizer`.

## Add your other programs

Repeat the formula steps in the **same tap**, using each program's release
archive, name, dependencies, build steps, and a test that verifies its command.
Python CLIs can use the same virtualenv helper; compiled programs need their
own build/install instructions. GUI applications generally use casks in `Casks/`.
Do not reuse Python dependency resources across unrelated formulas.

Once each formula is published, users run:

```bash
brew install mjfxjas/tap/PROGRAM_NAME
```

## References

- [Create and maintain a tap](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [Python formulae](https://docs.brew.sh/Language-Specific-Formulae#python)
- [Formula cookbook](https://docs.brew.sh/Formula-Cookbook)
