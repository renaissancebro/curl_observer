# Plurl

A powerful Playwright + curl-style HTTP testing tool that combines browser automation with API testing capabilities. Navigate web pages, interact with elements, and test multiple API endpoints concurrently—all from a single command.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🌐 **Browser Automation**: Navigate web pages with Playwright
- 🖱️ **Interactive Elements**: Click elements and wait for selectors  
- 🔗 **API Testing**: Test multiple endpoints with concurrent execution
- 🔄 **Retry Logic**: Built-in retry mechanism for failed API requests
- 📸 **Screenshot Capture**: Take screenshots of web pages
- 🎬 **Screen Recording**: Record browser sessions (experimental)
- 📊 **Structured Logging**: Comprehensive JSON logging of all operations
- 🚀 **Flexible HTTP Methods**: Support for GET, POST, PUT, DELETE, etc.
- 🔍 **Response Analysis**: Preview response content and headers
- ⚡ **Performance Metrics**: Track response times and page load metrics
- 🎯 **Keep Open Mode**: Keep browser open for manual interaction

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/renaissancebro/curl_observer.git
cd curl_observer
```

2. Install the package:
```bash
pip install -e .
```

3. Install Playwright browsers:
```bash
playwright install
```

### From PyPI (when published)

```bash
pip install plurl
playwright install
```

## Quick Start

After installation, you can use `plurl` from anywhere:

```bash
# Test a website
plurl --url https://example.com

# Test API endpoints
plurl --url https://api.github.com --test-endpoints /users/octocat

# Interactive browser session
plurl --url https://example.com --headed --keep-open
```

## Usage Examples

### Basic Web Testing

Navigate to a URL and capture metrics:
```bash
plurl --url https://example.com
```

### API Endpoint Testing

Test multiple endpoints concurrently:
```bash
plurl --url https://api.github.com --test-endpoints /users/octocat,/repos/microsoft/playwright
```

### Interactive Browser Testing

Click elements and wait for results:
```bash
plurl --url https://example.com --headed --click-selector "button.login" --wait-selector ".dashboard"
```

### Screenshot Capture

Take a screenshot of the page:
```bash
plurl --url https://example.com --screenshot screenshot.png
```

### API Testing with Retries

Test endpoints with retry logic and custom HTTP method:
```bash
plurl --url https://api.example.com --test-endpoints /api/status --method GET --retry 3 --timeout 10
```

### Development and Debugging

Keep browser open for manual inspection:
```bash
plurl --url https://example.com --headed --keep-open --verbose
```

### Screen Recording (Experimental)

Record browser session:
```bash
plurl --url https://example.com --headed --record
```

## Command Reference

```
plurl [OPTIONS]

OPTIONS:
  --url URL                    URL to launch in Playwright (required)
  --test-endpoints ENDPOINTS   Comma-separated list of API endpoints to test
  --click-selector SELECTOR    CSS selector to click after page load
  --wait-selector SELECTOR     CSS selector to wait for before continuing
  --method METHOD              HTTP method for API testing (default: GET)
  --timeout SECONDS            Request timeout in seconds (default: 30)
  --retry COUNT                Number of retry attempts for API requests (default: 0)
  --headless                   Run browser in headless mode (default)
  --headed                     Run browser in headed mode (visible)
  --keep-open                  Keep browser open after completion (requires --headed)
  --screenshot PATH            Take screenshot and save to specified path
  --record                     Record screen session (experimental)
  --verbose, -v                Enable verbose output
  --log-file PATH              Path to write structured log file (auto-generated if not specified)
  --help, -h                   Show help message and exit
```

## Output Format

Plurl provides comprehensive output including:

### Console Output
```
=== Plurl Session Summary ===
URL: https://api.github.com
Total time: 2.34s
Page title: GitHub API
API endpoints tested: 2
API success rate: 2/2 (100.0%)
Log file: logs/plurl_20240122_143052.json
=== End Summary ===
```

### Structured JSON Logs

All operations are logged in structured JSON format with events such as:
- `session_start`: Session initialization
- `phase`: Different execution phases
- `browser_*`: Browser-related events  
- `api_*`: API testing events
- `success`/`warning`/`error`: Status messages

### API Response Details

For each API endpoint tested:
- HTTP status code and response time
- Response headers and content preview
- Error details for failed requests
- Retry attempt information

## Advanced Usage

### Environment Variables

You can set default values using environment variables:

```bash
export PLURL_TIMEOUT=60
export PLURL_LOG_DIR=/var/log/plurl
export PLURL_HEADLESS=false
```

### Configuration File

Create a `.plurlrc` file in your project root:

```json
{
  "timeout": 30,
  "headless": true,
  "log_dir": "./logs",
  "default_endpoints": ["/health", "/status"]
}
```

### CI/CD Integration

Perfect for automated testing in CI pipelines:

```yaml
# GitHub Actions example
- name: Test API endpoints
  run: |
    plurl --url ${{ env.API_URL }} \
          --test-endpoints /health,/api/v1/status \
          --timeout 10 \
          --retry 2 \
          --headless
```

## Plurl vs Curl: When to Use Which

### 🌐 **Plurl Advantages**

#### **Browser Context & JavaScript**
Plurl renders full web applications with JavaScript, while curl only gets raw HTML:

```bash
# Plurl: Tests complete SPA with dynamic content
plurl --url https://react-app.com --test-endpoints /api/data --headed

# Curl: Misses JavaScript-rendered content
curl https://react-app.com  # ❌ Incomplete for SPAs
```

#### **Visual Verification & Screenshots**
```bash
# Plurl: Visual confirmation of what users see
plurl --url https://app.com --screenshot result.png --keep-open

# Curl: No visual feedback available
curl https://app.com  # ❌ Text-only output
```

#### **Interactive User Workflows**
```bash
# Plurl: Handle complex user interactions
plurl --url https://app.com --click-selector ".login-btn" \
      --wait-selector ".dashboard" --test-endpoints /api/profile

# Curl: Requires manual auth token management
curl -H "Authorization: Bearer $TOKEN" https://app.com/api/profile
```

#### **Concurrent API Testing**
```bash
# Plurl: Tests multiple endpoints simultaneously
plurl --url https://api.com --test-endpoints /users,/posts,/comments,/health

# Curl: Sequential testing only
for endpoint in users posts; do curl https://api.com/$endpoint; done
```

### ⚡ **Curl Advantages**

#### **Speed & Efficiency**
```bash
# Curl: Instant responses (~50ms)
curl https://api.github.com/users/octocat

# Plurl: Browser overhead (~2-3s startup)
plurl --url https://api.github.com --test-endpoints /users/octocat
```

#### **Simplicity & Universal Availability**
```bash
# Curl: Pre-installed on most systems
curl -X POST https://api.com/data -d '{"name":"test"}'

# Plurl: Requires installation
pip install plurl && playwright install
```

#### **Fine-grained HTTP Control**
```bash
# Curl: Precise control over requests
curl -H "Content-Type: application/json" \
     -H "User-Agent: MyBot/1.0" \
     -X PUT https://api.com/resource/123 \
     -d '{"field":"value"}'
```

### 🎯 **Decision Matrix**

| Use Case | Plurl | Curl | Reason |
|----------|--------|------|---------|
| REST API testing | ❌ | ✅ | Curl is faster and simpler |
| GraphQL API testing | ❌ | ✅ | Direct HTTP POST with curl |
| Single Page App (SPA) testing | ✅ | ❌ | Needs browser JS execution |
| File downloads/uploads | ❌ | ✅ | Curl excels at file operations |
| Visual regression testing | ✅ | ❌ | Screenshots only with Plurl |
| Load/performance testing | ❌ | ✅ | Curl has less overhead |
| Web form authentication | ✅ | ❌ | Complex UI interactions |
| CI/CD health checks | ❌ | ✅ | Lightweight and fast |
| Interactive debugging | ✅ | ❌ | Visual inspection needed |
| Mobile responsiveness | ✅ | ❌ | Browser viewport simulation |

### 🔄 **Hybrid Workflows**

Often the best approach combines both tools:

```bash
# 1. Use Plurl for complex web testing and auth
plurl --url https://app.com --click-selector ".login" \
      --test-endpoints /api/dashboard --log-file session.json

# 2. Extract auth details from Plurl logs
TOKEN=$(jq -r '.events[] | select(.type=="api_success") | .headers.authorization' session.json)

# 3. Use Curl for fast, targeted API testing
curl -H "Authorization: $TOKEN" https://api.com/detailed-endpoint
curl -H "Authorization: $TOKEN" https://api.com/bulk-data | jq '.items | length'
```

### 📋 **Quick Decision Guide**

**Choose Plurl when:**
- Testing SPAs or JavaScript-heavy sites
- Need visual verification (screenshots)
- Complex authentication flows (web forms)
- End-to-end user journey testing
- Development and debugging
- Testing responsive design

**Choose Curl when:**
- Simple REST API testing
- File operations (upload/download)
- Shell scripting and automation
- CI/CD health checks
- Performance/load testing
- Fine-grained HTTP control needed

## Architecture

Plurl consists of several modular components:

- **`cli.py`**: Command-line interface and orchestration
- **`browser_debugger.py`**: Playwright browser automation wrapper
- **`api_tester.py`**: Async HTTP client for API endpoint testing
- **`logger.py`**: Structured logging with JSON output
- **`utils.py`**: Utility functions for validation and formatting

## Error Handling

Comprehensive error handling for:

- ❌ Network timeouts and connection errors
- ❌ Invalid selectors or missing elements  
- ❌ HTTP errors and API failures
- ❌ Browser launch failures
- ❌ File I/O operations

All errors are logged with context and appropriate exit codes are returned.

## Requirements

- **Python**: 3.7 or higher
- **Playwright**: >= 1.40.0 (browser automation)
- **httpx**: >= 0.25.0 (async HTTP requests)

## Manual Page

Install the manual page:

```bash
sudo cp docs/plurl.1 /usr/local/share/man/man1/
man plurl
```

## Development

### Local Development

1. Clone and install in development mode:
```bash
git clone https://github.com/renaissancebro/curl_observer.git
cd curl_observer
pip install -e .
```

2. Run tests:
```bash
python -m pytest tests/
```

3. Format code:
```bash
black *.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/renaissancebro/curl_observer/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/renaissancebro/curl_observer/discussions)
- 📖 **Documentation**: [GitHub README](https://github.com/renaissancebro/curl_observer#readme)

---

**Plurl** - *Playwright meets curl for modern web testing*