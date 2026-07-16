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

const AGENTS = {
  claude: {
    name: 'Claude Code',
    dest: join(homedir(), '.claude', 'skills'),
  },
  cursor: {
    name: 'Cursor',
    dest: join(homedir(), '.cursor', 'skills'),
  },
  codex: {
    name: 'Codex',
    dest: join(homedir(), '.codex', 'skills'),
  },
  gemini: {
    name: 'Gemini CLI',
    dest: join(homedir(), '.gemini', 'skills'),
  },
};

const COMMANDS = {
  install: 'Install skills (--agent to target specific agent)',
  update: 'Update installed skills to latest version',
  check: 'Check if update is available',
  agents: 'List supported agents and their paths',
  help: 'Show this help message',
};

function getVersion() {
  const pkg = JSON.parse(
    readFileSync(join(__dirname, '..', 'package.json'), 'utf8')
  );
  return pkg.version;
}

function getInstalledVersion(dest) {
  const marker = join(dest, '.pm-skills-version');
  if (existsSync(marker)) {
    return readFileSync(marker, 'utf8').trim();
  }
  return null;
}

function listSkills() {
  return readdirSync(SKILLS_SOURCE).filter(
    (f) =>
      !f.startsWith('.') && statSync(join(SKILLS_SOURCE, f)).isDirectory()
  );
}

function copySkills(dest) {
  if (!existsSync(dest)) {
    mkdirSync(dest, { recursive: true });
  }

  const skills = listSkills();
  for (const skill of skills) {
    const src = join(SKILLS_SOURCE, skill);
    const skillDest = join(dest, skill);

    if (existsSync(skillDest)) {
      rmSync(skillDest, { recursive: true, force: true });
    }

    cpSync(src, skillDest, { recursive: true });
  }

  writeFileSync(join(dest, '.pm-skills-version'), getVersion());
}

function parseArgs(args) {
  const result = { command: 'help', agents: [] };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--agent' && args[i + 1]) {
      result.agents.push(args[++i]);
    } else if (!args[i].startsWith('-')) {
      result.command = args[i];
    }
  }

  return result;
}

function main() {
  const { command, agents: targetAgents } = parseArgs(process.argv.slice(2));

  // Default to all agents if none specified
  const targets =
    targetAgents.length > 0
      ? targetAgents
      : Object.keys(AGENTS);

  switch (command) {
    case 'install':
    case 'update': {
      const version = getVersion();
      const skills = listSkills();

      console.log(`\n📦 skill-library v${version}\n`);
      console.log('Skills:');
      for (const skill of skills) {
        console.log(`  ✓ ${skill}`);
      }

      console.log('\nInstalling to:');

      for (const agentKey of targets) {
        const agent = AGENTS[agentKey];
        if (!agent) {
          console.log(`  ⚠️  Unknown agent: ${agentKey}`);
          continue;
        }

        const installed = getInstalledVersion(agent.dest);

        if (command === 'install' && installed) {
          console.log(
            `\n  ${agent.name} (already installed v${installed}, updating...)`
          );
        } else {
          console.log(`\n  ${agent.name}`);
        }

        copySkills(agent.dest);
        console.log(`  ✅ ${agent.dest}`);
      }

      console.log('\nRestart your agent session to load skills.\n');
      break;
    }

    case 'check': {
      const version = getVersion();

      console.log(`\n📦 skill-library v${version}\n`);

      for (const agentKey of targets) {
        const agent = AGENTS[agentKey];
        if (!agent) continue;

        const installed = getInstalledVersion(agent.dest);
        const status = !installed
          ? 'not installed'
          : installed === version
            ? '✅ up to date'
            : `⚠️  v${installed} → v${version} available`;

        console.log(`  ${agent.name.padEnd(12)} ${status}`);
      }

      console.log('');
      break;
    }

    case 'agents': {
      console.log('\nSupported agents:\n');
      for (const [key, agent] of Object.entries(AGENTS)) {
        console.log(`  ${key.padEnd(10)} ${agent.name.padEnd(14)} → ${agent.dest}`);
      }
      console.log('\nUsage: npx @sirryou/skill-library install --agent claude\n');
      break;
    }

    case 'help':
    case '--help':
    case '-h':
    default: {
      console.log(`\n📦 skill-library v${getVersion()}\n`);
      console.log(
        'Usage: npx @sirryou/skill-library <command> [--agent <name>]\n'
      );
      console.log('Commands:');
      for (const [cmd, desc] of Object.entries(COMMANDS)) {
        console.log(`  ${cmd.padEnd(10)} ${desc}`);
      }
      console.log('\nAgents:');
      for (const [key, agent] of Object.entries(AGENTS)) {
        console.log(`  ${key.padEnd(10)} ${agent.name}`);
      }
      console.log(
        '\nIf no --agent specified, installs to all agents.\n'
      );
      break;
    }
  }
}

main();
