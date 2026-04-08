# Installation

## One-Time Auth Setup

```bash
npm login --scope=@devonenergyenterprise --auth-type=legacy --registry=https://npm.pkg.github.com
```

Username: GitHub username | Password: GitHub PAT with `read:packages` scope (SSO authorized for DevonEnergyEnterprise)

## Install

```bash
npm install @devonenergyenterprise/core-utils @devonenergyenterprise/service-utils @devonenergyenterprise/ag-grid-presets @devonenergyenterprise/ui-react @devonenergyenterprise/telemetry
```

## Azure Pipelines Auth

Add pipeline variable `dvnWebLibrariesSecret` (GitHub PAT), then:

```yaml
- task: Bash@3
  displayName: 'Configure npm for GitHub Packages'
  inputs:
    targetType: 'inline'
    script: |
      echo "@devonenergyenterprise:registry=https://npm.pkg.github.com" >> .npmrc
      echo "//npm.pkg.github.com/:_authToken=$(dvnWebLibrariesSecret)" >> .npmrc
```
