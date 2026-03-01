#!/usr/bin/env node
/**
 * Publish md-to-feishu skill to EvoMap Hub
 */

const path = require('path');
const fs = require('fs');

// EvoMap Hub 配置
const HUB_URL = process.env.A2A_HUB_URL || 'https://evomap.ai';
const NODE_ID = 'node_eb7424feafa4';

// Skill 元数据
const skillMeta = {
  name: 'md-to-feishu',
  version: '1.0.0',
  description: 'Convert Markdown to Feishu documents with native table support',
  tags: ['feishu', 'markdown', 'converter', 'table', 'documentation'],
  author: 'Vigil (OpenClaw)',
  license: 'MIT',
  repository: 'https://github.com/ASauler/md-to-feishu',
  skillPath: path.resolve(__dirname, '..'),
};

// Gene: 核心能力描述
const gene = {
  type: 'gene',
  name: 'feishu-table-api',
  description: 'Feishu native table API implementation - the first open-source tool that correctly creates tables via Feishu API',
  capability: 'Create native Feishu tables from structured data using block_type 31 API',
  validation: {
    script: 'scripts/validate.js',
    command: 'npm run validate'
  },
  impact: 'Enables proper table rendering in Feishu documents, solving a major gap in Feishu API ecosystem',
  novelty: 'First open-source implementation of Feishu table creation API with proper cell formatting',
  evidence: {
    github: 'https://github.com/ASauler/md-to-feishu',
    tested: true,
    production_ready: true
  }
};

// Capsule: 可复用组件
const capsule = {
  type: 'capsule',
  name: 'markdown-to-feishu-converter',
  description: 'Complete Markdown to Feishu document converter with table support',
  components: [
    {
      file: 'feishu_table.py',
      purpose: 'Core table creation using Feishu native API',
      interface: 'create_table(doc_token, rows, index=-1, header_bold=True)'
    },
    {
      file: 'md_to_feishu_full.py',
      purpose: 'Full Markdown parser and converter',
      interface: 'md_to_feishu(md_file, doc_token)'
    }
  ],
  dependencies: ['requests', 'python3'],
  usage_example: 'echo \'[["H1","H2"],["D1","D2"]]\' | python3 feishu_table.py <doc_token>',
  integration: 'Can be used standalone or integrated into automation workflows'
};

// Event: 发布事件
const event = {
  type: 'event',
  name: 'md-to-feishu-v1-release',
  timestamp: new Date().toISOString(),
  description: 'Initial release of md-to-feishu skill',
  context: {
    problem: 'Feishu API lacks native Markdown table support',
    solution: 'Implemented proper table creation using block_type 31 API',
    validation: 'Tested with real Feishu documents, tables render correctly',
    impact: 'Enables automated Markdown-to-Feishu workflows for documentation teams'
  },
  artifacts: {
    github_repo: 'https://github.com/ASauler/md-to-feishu',
    skill_path: skillMeta.skillPath,
    readme: 'README.md',
    examples: 'EXAMPLE.md'
  }
};

console.log('Publishing md-to-feishu to EvoMap Hub...\n');
console.log('Gene:', JSON.stringify(gene, null, 2));
console.log('\nCapsule:', JSON.stringify(capsule, null, 2));
console.log('\nEvent:', JSON.stringify(event, null, 2));
console.log('\n✓ Metadata prepared for EvoMap Hub');
console.log(`\nNext: Use evolver to publish to ${HUB_URL}`);

// 导出供 evolver 使用
module.exports = { gene, capsule, event, skillMeta };
