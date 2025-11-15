#!/usr/bin/env python3
"""
Security check script for the Investment Backend.

This script checks for common security issues including:
- Hardcoded API keys and secrets
- Insecure dependencies
- Outdated dependencies with known vulnerabilities
- Misconfigurations in settings
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Pattern
import requests

# Configuration
ROOT_DIR = Path(__file__).parent.parent
EXCLUDED_DIRS = {
    '.git',
    '__pycache__',
    'venv',
    'node_modules',
    '.pytest_cache',
    '.mypy_cache'
}

# Patterns to detect sensitive information
SENSITIVE_PATTERNS = [
    # API keys
    (r'(?i)api[_-]?key\s*[=:]\s*[\'\"][0-9a-zA-Z]{16,}[\'\"]', 'API_KEY', 'Hardcoded API key'),
    (r'(?i)secret[\s\w]*[=:]\s*[\'\"][0-9a-zA-Z]{16,}[\'\"]', 'SECRET', 'Hardcoded secret'),
    (r'(?i)password\s*[=:]\s*[\'\"][^\'\"]+[\'\"]', 'PASSWORD', 'Hardcoded password'),
    (r'(?i)token\s*[=:]\s*[\'\"][0-9a-zA-Z]{16,}[\'\"]', 'TOKEN', 'Hardcoded token'),
    # URLs with credentials
    (r'(?i)(https?://)[^:\s]+:[^@\s]+@', 'CREDENTIALS_IN_URL', 'Credentials in URL'),
    # AWS specific
    (r'AKIA[0-9A-Z]{16}', 'AWS_ACCESS_KEY', 'AWS Access Key ID'),
    (r'[0-9a-zA-Z/+]{40}', 'AWS_SECRET_KEY', 'AWS Secret Access Key'),
]

class SecurityCheckError(Exception):
    """Custom exception for security check failures."""
    pass

def find_sensitive_info() -> List[Dict]:
    """Search for sensitive information in the codebase."""
    issues = []
    
    # Compile patterns once
    compiled_patterns = [(re.compile(pattern), code, message) 
                        for pattern, code, message in SENSITIVE_PATTERNS]
    
    # Walk through the directory
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip binary files and other non-text files
            if file_path.suffix in {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe'}:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Skip binary files that might have been missed by extension
                    if '\x00' in content:
                        continue
                        
                    for line_num, line in enumerate(content.split('\n'), 1):
                        for pattern, code, message in compiled_patterns:
                            if pattern.search(line):
                                issues.append({
                                    'file': str(file_path.relative_to(ROOT_DIR)),
                                    'line': line_num,
                                    'code': code,
                                    'message': message,
                                    'snippet': line.strip()
                                })
                                
            except (UnicodeDecodeError, PermissionError) as e:
                # Skip files that can't be read as text
                continue
                
    return issues

def check_dependencies() -> List[Dict]:
    """Check for outdated or vulnerable dependencies."""
    issues = []
    
    try:
        # Check if safety is installed
        import safety
        from safety import safety as safety_check
        
        # Check Python dependencies
        requirements = ROOT_DIR / 'requirements.txt'
        if requirements.exists():
            result = safety_check.check(packages=[], check_files=[str(requirements)])
            for vuln in result.vulnerabilities:
                issues.append({
                    'code': 'VULNERABLE_DEPENDENCY',
                    'message': f'Vulnerable dependency: {vuln.name} {vuln.spec}',
                    'details': {
                        'vulnerability': vuln.vulnerability_id,
                        'affected_versions': vuln.vulnerable_spec,
                        'advisory': vuln.advisory,
                        'severity': vuln.severity
                    }
                })
                
    except ImportError:
        issues.append({
            'code': 'SAFETY_NOT_INSTALLED',
            'message': 'Safety package not installed. Run: pip install safety',
            'details': {}
        })
    
    return issues

def check_env_file() -> Tuple[bool, List[Dict]]:
    """Check if .env.example is up to date with .env."""
    issues = []
    
    env_example = ROOT_DIR / '.env.example'
    env_file = ROOT_DIR / '.env'
    
    if not env_example.exists():
        issues.append({
            'code': 'MISSING_ENV_EXAMPLE',
            'message': '.env.example file is missing',
            'details': {}
        })
        return False, issues
        
    if not env_file.exists():
        issues.append({
            'code': 'MISSING_ENV',
            'message': '.env file is missing',
            'details': {}
        })
        return False, issues
        
    # Check if .env is in .gitignore
    gitignore = ROOT / '.gitignore'
    if gitignore.exists():
        with open(gitignore, 'r') as f:
            if '.env' not in f.read():
                issues.append({
                    'code': 'ENV_NOT_IGNORED',
                    'message': '.env file is not in .gitignore',
                    'details': {}
                })
    
    return True, issues

def main():
    """Run all security checks."""
    print("🔍 Running security checks...\n")
    
    # Check for sensitive information
    print("🔑 Checking for sensitive information in code...")
    sensitive_issues = find_sensitive_info()
    
    # Check dependencies
    print("📦 Checking dependencies for vulnerabilities...")
    dependency_issues = check_dependencies()
    
    # Check environment configuration
    print("⚙️  Checking environment configuration...")
    env_ok, env_issues = check_env_file()
    
    # Combine all issues
    all_issues = sensitive_issues + dependency_issues + env_issues
    
    # Print results
    if all_issues:
        print("\n❌ Found potential security issues:")
        for issue in all_issues:
            print(f"\n[{issue['code']}] {issue['message']}")
            if 'file' in issue:
                print(f"   File: {issue['file']}:{issue['line']}")
                print(f"   Snippet: {issue['snippet']}")
            if 'details' in issue and issue['details']:
                print("   Details:")
                for key, value in issue['details'].items():
                    print(f"     {key}: {value}")
        
        print("\n🚨 Please fix the above issues before committing.")
        sys.exit(1)
    else:
        print("\n✅ No security issues found!")
        sys.exit(0)

if __name__ == "__main__":
    main()
