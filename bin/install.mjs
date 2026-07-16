#!/usr/bin/env node

import {
  readdirSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
  cpSync,
  rmSync,
  existsSync,
  statSync,
} from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILLS_SOURCE = join(__dirname, '..', 'skills');
const DEST_BASE = join(homedir(), '.claude', 'skills');
const VERSION_MARKER = join(DEST_BASE, '.pm-skills-version');

const COMMANDS = {
  install: 'Install skills to ~/.claude/skills/',
  update: 'Update installed skills to latest version',
  check: 'Check if update is available',
  help: 'Show this help message',
};

function getVersion() {
  const pkg = JSON.parse(
    readFileSync(join(__dirname, '..', 'package.json'), 'utf8')
  );
  return pkg.version;
}

function getInstalledVersion() {
  if (existsSync(VERSION_MARKER)) {
    return readFileSync(VERSION_MARKER, 'utf8').trim();
  }
  return null;
}

function listSkills() {
  return readdirSync(SKILLS_SOURCE).filter(
    (f) => !f.startsWith('.') && statSync(join(SKILLS_SOURCE, f)).isDirectory()
  );
}

function copySkills() {
  if (!existsSync(DEST_BASE)) {
    mkdirSync(DEST_BASE, { recursive: true });
  }

  const skills = listSkills();
  for (const skill of skills) {
    const src = join(SKILLS_SOURCE, skill);
    const dest = join(DEST_BASE, skill);

    // Remove existing (file or directory) before copying
    if (existsSync(dest)) {
      rmSync(dest, { recursive: true, force: true });
    }

    cpSync(src, dest, { recursive: true });
  }

  writeFileSync(VERSION_MARKER, getVersion());
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';

  switch (command) {
    case 'install':
    case 'update': {
      const version = getVersion();
      const installed = getInstalledVersion();
      const skills = listSkills();

      if (command === 'update' && !installed) {
        console.log('No existing installation found. Running install...\n');
      }

      if (command === 'install' && installed) {
        console.log(
          `Already installed (v${installed}). Running update...\n`
        );
      }

      console.log(`📦 pm-skills v${version}\n`);
      console.log('Skills:');

      for (const skill of skills) {
        console.log(`  ✓ ${skill}`);
      }

      copySkills();

      console.log(`\n✅ Installed to ${DEST_BASE}`);
      console.log('\nRestart your Claude Code session to load them.\n');
      break;
    }

    case 'check': {
      const version = getVersion();
      const installed = getInstalledVersion();

      console.log('\n📦 pm-skills\n');
      console.log(`  Package version:   ${version}`);
      console.log(
        `  Installed version: ${installed || 'not installed'}`
      );

      if (!installed) {
        console.log(
          '\n  Run: npx @sirryou/project-management install\n'
        );
      } else if (installed === version) {
        console.log('\n  ✅ Up to date.\n');
      } else {
        console.log(
          '\n  ⚠️  Update available. Run: npx @sirryou/project-management update\n'
        );
      }
      break;
    }

    case 'help':
    case '--help':
    case '-h':
    default: {
      console.log(`\n📦 pm-skills v${getVersion()}\n`);
      console.log(
        'Usage: npx @sirryou/project-management <command>\n'
      );
      console.log('Commands:');
      for (const [cmd, desc] of Object.entries(COMMANDS)) {
        console.log(`  ${cmd.padEnd(10)} ${desc}`);
      }
      console.log('');
      break;
    }
  }
}

main();
