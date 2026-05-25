// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Cross-platform helper CLI for excalibur-quest remediation orchestrations.
 * Zero-dependency, compatible with Windows, macOS, and Linux Node.js environments.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class QuestDB {
  constructor(dbDir) {
    this.dbDir = dbDir;
    if (!fs.existsSync(this.dbDir)) {
      fs.mkdirSync(this.dbDir, { recursive: true });
    }
    this.jsonDb = path.join(this.dbDir, 'quest_db.json');
    this.useDolt = this.checkDolt();
  }

  checkDolt() {
    try {
      execSync('dolt version', { stdio: 'ignore' });
      return true;
    } catch (e) {
      return false;
    }
  }

  loadQuest(issueId) {
    if (this.useDolt) {
      try {
        const query = `SELECT data FROM quests WHERE issue_id = '${issueId}'`;
        const res = execSync(`dolt sql -q "${query}" -r json`, { encoding: 'utf8' }).trim();
        if (res) {
          const rows = JSON.parse(res);
          if (rows && rows.rows && rows.rows.length > 0) {
            return JSON.parse(rows.rows[0].data);
          }
        }
      } catch (e) {
        console.error('Dolt load failed, falling back to JSON:', e.message);
      }
    }

    if (fs.existsSync(this.jsonDb)) {
      try {
        const data = JSON.parse(fs.readFileSync(this.jsonDb, 'utf8'));
        return data[issueId];
      } catch (e) {
        console.error('JSON load failed:', e.message);
      }
    }
    return null;
  }

  saveQuest(issueId, questData) {
    if (this.useDolt) {
      try {
        execSync('dolt sql -q "CREATE TABLE IF NOT EXISTS quests (issue_id VARCHAR(50) PRIMARY KEY, data TEXT)"', { stdio: 'ignore' });
        const escapedData = JSON.stringify(questData).replace(/'/g, "''");
        execSync(`dolt sql -q "REPLACE INTO quests (issue_id, data) VALUES ('${issueId}', '${escapedData}')"`, { stdio: 'ignore' });
        return;
      } catch (e) {
        console.error('Dolt write failed, falling back to JSON:', e.message);
      }
    }

    let data = {};
    if (fs.existsSync(this.jsonDb)) {
      try {
        data = JSON.parse(fs.readFileSync(this.jsonDb, 'utf8'));
      } catch (e) {}
    }
    data[issueId] = questData;
    try {
      fs.writeFileSync(this.jsonDb, JSON.stringify(data, null, 2), 'utf8');
    } catch (e) {
      console.error('JSON write failed:', e.message);
    }
  }
}

function acquireConcurrencySlot(lockDir, maxConcurrent = 3) {
  if (!fs.existsSync(lockDir)) {
    fs.mkdirSync(lockDir, { recursive: true });
  }

  while (true) {
    for (let i = 0; i < maxConcurrent; i++) {
      const lockPath = path.join(lockDir, `lock_${i}`);
      try {
        fs.mkdirSync(lockPath);
        console.error(`Acquired Roundtable seat ${i + 1} of ${maxConcurrent}`);
        return () => {
          try {
            fs.rmdirSync(lockPath);
          } catch (e) {}
        };
      } catch (err) {
        if (err.code !== 'EEXIST') {
          throw err;
        }
      }
    }
    console.error('Roundtable seats full. Waiting for slot...');
    const start = Date.now();
    while (Date.now() - start < 1000) {}
  }
}

function printHelpAndExit() {
  console.log(`
Excalibur Quest remediation coordinator.

Usage: node quest_helper.js <command> [options]

Commands:
  init   Initialize remediation beads database
  sync   Sync local beads state to GitHub
  close  Close beads and finalize quest

Options:
  --issue-id      Target GitHub issue number (required)
  --reviews-path  Path to JSON review findings file
  --repo-owner    GitHub repository owner (sync only)
  --repo-name     GitHub repository name (sync only)
  --output        Output JSON status file path (required)
`);
  process.exit(1);
}

function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  const command = argv[0];
  if (!command || !['init', 'sync', 'close'].includes(command)) {
    printHelpAndExit();
  }
  args.command = command;

  for (let i = 1; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2).replace(/-([a-z])/g, (g) => g[1].toUpperCase());
      const val = argv[i + 1];
      if (val && !val.startsWith('--')) {
        args[key] = val;
        i++;
      } else {
        args[key] = true;
      }
    }
  }

  if (!args.issueId || !args.output) {
    console.error('Error: --issue-id and --output are required.\n');
    printHelpAndExit();
  }
  return args;
}

function runInit(args, db) {
  let beads = [];
  if (args.reviewsPath && fs.existsSync(args.reviewsPath)) {
    try {
      const reviews = JSON.parse(fs.readFileSync(args.reviewsPath, 'utf8'));
      if (reviews.findings) {
        beads = reviews.findings.map((r, idx) => ({
          id: `bead-${idx + 1}`,
          title: r.title || `Remediation item ${idx + 1}`,
          severity: r.severity || 'MEDIUM',
          status: 'PENDING'
        }));
      }
    } catch (e) {
      console.error('Failed to load reviews path:', e.message);
    }
  }

  if (beads.length === 0) {
    beads = [
      { id: 'bead-1', title: 'Audit source for security vulnerabilities', severity: 'CRITICAL', status: 'PENDING' },
      { id: 'bead-2', title: 'Verify tokio async I/O migrations', severity: 'HIGH', status: 'PENDING' },
      { id: 'bead-3', title: 'Check static analyzer schemas', severity: 'MEDIUM', status: 'PENDING' }
    ];
  }

  const questData = {
    issue_id: args.issueId,
    status: 'ACTIVE',
    beads: beads,
    created_at: Date.now() / 1000
  };
  db.saveQuest(args.issueId, questData);
  return questData;
}

function runSync(args, db) {
  const quest = db.loadQuest(args.issueId);
  if (!quest) {
    console.error(`Error: Quest for issue ${args.issueId} not initialized.`);
    process.exit(1);
  }

  if (!args.repoOwner || !args.repoName) {
    console.error('Error: --repo-owner and --repo-name are required for sync.');
    process.exit(1);
  }

  console.error(`Syncing beads status to GitHub repo ${args.repoOwner}/${args.repoName}...`);

  let commentBody = `### Excalibur Quest Sync Update\n\n**Quest Status:** ${quest.status}\n\n**Beads Progress:**\n`;
  for (const b of quest.beads || []) {
    const statusBox = b.status === 'COMPLETED' ? '[x]' : '[ ]';
    commentBody += `- ${statusBox} **${b.id}**: ${b.title} (${b.severity})\n`;
  }

  try {
    execSync(`gh issue comment ${args.issueId} --repo ${args.repoOwner}/${args.repoName} --body "${commentBody.replace(/"/g, '\\"')}"`, { stdio: 'pipe' });
    console.error('Successfully synced comment to GitHub.');
    quest.github_synced = true;
  } catch (e) {
    console.error('Warning: gh CLI sync failed (continuing locally):', e.message);
    quest.github_synced = false;
  }

  db.saveQuest(args.issueId, quest);
  return quest;
}

function runClose(args, db) {
  const quest = db.loadQuest(args.issueId);
  if (!quest) {
    console.error(`Error: Quest for issue ${args.issueId} not found.`);
    process.exit(1);
  }

  quest.status = 'COMPLETED';
  if (quest.beads) {
    quest.beads.forEach(b => b.status = 'COMPLETED');
  }

  db.saveQuest(args.issueId, quest);
  console.error(`Successfully closed quest ${args.issueId}.`);
  return quest;
}

function main() {
  const args = parseArgs();

  let workspaceRoot;
  try {
    workspaceRoot = execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim();
  } catch (e) {
    workspaceRoot = process.cwd();
  }

  const lockDir = path.join(workspaceRoot, '.excalibur_locks');
  const cleanup = acquireConcurrencySlot(lockDir);

  // Register cleanup exit hooks
  process.on('exit', cleanup);
  process.on('SIGINT', () => { cleanup(); process.exit(); });
  process.on('SIGTERM', () => { cleanup(); process.exit(); });

  try {
    const db = new QuestDB(path.join(workspaceRoot, '.excalibur_quest'));
    let result;

    if (args.command === 'init') {
      result = runInit(args, db);
    } else if (args.command === 'sync') {
      result = runSync(args, db);
    } else if (args.command === 'close') {
      result = runClose(args, db);
    }

    try {
      fs.writeFileSync(args.output, JSON.stringify(result, null, 2), 'utf8');
      console.log(`Success! Data written to: ${args.output}`);
    } catch (e) {
      console.error(`Error writing output to ${args.output}:`, e.message);
      process.exit(1);
    }
  } finally {
    cleanup();
  }
}

main();
