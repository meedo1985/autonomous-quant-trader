// Verify one drand quicknet round against the chain bound by FP3
// (review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md, Rules 2 and 4).
// Usage: node verify.mjs <chain-info.json> <beacon.json> <expected round>
// Prints one JSON line; exit 0 only if every check passes.
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { fetchBeacon } from 'drand-client'

// drand-client exports verification only through fetchBeacon; an offline client
// serves the saved response, so drand's own verifyBeacon runs on it (no network).
async function verifyBeacon(info, beacon, round) {
  const client = {
    options: { disableBeaconVerification: false },
    chain: () => ({ info: async () => info }),
    get: async () => beacon,
  }
  try {
    await fetchBeacon(client, round)
    return true
  } catch {
    return false
  }
}

// Rule 2: the bound chain. The info file must match these, field by field.
const BOUND = {
  hash: '52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971',
  public_key: '83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a',
  schemeID: 'bls-unchained-g1-rfc9380',
  period: 3,
  genesis_time: 1692803367,
}

const [infoPath, beaconPath, roundArg] = process.argv.slice(2)
if (!infoPath || !beaconPath || !/^[1-9][0-9]*$/.test(roundArg ?? '')) {
  console.error('usage: node verify.mjs <chain-info.json> <beacon.json> <expected round>')
  process.exit(2)
}
const round = Number(roundArg)
const info = JSON.parse(readFileSync(infoPath, 'utf8'))
const raw = JSON.parse(readFileSync(beaconPath, 'utf8'))

const result = { round, chain_matches: true, signature: raw.signature ?? null }
for (const [k, v] of Object.entries(BOUND)) {
  if (info[k] !== v) result.chain_matches = false
}
// Rule 4: randomness = SHA-256 of the raw 48-byte signature, 64 lowercase hex;
// any randomness field in the response is ignored for the value used.
const sig = typeof raw.signature === 'string' && /^[0-9a-f]{96}$/.test(raw.signature)
  ? Buffer.from(raw.signature, 'hex') : null
result.randomness = sig ? createHash('sha256').update(sig).digest('hex') : null
result.response_randomness_differs = raw.randomness !== undefined && raw.randomness !== result.randomness
result.round_matches = raw.round === round
let verified = false
if (result.chain_matches && sig && result.round_matches) {
  verified = await verifyBeacon(BOUND, { round: raw.round, signature: raw.signature, randomness: result.randomness }, round)
}
result.signature_verifies = verified
result.ok = result.chain_matches && result.round_matches && verified
console.log(JSON.stringify(result))
process.exit(result.ok ? 0 : 1)
