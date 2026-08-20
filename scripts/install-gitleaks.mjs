#!/usr/bin/env node
// Downloads the official gitleaks binary (github.com/gitleaks/gitleaks releases)
// and verifies it against the checksums file published in that same release,
// rather than depending on an unofficial npm-packaged wrapper.
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync, chmodSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import os from 'node:os'
import path from 'node:path'
import {
  GITLEAKS_VERSION,
  BIN_DIR,
  BIN_NAME,
  BIN_PATH,
  VERSION_FILE,
  assetName,
  releaseUrl,
} from './gitleaks-common.mjs'

async function alreadyInstalled() {
  if (!existsSync(BIN_PATH) || !existsSync(VERSION_FILE)) return false
  return readFileSync(VERSION_FILE, 'utf8').trim() === GITLEAKS_VERSION
}

async function download(url) {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to download ${url}: ${res.status} ${res.statusText}`)
  return Buffer.from(await res.arrayBuffer())
}

function sha256(buf) {
  return createHash('sha256').update(buf).digest('hex')
}

function expectedChecksum(checksumsText, fileName) {
  const line = checksumsText.split('\n').find((l) => l.trim().endsWith(fileName))
  if (!line) throw new Error(`No checksum entry found for ${fileName}`)
  return line.trim().split(/\s+/)[0]
}

async function main() {
  if (await alreadyInstalled()) {
    console.log(`[gitleaks] v${GITLEAKS_VERSION} already installed at ${BIN_PATH}`)
    return
  }

  const asset = assetName()
  const assetUrl = releaseUrl(asset)
  const checksumsUrl = releaseUrl(`gitleaks_${GITLEAKS_VERSION}_checksums.txt`)

  console.log(`[gitleaks] downloading ${asset} ...`)
  const [assetBuf, checksumsBuf] = await Promise.all([download(assetUrl), download(checksumsUrl)])

  const expected = expectedChecksum(checksumsBuf.toString('utf8'), asset)
  const actual = sha256(assetBuf)
  if (expected !== actual) {
    throw new Error(
      `[gitleaks] checksum mismatch for ${asset}\n  expected: ${expected}\n  actual:   ${actual}\n` +
      'Aborting install - the download may be corrupted or tampered with.'
    )
  }

  const tmpDir = mkdtempSync(path.join(os.tmpdir(), 'gitleaks-install-'))
  const archivePath = path.join(tmpDir, asset)
  writeFileSync(archivePath, assetBuf)

  if (asset.endsWith('.zip')) {
    // Don't rely on `tar` for zip: on Windows, whichever `tar` wins PATH
    // resolution matters - Git for Windows ships a GNU tar that can't
    // extract zip, unlike the system bsdtar in System32. PowerShell's
    // Expand-Archive is always present and unambiguous.
    execFileSync(
      'powershell.exe',
      ['-NoProfile', '-NonInteractive', '-Command', `Expand-Archive -LiteralPath '${archivePath}' -DestinationPath '${tmpDir}' -Force`],
      { stdio: 'inherit' }
    )
  } else {
    // Run with cwd set and a bare filename (not an absolute path) - tar on
    // Windows misreads a leading "C:\..." drive letter as a "host:path"
    // remote-archive spec otherwise. Not an issue here since this branch
    // only handles .tar.gz (macOS/Linux), but kept consistent regardless.
    execFileSync('tar', ['-xf', asset], { cwd: tmpDir, stdio: 'inherit' })
  }

  const extractedBin = path.join(tmpDir, BIN_NAME)
  if (!existsSync(extractedBin)) {
    throw new Error(`[gitleaks] expected binary "${BIN_NAME}" not found after extracting ${asset}`)
  }

  mkdirSync(BIN_DIR, { recursive: true })
  writeFileSync(BIN_PATH, readFileSync(extractedBin))
  if (process.platform !== 'win32') chmodSync(BIN_PATH, 0o755)
  writeFileSync(VERSION_FILE, GITLEAKS_VERSION)

  rmSync(tmpDir, { recursive: true, force: true })
  console.log(`[gitleaks] installed v${GITLEAKS_VERSION} to ${BIN_PATH}`)
}

main().catch((err) => {
  console.error(err.message ?? err)
  process.exit(1)
})
