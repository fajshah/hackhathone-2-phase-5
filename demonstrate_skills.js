#!/usr/bin/env node

/**
 * Demonstration script for Skills Implementation
 * Shows how to use all available skills
 */

const SkillsImplementation = require('./skills_implementation.js');

// Create an instance of the skills implementation
const skills = new SkillsImplementation();

console.log('=== Skills Implementation Demonstration ===\n');

// List all available skills
console.log('Available Skills:');
const skillsList = skills.listSkills();
skillsList.skills.forEach((skill, index) => {
  console.log(`${index + 1}. ${skill}`);
});
console.log('');

// Demonstrate each skill with sample data
async function demonstrateSkills() {
  console.log('Demonstrating each skill...\n');

  // 1. sp.specify - Create feature specification
  console.log('1. Demonstrating sp.specify...');
  const specResult = skills.executeSkill('sp.specify', {
    name: 'User Authentication',
    description: 'Implement secure user authentication with JWT tokens'
  });
  console.log('Result:', specResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 2. sp.plan - Create implementation plan
  console.log('2. Demonstrating sp.plan...');
  const planResult = skills.executeSkill('sp.plan');
  console.log('Result:', planResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 3. sp.tasks - Generate tasks
  console.log('3. Demonstrating sp.tasks...');
  const tasksResult = skills.executeSkill('sp.tasks');
  console.log('Result:', tasksResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 4. sp.clarify - Generate clarification questions
  console.log('4. Demonstrating sp.clarify...');
  const clarifyResult = skills.executeSkill('sp.clarify');
  console.log('Result:', clarifyResult.success ? '✓ Success' : '✗ Failed');
  console.log('Questions generated:', clarifyResult.result.questions.length);
  console.log('');

  // 5. sp.constitution - Create constitution
  console.log('5. Demonstrating sp.constitution...');
  const constitutionResult = skills.executeSkill('sp.constitution', {
    principles: [
      'Secure by default',
      'Privacy first',
      'Performance oriented',
      'Test driven development'
    ],
    decisionMakers: ['tech-lead', 'product-owner', 'security-officer']
  });
  console.log('Result:', constitutionResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 6. sp.checklist - Generate checklist
  console.log('6. Demonstrating sp.checklist...');
  const checklistResult = skills.executeSkill('sp.checklist');
  console.log('Result:', checklistResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 7. sp.analyze - Analyze artifacts
  console.log('7. Demonstrating sp.analyze...');
  const analyzeResult = skills.executeSkill('sp.analyze');
  console.log('Result:', analyzeResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 8. sp.adr - Create ADR
  console.log('8. Demonstrating sp.adr...');
  const adrResult = skills.executeSkill('sp.adr', {
    title: 'Authentication Method Selection',
    decision: 'JWT-based authentication with refresh tokens',
    context: 'Need secure, stateless authentication mechanism',
    consequences: 'Improved scalability but requires token management',
    alternatives: ['Session-based auth', 'OAuth2', 'OpenID Connect']
  });
  console.log('Result:', adrResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 9. sp.phr - Create PHR
  console.log('9. Demonstrating sp.phr...');
  const phrResult = skills.executeSkill('sp.phr', {
    prompt: 'Implement user authentication feature',
    response: 'Created JWT-based authentication system',
    context: { feature: 'authentication', priority: 'high' },
    tags: ['auth', 'security', 'feature'],
    skillUsed: 'sp.implement',
    duration: 120,
    success: true
  });
  console.log('Result:', phrResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 10. sp.reverse-engineer - Reverse engineer codebase
  console.log('10. Demonstrating sp.reverse-engineer...');
  const reverseResult = skills.executeSkill('sp.reverse-engineer');
  console.log('Result:', reverseResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 11. sp.taskstoissues - Convert tasks to GitHub issues
  console.log('11. Demonstrating sp.taskstoissues...');
  const issuesResult = skills.executeSkill('sp.taskstoissues');
  console.log('Result:', issuesResult.success ? '✓ Success' : '✗ Failed');
  console.log('Issues created:', issuesResult.result.issues.length);
  console.log('');

  // 12. sp.git.commit_pr - Git workflow
  console.log('12. Demonstrating sp.git.commit_pr...');
  const gitResult = skills.executeSkill('sp.git.commit_pr', {
    message: 'Implement user authentication feature'
  });
  console.log('Result:', gitResult.success ? '✓ Success' : '✗ Failed');
  console.log('');

  // 13. sp.implement - Execute implementation plan
  console.log('13. Demonstrating sp.implement...');
  try {
    const implementResult = skills.executeSkill('sp.implement');
    console.log('Result:', implementResult.success ? '✓ Success' : '✗ Failed');
  } catch (error) {
    console.log('Result: ✗ Failed (expected if tasks.md not found)');
  }
  console.log('');

  console.log('=== Demonstration Complete ===');
  console.log('All skills have been demonstrated with sample data.');
  console.log('Check the generated files in your project directory.');
}

// Run the demonstration
demonstrateSkills().catch(console.error);