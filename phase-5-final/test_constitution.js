const SkillsImplementation = require('./skills_implementation.js');
const skills = new SkillsImplementation();

try {
  const result = skills.executeSkill('sp.constitution', {
    principles: [
      'Secure by default',
      'Privacy first',
      'Performance oriented',
      'Test driven development'
    ],
    decisionMakers: ['tech-lead', 'product-owner', 'security-officer']
  });
  console.log('Constitution result:', result);
} catch (error) {
  console.error('Error creating constitution:', error);
  console.error('Stack trace:', error.stack);
}