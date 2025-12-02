# Test Failure Screenshots

This directory contains screenshots captured when E2E tests fail.

## File Naming Convention

Screenshots are automatically named using the pattern:
```
FAILED_{test_path}_{test_name}_{timestamp}.png
```

Example:
```
FAILED_tests_e2e_test_all_products.py_test_product_page_loads_fiido-t1_20251202_094530.png
```

## Features

- **Automatic capture**: Screenshots are taken automatically when tests fail
- **Full page**: Screenshots capture the entire page (not just viewport)
- **Timestamped**: Each screenshot includes a timestamp for uniqueness
- **Console output**: Screenshot paths are printed to console for easy access

## Cleanup

Screenshots are not committed to git (see `.gitignore`).

To clean up old screenshots:
```bash
# Remove all screenshots
rm screenshots/FAILED_*.png

# Remove screenshots older than 7 days
find screenshots -name "FAILED_*.png" -mtime +7 -delete
```

## Viewing Screenshots

After a test failure, check the console output for the screenshot path, or browse this directory directly.
