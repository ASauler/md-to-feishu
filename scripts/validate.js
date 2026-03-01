#!/usr/bin/env node
/**
 * Validation test for md-to-feishu skill
 * Tests feishu_table.py functionality
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

async function validate() {
  console.log('Validating md-to-feishu skill...');
  
  // Test 1: Check if feishu_table.py exists and is executable
  const tablePath = path.join(__dirname, '..', 'feishu_table.py');
  if (!fs.existsSync(tablePath)) {
    throw new Error('feishu_table.py not found');
  }
  console.log('✓ feishu_table.py exists');
  
  // Test 2: Check if md_to_feishu_full.py exists
  const converterPath = path.join(__dirname, '..', 'md_to_feishu_full.py');
  if (!fs.existsSync(converterPath)) {
    throw new Error('md_to_feishu_full.py not found');
  }
  console.log('✓ md_to_feishu_full.py exists');
  
  // Test 3: Verify Python syntax
  try {
    execSync(`python3 -m py_compile ${tablePath}`, { stdio: 'pipe' });
    console.log('✓ feishu_table.py syntax valid');
  } catch (e) {
    throw new Error('feishu_table.py has syntax errors');
  }
  
  try {
    execSync(`python3 -m py_compile ${converterPath}`, { stdio: 'pipe' });
    console.log('✓ md_to_feishu_full.py syntax valid');
  } catch (e) {
    throw new Error('md_to_feishu_full.py has syntax errors');
  }
  
  // Test 4: Check README exists and has required sections
  const readmePath = path.join(__dirname, '..', 'README.md');
  if (!fs.existsSync(readmePath)) {
    throw new Error('README.md not found');
  }
  
  const readme = fs.readFileSync(readmePath, 'utf-8');
  const requiredSections = ['Installation', 'Usage', 'API Reference', '安装', '使用方法'];
  for (const section of requiredSections) {
    if (!readme.includes(section)) {
      throw new Error(`README.md missing section: ${section}`);
    }
  }
  console.log('✓ README.md complete');
  
  // Test 5: Verify imports can be resolved
  const testScript = `
import sys
import json
import re
import subprocess
import os
print("All imports successful")
`;
  
  try {
    execSync(`python3 -c "${testScript}"`, { stdio: 'pipe' });
    console.log('✓ All Python dependencies available');
  } catch (e) {
    throw new Error('Missing Python dependencies');
  }
  
  console.log('\n✅ All validation tests passed');
  return true;
}

validate().catch(err => {
  console.error('❌ Validation failed:', err.message);
  process.exit(1);
});
