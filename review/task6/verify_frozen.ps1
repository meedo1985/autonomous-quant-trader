$ErrorActionPreference = 'Stop'

$root = (Get-Location).Path
$baseline = Get-Content -LiteralPath 'review/task1/protected-before.json' -Raw |
    ConvertFrom-Json
$expected = @{}
foreach ($entry in $baseline) {
    $expected[$entry.path] = [string]$entry.sha256
}
if ($expected.Count -ne 28) {
    throw "baseline count $($expected.Count)"
}

$actual = @()
foreach ($area in @('docs', 'protocols', 'schemas', 'specs')) {
    $actual += Get-ChildItem -LiteralPath $area -File -Recurse |
        Where-Object { $_.FullName -ne (Join-Path $root 'docs\README.md') } |
        ForEach-Object { $_.FullName.Substring($root.Length + 1).Replace('\', '/') }
}
$actual += @('FROZEN_HASHES.json', 'FROZEN_HASHES.json.sha256')
if (@(Compare-Object @($expected.Keys | Sort-Object) @($actual | Sort-Object)).Count) {
    throw 'protected inventory mismatch'
}
foreach ($path in $expected.Keys) {
    $digest = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $expected[$path]) {
        throw "baseline mismatch $path"
    }
}

$sidecars = @($actual | Where-Object { $_.EndsWith('.sha256') })
if ($sidecars.Count -ne 14) {
    throw "sidecar count $($sidecars.Count)"
}
foreach ($path in $sidecars) {
    $parts = (Get-Content -LiteralPath $path -Raw).Trim() -split '\s+', 2
    $parent = Split-Path $path
    $target = if ($parent) { Join-Path $parent $parts[1] } else { $parts[1] }
    $digest = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $parts[0]) {
        throw "sidecar mismatch $path"
    }
}

$constitution = Get-Content -LiteralPath 'docs/RESEARCH_CONSTITUTION.md' -Raw
$match = [regex]::Match(
    $constitution,
    '(\*\*Content hash:\*\* `)([0-9a-f]{64})(`)'
)
if (-not $match.Success) {
    throw 'constitution hash field missing'
}
$canonical = $constitution.Substring(0, $match.Groups[2].Index) +
    $constitution.Substring($match.Groups[2].Index + $match.Groups[2].Length)
$sha = [System.Security.Cryptography.SHA256]::Create()
$utf8 = [System.Text.UTF8Encoding]::new($false)
$contentHash = [Convert]::ToHexString(
    $sha.ComputeHash($utf8.GetBytes($canonical))
).ToLowerInvariant()
if ($contentHash -ne $match.Groups[2].Value) {
    throw 'constitution self-hash mismatch'
}

$manifest = Get-Content -LiteralPath 'FROZEN_HASHES.json' -Raw | ConvertFrom-Json
$bindings = @{
    protocol_file_sha256 = 'protocols/protocol_v1.yaml'
    cost_model_sha256 = 'specs/COST_MODEL_v1.md'
    feature_factory_sha256 = 'specs/FEATURE_FACTORY_v1.md'
    benchmark_set_sha256 = 'specs/CANONICAL_BENCHMARKS_v1.md'
    backtester_spec_sha256 = 'specs/BACKTESTER_SPEC_v1.md'
    threat_model_sha256 = 'docs/THREAT_MODEL_v1.md'
    hash_canonicalization_spec_sha256 = 'schemas/HASH_CANONICALIZATION_v1.md'
}
if (
    $manifest.release -ne 'v1.0' -or
    $manifest.status -ne 'FROZEN' -or
    $manifest.constitution_content_hash -ne $contentHash
) {
    throw 'manifest metadata mismatch'
}
foreach ($field in $bindings.Keys) {
    $digest = (Get-FileHash -LiteralPath $bindings[$field] -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($manifest.$field -ne $digest) {
        throw "manifest binding mismatch $field"
    }
}

$protocol = Get-Content -LiteralPath 'protocols/protocol_v1.yaml' -Raw
$protocolBindings = @{
    constitution_hash = $contentHash
    cost_model_hash = $manifest.cost_model_sha256
    feature_factory_hash = $manifest.feature_factory_sha256
    benchmark_set_hash = $manifest.benchmark_set_sha256
    backtester_spec_hash = $manifest.backtester_spec_sha256
    threat_model_hash = $manifest.threat_model_sha256
    hash_canonicalization_spec_hash = $manifest.hash_canonicalization_spec_sha256
}
foreach ($field in $protocolBindings.Keys) {
    $pattern = '(?m)^' + [regex]::Escape($field) +
        ':\s*"?([0-9a-f]{64})"?\s*$'
    $binding = [regex]::Match($protocol, $pattern)
    if (-not $binding.Success -or $binding.Groups[1].Value -ne $protocolBindings[$field]) {
        throw "protocol binding mismatch $field"
    }
}
foreach ($field in @('cost_model_hash', 'feature_factory_hash', 'benchmark_set_hash')) {
    $occurrences = [regex]::Matches(
        $protocol,
        [regex]::Escape($protocolBindings[$field])
    ).Count
    if ($occurrences -lt 2) {
        throw "nested protocol binding missing $field"
    }
}

Write-Output 'PASS: 28/28 trusted bytes and exact inventory; 14/14 sidecars'
Write-Output 'PASS: Constitution self-hash; 7/7 manifest and protocol bindings'
Write-Output 'PASS: nested cost-model, feature-factory, and benchmark bindings'
