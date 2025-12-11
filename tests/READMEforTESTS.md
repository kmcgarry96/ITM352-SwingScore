# Tests for ITM352-SwingScore

This directory contains all test files for the SwingScore application.

---

## 🚀 Quick Start

### Run ALL Tests (Pretty Output) ⭐ RECOMMENDED

**Option 1: Shell Script (Easiest)**
```bash
./tests/test.sh
```

**Option 2: Python Runner**
```bash
python3 tests/run_tests.py
```

**Features of Pretty Output:**
- ✅ Color-coded results (green ✓ for pass, red ✗ for fail)
- 📦 Tests grouped by file/module
- 📊 Summary statistics with success rate
- 🎉 Clean, easy-to-read format
- 🎯 Shows detailed errors only if tests fail

### Run ALL Tests (Standard Output)
```bash
python3 -m unittest discover tests/
```

### Run Tests with Verbose Output
```bash
python3 -m unittest discover tests/ -v
```

---

## 📋 Test Files and Individual Commands

### 1. **test_app.py** - Flask Application Basic Tests
**What it tests:**
- Home page loads successfully
- Home page contains expected content
- Basic Flask application functionality

**Run individually:**
```bash
python3 tests/test_app.py
```
Or:
```bash
python3 -m unittest tests.test_app
```

---

### 2. **test_swing_score.py** - Swing Score Normalization
**What it tests:**
- `normalize_series()` basic functionality
- Normalization with all equal values
- Edge cases in normalization

**Run individually:**
```bash
python3 tests/test_swing_score.py
```
Or:
```bash
python3 -m unittest tests.test_swing_score
```

---

### 3. **test_data_loading.py** - Data Loading Functions
**What it tests:**
- `load_state_raw_data()` with invalid state codes
- Case-insensitive state code handling
- Error handling for missing data files

**Run individually:**
```bash
python3 tests/test_data_loading.py
```
Or:
```bash
python3 -m unittest tests.test_data_loading
```

---

### 4. **test_aggregation.py** - Data Aggregation Logic
**What it tests:**
- `aggregate_to_county_year()` basic functionality
- Margin calculations (dem_votes - rep_votes)
- Total votes summation
- DataFrame structure validation

**Run individually:**
```bash
python3 tests/test_aggregation.py
```
Or:
```bash
python3 -m unittest tests.test_aggregation
```

---

### 5. **test_api_endpoints.py** - Flask API Endpoints
**What it tests:**
- Index page loads and returns HTML
- State view endpoints (e.g., `/state/PA`)
- Map view endpoints (e.g., `/map/PA`)
- Case-insensitive state codes
- 404 handling for nonexistent routes

**Run individually:**
```bash
python3 tests/test_api_endpoints.py
```
Or:
```bash
python3 -m unittest tests.test_api_endpoints
```

---

### 6. **test_swing_components.py** - Swing Score Components
**What it tests:**
- `compute_swing_components()` return structure
- Component calculations (margin_change, closeness, turnout, votes)
- Normalization ranges (0-1)
- Empty series handling

**Run individually:**
```bash
python3 tests/test_swing_components.py
```
Or:
```bash
python3 -m unittest tests.test_swing_components
```

---

### 7. **test_validation.py** - Input Validation & Edge Cases
**What it tests:**
- Invalid/empty state codes
- Single value normalization
- Negative value handling
- NaN value handling
- Boundary conditions

**Run individually:**
```bash
python3 tests/test_validation.py
```
Or:
```bash
python3 -m unittest tests.test_validation
```

---

### 8. **test_integration.py** - End-to-End Integration Tests
**What it tests:**
- Complete workflow: home → state view
- Complete workflow: home → map view
- Multiple state access in sequence
- Full application integration

**Run individually:**
```bash
python3 tests/test_integration.py
```
Or:
```bash
python3 -m unittest tests.test_integration
```

---

### 9. **test_display.py** - Display & Formatting Functions
**What it tests:**
- `show_ranked_counties()` output formatting
- `show_state_summary()` output formatting
- Console output generation
- Data presentation

**Run individually:**
```bash
python3 tests/test_display.py
```
Or:
```bash
python3 -m unittest tests.test_display
```

---

## 🎯 Running Specific Test Categories

### Run only Flask/API tests:
```bash
python3 -m unittest tests.test_app tests.test_api_endpoints
```

### Run only data processing tests:
```bash
python3 -m unittest tests.test_data_loading tests.test_aggregation
```

### Run only swing score calculation tests:
```bash
python3 -m unittest tests.test_swing_score tests.test_swing_components
```

---

## 📊 Test Coverage

To run tests with coverage (requires pytest and pytest-cov):
```bash
pip install pytest pytest-cov
python3 -m pytest --cov=backend tests/
```

---

## ✅ Adding New Tests

1. Create a new file with the prefix `test_` (e.g., `test_new_feature.py`)
2. Import unittest and the modules you want to test
3. Create test classes that inherit from `unittest.TestCase`
4. Write test methods with the prefix `test_`
5. Update this README with the new test file documentation

---

## 📝 Test Summary

| Test File | # Tests | Focus Area |
|-----------|---------|------------|
| test_app.py | 2 | Flask basic functionality |
| test_swing_score.py | 2 | Score normalization |
| test_data_loading.py | 2 | Data loading |
| test_aggregation.py | 2 | Data aggregation |
| test_api_endpoints.py | 6 | API endpoints |
| test_swing_components.py | 3 | Component calculations |
| test_validation.py | 5 | Input validation |
| test_integration.py | 3 | End-to-end workflows |
| test_display.py | 2 | Output formatting |
| **TOTAL** | **27** | **Full application** |
