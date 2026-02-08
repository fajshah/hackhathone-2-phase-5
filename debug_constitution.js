const fs = require('fs');
const path = require('path');

// Simulate the constitution method
function createConstitution(args) {
    console.log('Creating/updating project constitution...');

    const constitution = {
      title: 'Project Constitution',
      version: '1.0.0',
      principles: args?.principles || [
        'Maintain backward compatibility',
        'Follow security best practices',
        'Ensure test coverage >90%',
        'Document all public APIs'
      ],
      governance: {
        decisionMakers: args?.decisionMakers || ['lead', 'architect'],
        conflictResolution: 'consensus-first, escalation to lead'
      },
      compliance: {
        securityStandards: ['OWASP', 'ISO27001'],
        qualityMetrics: ['coverage', 'performance', 'security']
      }
    };

    const constitutionPath = path.join(process.cwd(), 'CONSTITUTION.md');
    console.log('Path being used:', constitutionPath);

    // Create formatConstitutionMd function
    function formatConstitutionMd(constitution) {
      let content = '# Project Constitution\n\n';
      content += `Version: ${constitution.version}\n\n`;

      content += '## Principles\n\n';
      for (const principle of constitution.principles) {
        content += `- ${principle}\n`;
      }

      content += '\n## Governance\n\n';
      content += `Decision Makers: ${constitution.governance.decisionMakers.join(', ')}\n\n`;
      content += `Conflict Resolution: ${constitution.governance.conflictResolution}\n\n`;

      content += '## Compliance\n\n';
      content += 'Security Standards:\n';
      for (const standard of constitution.compliance.securityStandards) {
        content += `- ${standard}\n`;
      }

      return content;
    }

    const constitutionContent = formatConstitutionMd(constitution);

    fs.writeFileSync(constitutionPath, constitutionContent);

    console.log('Constitution created successfully');
    // Check if there's a typo here
    return { success: true, constitutionPath: constitutionPath };
}

try {
    const result = createConstitution({ principles: ['test'] });
    console.log('Success:', result);
} catch (error) {
    console.error('Error:', error.message);
    console.error('Stack:', error.stack);
}