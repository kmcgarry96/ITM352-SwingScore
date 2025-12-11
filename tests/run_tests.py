#!/usr/bin/env python3
"""
Custom test runner with enhanced output formatting
Run this instead of unittest discover for prettier output
"""
import unittest
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class with colored output"""
    
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results = []
    
    def startTest(self, test):
        super().startTest(test)
        self.current_test_output = StringIO()
        self._original_stdout = sys.stdout
        # Don't redirect stdout to capture backend prints
    
    def addSuccess(self, test):
        super().addSuccess(test)
        test_name = self.getDescription(test)
        self.test_results.append(('PASS', test_name, None))
    
    def addError(self, test, err):
        super().addError(test, err)
        test_name = self.getDescription(test)
        self.test_results.append(('ERROR', test_name, err))
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        test_name = self.getDescription(test)
        self.test_results.append(('FAIL', test_name, err))
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        test_name = self.getDescription(test)
        self.test_results.append(('SKIP', test_name, reason))


class ColoredTextTestRunner(unittest.TextTestRunner):
    """Custom test runner with colored and formatted output"""
    
    resultclass = ColoredTextTestResult
    
    def run(self, test):
        """Run tests with custom formatting"""
        result = super().run(test)
        
        # Print formatted results
        self.print_results(result)
        
        return result
    
    def print_results(self, result):
        """Print beautifully formatted test results"""
        print("\n" + "="*80)
        print(f"{ColoredTextTestResult.BOLD}{ColoredTextTestResult.CYAN}TEST RESULTS SUMMARY{ColoredTextTestResult.RESET}")
        print("="*80 + "\n")
        
        # Group tests by file
        tests_by_file = {}
        for status, test_name, error in result.test_results:
            # Extract file name from test
            if '(' in test_name and ')' in test_name:
                file_part = test_name.split('(')[1].split(')')[0]
                module = file_part.split('.')[0] if '.' in file_part else file_part
            else:
                module = "unknown"
            
            if module not in tests_by_file:
                tests_by_file[module] = []
            tests_by_file[module].append((status, test_name, error))
        
        # Print results grouped by file
        for module in sorted(tests_by_file.keys()):
            tests = tests_by_file[module]
            
            # Module header
            print(f"{ColoredTextTestResult.BOLD}{ColoredTextTestResult.MAGENTA}📦 {module}{ColoredTextTestResult.RESET}")
            print("-" * 80)
            
            # Print each test
            for status, test_name, error in tests:
                # Clean up test name
                if '(' in test_name:
                    clean_name = test_name.split('(')[0].strip()
                else:
                    clean_name = test_name
                
                # Format based on status
                if status == 'PASS':
                    icon = f"{ColoredTextTestResult.GREEN}✓{ColoredTextTestResult.RESET}"
                    status_text = f"{ColoredTextTestResult.GREEN}PASS{ColoredTextTestResult.RESET}"
                elif status == 'FAIL':
                    icon = f"{ColoredTextTestResult.RED}✗{ColoredTextTestResult.RESET}"
                    status_text = f"{ColoredTextTestResult.RED}FAIL{ColoredTextTestResult.RESET}"
                elif status == 'ERROR':
                    icon = f"{ColoredTextTestResult.RED}⚠{ColoredTextTestResult.RESET}"
                    status_text = f"{ColoredTextTestResult.RED}ERROR{ColoredTextTestResult.RESET}"
                else:  # SKIP
                    icon = f"{ColoredTextTestResult.YELLOW}⊘{ColoredTextTestResult.RESET}"
                    status_text = f"{ColoredTextTestResult.YELLOW}SKIP{ColoredTextTestResult.RESET}"
                
                print(f"  {icon} {status_text:20} {clean_name}")
            
            print()
        
        # Print summary statistics
        print("="*80)
        total = result.testsRun
        passed = len([t for t in result.test_results if t[0] == 'PASS'])
        failed = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped)
        
        print(f"{ColoredTextTestResult.BOLD}SUMMARY:{ColoredTextTestResult.RESET}")
        print(f"  Total:   {total} tests")
        print(f"  {ColoredTextTestResult.GREEN}Passed:  {passed}{ColoredTextTestResult.RESET}")
        if failed > 0:
            print(f"  {ColoredTextTestResult.RED}Failed:  {failed}{ColoredTextTestResult.RESET}")
        if errors > 0:
            print(f"  {ColoredTextTestResult.RED}Errors:  {errors}{ColoredTextTestResult.RESET}")
        if skipped > 0:
            print(f"  {ColoredTextTestResult.YELLOW}Skipped: {skipped}{ColoredTextTestResult.RESET}")
        
        # Success rate
        if total > 0:
            success_rate = (passed / total) * 100
            if success_rate == 100:
                color = ColoredTextTestResult.GREEN
                emoji = "🎉"
            elif success_rate >= 80:
                color = ColoredTextTestResult.YELLOW
                emoji = "⚠️"
            else:
                color = ColoredTextTestResult.RED
                emoji = "❌"
            
            print(f"\n  {emoji} {color}Success Rate: {success_rate:.1f}%{ColoredTextTestResult.RESET}")
        
        print("="*80 + "\n")
        
        # Print detailed errors if any
        if failed > 0 or errors > 0:
            print(f"\n{ColoredTextTestResult.BOLD}{ColoredTextTestResult.RED}DETAILED FAILURES:{ColoredTextTestResult.RESET}\n")
            for status, test_name, error in result.test_results:
                if status in ('FAIL', 'ERROR'):
                    print(f"{ColoredTextTestResult.RED}{'='*80}{ColoredTextTestResult.RESET}")
                    print(f"{ColoredTextTestResult.BOLD}{test_name}{ColoredTextTestResult.RESET}")
                    print(f"{ColoredTextTestResult.RED}{'-'*80}{ColoredTextTestResult.RESET}")
                    if error:
                        print(self._exc_info_to_string(error, None))
                    print()


def main():
    """Main test runner"""
    print(f"\n{ColoredTextTestResult.BOLD}{ColoredTextTestResult.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║                      ITM352-SwingScore Test Suite                              ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    print(f"{ColoredTextTestResult.RESET}")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = ColoredTextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
