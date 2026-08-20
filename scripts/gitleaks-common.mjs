import path from 'node:path'
import { fileURLToPath } from 'node:url'

// Pinned release: https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1
// Bump deliberately - the installer verifies the download against the
// official checksums file published alongside this same release tag.
export const GITLEAKS_VERSION = '8.30.1'

export const REPO_ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
export const BIN_DIR = path.join(REPO_ROOT, '.gitleaks-bin')
export const IS_WINDOWS = process.platform === 'win32'
export const BIN_NAME = IS_WINDOWS ? 'gitleaks.exe' : 'gitleaks'
export const BIN_PATH = path.join(BIN_DIR, BIN_NAME)
export const VERSION_FILE = path.join(BIN_DIR, '.version')

const PLATFORM_ASSETS = {
  'darwin-x64': 'darwin_x64.tar.gz',
  'darwin-arm64': 'darwin_arm64.tar.gz',
  'linux-x64': 'linux_x64.tar.gz',
  'linux-arm64': 'linux_arm64.tar.gz',
  'win32-x64': 'windows_x64.zip',
  'win32-arm64': 'windows_arm64.zip',
}

export function assetName(version = GITLEAKS_VERSION) {
  const key = `${process.platform}-${process.arch}`
  const suffix = PLATFORM_ASSETS[key]
  if (!suffix) {
    throw new Error(
      `No gitleaks release asset mapped for platform "${key}". ` +
      `Supported: ${Object.keys(PLATFORM_ASSETS).join(', ')}`
    )
  }
  return `gitleaks_${version}_${suffix}`
}

export function releaseUrl(fileName, version = GITLEAKS_VERSION) {
  return `https://github.com/gitleaks/gitleaks/releases/download/v${version}/${fileName}`
}
