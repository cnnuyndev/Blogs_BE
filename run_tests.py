#!/usr/bin/env python
"""
Test runner script for BE_BLOG project
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_BLOG.settings')


def run_django_tests(test_path=None, verbosity=2):
    """Run Django tests"""
    cmd = ['python', 'manage.py', 'test', f'--verbosity={verbosity}']
    
    if test_path:
        cmd.append(test_path)
    
    print(f"Running Django tests: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=project_root)


def run_pytest_tests(test_path=None, markers=None, coverage=False):
    """Run pytest tests"""
    cmd = ['pytest']
    
    if test_path:
        cmd.append(test_path)
    
    if markers:
        cmd.extend(['-m', markers])
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    cmd.extend(['-v', '--tb=short'])
    
    print(f"Running pytest: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=project_root)


def run_celery_tests():
    """Run Celery-specific tests"""
    print("Running Celery tests...")
    return run_pytest_tests('tests/unit/test_celery_tasks.py', 'celery')


def run_api_tests():
    """Run API tests"""
    print("Running API tests...")
    return run_pytest_tests('tests/api/', 'api')


def run_unit_tests():
    """Run unit tests"""
    print("Running unit tests...")
    return run_pytest_tests('tests/unit/', 'unit')


def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    return run_pytest_tests('tests/integration/', 'integration')


def run_all_tests(coverage=False):
    """Run all tests"""
    print("Running all tests...")
    
    # Run Django tests
    django_result = run_django_tests()
    
    # Run pytest tests
    pytest_result = run_pytest_tests(coverage=coverage)
    
    return django_result.returncode == 0 and pytest_result.returncode == 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='BE_BLOG Test Runner')
    parser.add_argument('--django', action='store_true', help='Run Django tests only')
    parser.add_argument('--pytest', action='store_true', help='Run pytest tests only')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--api', action='store_true', help='Run API tests only')
    parser.add_argument('--celery', action='store_true', help='Run Celery tests only')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--path', type=str, help='Run tests from specific path')
    parser.add_argument('--markers', type=str, help='Run tests with specific markers')
    parser.add_argument('--verbosity', type=int, default=2, help='Django test verbosity (1-3)')
    
    args = parser.parse_args()
    
    success = True
    
    try:
        if args.django:
            success = run_django_tests(args.path, args.verbosity).returncode == 0
        elif args.pytest:
            success = run_pytest_tests(args.path, args.markers, args.coverage).returncode == 0
        elif args.unit:
            success = run_unit_tests()
        elif args.integration:
            success = run_integration_tests()
        elif args.api:
            success = run_api_tests()
        elif args.celery:
            success = run_celery_tests()
        elif args.path:
            success = run_pytest_tests(args.path, args.markers, args.coverage).returncode == 0
        elif args.markers:
            success = run_pytest_tests(markers=args.markers, coverage=args.coverage).returncode == 0
        else:
            # Run all tests by default
            success = run_all_tests(args.coverage)
        
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
