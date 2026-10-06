# Homebrew distribution

The shared tap is [mjfxjas/homebrew-tap](https://github.com/mjfxjas/homebrew-tap).
AWS Cost Optimizer 0.1.4 is also available on PyPI.

## Install

```bash
brew install mjfxjas/tap/aws-cost-optimizer
aws-cost-optimizer --help
aws-cost-optimizer analyze
```

Homebrew manages Python and all dependencies, including AWS CRT for `aws login`.
There is no virtual environment activation step. Analysis still requires AWS
credentials, a region, and suitable IAM permissions.

Upgrade with:

```bash
brew update
brew upgrade mjfxjas/tap/aws-cost-optimizer
```

## Maintain the shared tap

Keep one formula per CLI in `Formula/`. Python formulae use
`Language::Python::Virtualenv`, checksummed source archives, and checksummed
resources for every runtime dependency. AWS Cost Optimizer records `boto3[crt]`
in `pypi_packages` so resource updates retain AWS CRT support. CMake is declared
as a build dependency for CRT.

For a new program release:

1. Run its regression tests and release checks.
2. Publish the release to PyPI or its normal release host.
3. Update the formula's source URL and SHA256.
4. Regenerate resources and test the formula:

   ```bash
   brew update-python-resources mjfxjas/tap/aws-cost-optimizer --install-dependencies
   brew reinstall --build-from-source mjfxjas/tap/aws-cost-optimizer
   brew test mjfxjas/tap/aws-cost-optimizer
   brew audit --strict --online mjfxjas/tap/aws-cost-optimizer
   ```

   For a just-published package, resource generation may need
   `--ignore-main-package-cooldown`. This preserves the cooldown for dependencies.

5. Commit and push the tested formula in the tap repository.

The application repository's release workflow publishes to PyPI on GitHub
release publication, using the configured `pypi` environment and
`PYPI_API_TOKEN`. The tap's generated workflows check syntax on pushes and
build/test formulas for pull requests.

## Add another program

Use the same tap instead of creating another repository. Start from that
program's released source archive:

```bash
brew create --tap=mjfxjas/tap --set-name=PROGRAM_NAME 'RELEASE_SOURCE_ARCHIVE_URL'
```

For Python CLIs, add `--python`, use the virtualenv helper, and generate all
transitive dependency resources. For compiled programs, use their actual
build/install commands and declare build tools. GUI applications generally use
casks under `Casks/`.

Add a credential-free functional test, then run build/test/audit before
publishing. Users install the new formula with
`brew install mjfxjas/tap/PROGRAM_NAME`.

## References

- [Shared tap and maintainer instructions](https://github.com/mjfxjas/homebrew-tap)
- [Create and maintain a tap](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [Python formulae](https://docs.brew.sh/Language-Specific-Formulae#python)
- [Formula cookbook](https://docs.brew.sh/Formula-Cookbook)
