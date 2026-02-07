#!/usr/bin/env node

/**
 * Complete Test of Skills Implementation
 */

const SkillsImplementation = require('./skills_implementation_fixed.js');

async function runCompleteTest() {
  console.log('=== Complete Skills Test ===\n');

  const skills = new SkillsImplementation();

  const testResults = {};

  // Test each skill
  const skillsToTest = [
    { name: 'sp.specify', args: { name: 'Test Feature', description: 'Test feature description' } },
    { name: 'sp.plan', args: {} },
    { name: 'sp.tasks', args: {} },
    { name: 'sp.constitution', args: { principles: ['Test principle 1', 'Test principle 2'] } },
    { name: 'sp.clarify', args: {} },
    { name: 'sp.checklist', args: {} },
    { name: 'sp.analyze', args: {} },
    { name: 'sp.adr', args: { title: 'Test ADR', decision: 'Test decision' } },
    { name: 'sp.phr', args: { prompt: 'Test prompt', response: 'Test response' } },
    { name: 'sp.reverse-engineer', args: {} },
    { name: 'sp.taskstoissues', args: {} },
    { name: 'sp.git.commit_pr', args: { message: 'Test commit' } }
  ];

  for (const { name, args } of skillsToTest) {
    console.log(`Testing ${name}...`);
    try {
      const result = skills.executeSkill(name, args);
      testResults[name] = result.success;
      console.log(`  ${result.success ? '✓' : '✗'} ${name}: ${result.success ? 'PASS' : 'FAIL'}`);
      if (!result.success) {
        console.log(`    Error: ${result.error}`);
      }
    } catch (error) {
      testResults[name] = false;
      console.log(`  ✗ ${name}: FAIL - ${error.message}`);
    }
  }

  // Special test for sp.implement since it depends on tasks.md
  console.log('Testing sp.implement...');
  try {
    const result = skills.executeSkill('sp.implement', {});
    testResults['sp.implement'] = result.success;
    console.log(`  ${result.success ? '✓' : '✗'} sp.implement: ${result.success ? 'PASS' : 'FAIL'}`);
  } catch (error) {
    testResults['sp.implement'] = false;
    console.log(`  ✗ sp.implement: FAIL - ${error.message}`);
  }

  // Summary
  const passed = Object.values(testResults).filter(Boolean).length;
  const total = Object.keys(testResults).length;

  console.log(`\n=== Test Summary ===`);
  console.log(`Passed: ${passed}/${total} skills`);
  console.log(`Success Rate: ${Math.round((passed/total)*100)}%`);

  if (passed === total) {
    console.log('🎉 All skills are working correctly!');
  } else {
    console.log('⚠️ Some skills need attention.');
  }
}

runCompleteTest().catch(console.error);