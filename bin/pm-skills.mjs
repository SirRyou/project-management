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
    dest: (ws) => (ws ? join(process.cwd(), '.claude', 'skills') : join(homedir(), '.claude', 'skills')),
  },
  cursor: {
    name: 'Cursor',
    dest: (ws) => (ws ? join(process.cwd(), '.cursor', 'skills') : join(homedir(), '.cursor', 'skills')),
  },
  codex: {
    name: 'Codex',
    dest: (ws) => (ws ? join(process.cwd(), '.codex', 'skills') : join(homedir(), '.codex', 'skills')),
    agentsDest: (ws) => (ws ? join(process.cwd(), '.codex', 'agents') : join(homedir(), '.codex', 'agents')),
    subagentFormat: 'codex-toml',
  },
  gemini: {
    name: 'Gemini CLI',
    dest: (ws) => (ws ? join(process.cwd(), '.gemini', 'skills') : join(homedir(), '.gemini', 'skills')),
  },
  antigravity: {
    name: 'Antigravity',
    dest: (ws) => (ws ? join(process.cwd(), '.agents', 'skills') : join(homedir(), '.gemini', 'antigravity-cli', 'skills')),
    agentsDest: (ws) => (ws ? join(process.cwd(), '.agents', 'subagents') : join(homedir(), '.gemini', 'antigravity-cli', 'subagents')),
    rulesDest: (ws) => (ws ? join(process.cwd(), '.agents', 'rules') : null),
    subagentFormat: 'antigravity-json',
  },
};

const COMMANDS = {
  install: 'Install skills (--agent <name>, --workspace for project-local)',
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

/**
 * Provision platform-specific subagents for runtimes like Codex and Antigravity.
 */
function provisionSubagents(agentKey, agentConfig, isWorkspace) {
  if (!agentConfig.agentsDest) return [];

  const targetDir = agentConfig.agentsDest(isWorkspace);
  if (!existsSync(targetDir)) {
    mkdirSync(targetDir, { recursive: true });
  }

  const skills = listSkills();
  const provisioned = [];

  for (const skill of skills) {
    const manifestPath = join(SKILLS_SOURCE, skill, 'subagents.json');
    if (!existsSync(manifestPath)) continue;

    try {
      const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
      if (!Array.isArray(manifest)) continue;

      for (const agent of manifest) {
        const specFilePath = join(SKILLS_SOURCE, skill, agent.spec_file);
        let instructions = '';
        if (existsSync(specFilePath)) {
          instructions = readFileSync(specFilePath, 'utf8').trim();
        }

        if (agentConfig.subagentFormat === 'codex-toml' && agent.codex) {
          // Schema from OpenAI Codex docs:
          // name, description, developer_instructions (required)
          // model, model_reasoning_effort, sandbox_mode (optional)
          const tomlParts = [
            `name = "${agent.name}"`,
            `description = "${agent.description.replace(/"/g, '\\"')}"`,
            `model = "${agent.codex.model || 'gpt-5.6'}"`,
            `model_reasoning_effort = "${agent.codex.model_reasoning_effort || 'medium'}"`,
          ];

          if (agent.codex.sandbox_mode) {
            tomlParts.push(`sandbox_mode = "${agent.codex.sandbox_mode}"`);
          }

          // Format multi-line string safely for TOML
          const cleanInstructions = instructions.replace(/"""/g, "'''");
          tomlParts.push(`developer_instructions = """\n${cleanInstructions}\n"""\n`);

          const tomlContent = tomlParts.join('\n');
          const outFile = join(targetDir, `${agent.name}.toml`);
          writeFileSync(outFile, tomlContent, 'utf8');
          provisioned.push(`${agent.name}.toml`);
        } else if (agentConfig.subagentFormat === 'antigravity-json' && agent.antigravity) {
          // Schema for Antigravity custom subagents:
          // name, description, system_prompt, model, enable_write_tools, enable_subagent_tools, enable_mcp_tools
          const agyConfig = {
            name: agent.name,
            description: agent.description,
            system_prompt: instructions,
            model: agent.antigravity.model || 'inherit',
            enable_write_tools: Boolean(agent.antigravity.enable_write_tools),
            enable_subagent_tools: Boolean(agent.antigravity.enable_subagent_tools),
            enable_mcp_tools: Boolean(agent.antigravity.enable_mcp_tools),
          };

          const outFile = join(targetDir, `${agent.name}.json`);
          writeFileSync(outFile, JSON.stringify(agyConfig, null, 2), 'utf8');
          provisioned.push(`${agent.name}.json`);
        }
      }

      // If Antigravity workspace mode, also emit a workspace rule to auto-discover them
      if (agentConfig.subagentFormat === 'antigravity-json' && agentConfig.rulesDest && isWorkspace) {
        const rulesDir = agentConfig.rulesDest(isWorkspace);
        if (!existsSync(rulesDir)) {
          mkdirSync(rulesDir, { recursive: true });
        }
        const ruleContent = `---
trigger: model_decision
description: Load and register deep-plan specialist subagents when executing deep-plan workflows
---

# Deep Plan Subagent Discovery

The workspace contains specialized deep-plan subagent definitions in \`.agents/subagents/\`.
When executing deep-plan workflows (such as during Phase 3 planning or Phase 4 swarm execution),
ensure these custom subagents are defined in your runtime session using \`define_subagent\`
if they have not already been registered.
`;
        writeFileSync(join(rulesDir, 'deep-plan-subagents.md'), ruleContent, 'utf8');
      }
    } catch (err) {
      console.error(`  ⚠️ Failed to parse subagents for skill ${skill}:`, err.message);
    }
  }

  return provisioned;
}

function parseArgs(args) {
  const result = { command: 'help', agents: [], workspace: false };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--agent' && args[i + 1]) {
      result.agents.push(args[++i]);
    } else if (args[i] === '--workspace' || args[i] === '-w') {
      result.workspace = true;
    } else if (!args[i].startsWith('-')) {
      result.command = args[i];
    }
  }

  return result;
}

function main() {
  const { command, agents: targetAgents, workspace } = parseArgs(process.argv.slice(2));

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

      console.log(`\nInstalling (${workspace ? 'Workspace Project' : 'User Global'}):`);

      for (const agentKey of targets) {
        const agent = AGENTS[agentKey];
        if (!agent) {
          console.log(`  ⚠️  Unknown agent: ${agentKey}`);
          continue;
        }

        const dest = agent.dest(workspace);
        const installed = getInstalledVersion(dest);

        if (command === 'install' && installed) {
          console.log(
            `\n  ${agent.name} (already installed v${installed}, updating...)`
          );
        } else {
          console.log(`\n  ${agent.name}`);
        }

        copySkills(dest);
        console.log(`  ✅ Skills: ${dest}`);

        // Provision native subagents for Codex, Antigravity, etc.
        const provisioned = provisionSubagents(agentKey, agent, workspace);
        if (provisioned.length > 0) {
          const agentsDir = agent.agentsDest(workspace);
          console.log(`  🤖 Subagents (${provisioned.length}): ${agentsDir}`);
          for (const item of provisioned) {
            console.log(`     • ${item}`);
          }
        }
      }

      console.log('\nRestart your agent session to load skills and subagents.\n');
      break;
    }

    case 'check': {
      const version = getVersion();

      console.log(`\n📦 skill-library v${version}\n`);

      for (const agentKey of targets) {
        const agent = AGENTS[agentKey];
        if (!agent) continue;

        const dest = agent.dest(workspace);
        const installed = getInstalledVersion(dest);
        const status = !installed
          ? 'not installed'
          : installed === version
            ? '✅ up to date'
            : `⚠️  v${installed} → v${version} available`;

        console.log(`  ${agent.name.padEnd(14)} ${status}`);
      }

      console.log('');
      break;
    }

    case 'agents': {
      console.log('\nSupported agents:\n');
      for (const [key, agent] of Object.entries(AGENTS)) {
        const dest = agent.dest(workspace);
        const subagentsNote = agent.agentsDest ? ` [+ subagents → ${agent.agentsDest(workspace)}]` : '';
        console.log(`  ${key.padEnd(12)} ${agent.name.padEnd(14)} → ${dest}${subagentsNote}`);
      }
      console.log('\nUsage: npx @sirryou/skill-library install --agent codex [--workspace]\n');
      break;
    }

    case 'help':
    case '--help':
    case '-h':
    default: {
      console.log(`\n📦 skill-library v${getVersion()}\n`);
      console.log(
        'Usage: npx @sirryou/skill-library <command> [--agent <name>] [--workspace]\n'
      );
      console.log('Commands:');
      for (const [cmd, desc] of Object.entries(COMMANDS)) {
        console.log(`  ${cmd.padEnd(10)} ${desc}`);
      }
      console.log('\nAgents:');
      for (const [key, agent] of Object.entries(AGENTS)) {
        console.log(`  ${key.padEnd(12)} ${agent.name}`);
      }
      console.log('\nFlags:');
      console.log('  --workspace, -w   Install to current project directory instead of home directory');
      console.log('  --agent <name>    Target specific agent (e.g. codex, antigravity, claude, cursor, gemini)\n');
      break;
    }
  }
}

main();
