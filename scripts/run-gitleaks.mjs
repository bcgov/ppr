#!/usr/bin/env node
import { existsSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { BIN_PATH, GITLEAKS_VERSION, REPO_ROOT } from './gitleaks-common.mjs'

if (!existsSync(BIN_PATH)) {
  console.error(
    `[gitleaks] binary not found at ${BIN_PATH}.\n` +
    `Run "pnpm install" to install gitleaks v${GITLEAKS_VERSION}, then try again.`
  )
  process.exit(1)
}

const result = spawnSync(
  BIN_PATH,
  ['git', '--staged', '--redact', '--exit-code=1', REPO_ROOT],
  { stdio: 'inherit' }
)

process.exit(result.status ?? 1)
