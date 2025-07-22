# Play Curl

A powerful Playwright + curl-style HTTP testing tool that combines browser automation with API testing capabilities. This tool allows you to navigate web pages, interact with elements, and test multiple API endpoints concurrently or with retry logic.

## Features

- **Browser Automation**: Navigate to web pages with Playwright
- **Interactive Elements**: Click elements and wait for selectors  
- **API Testing**: Test multiple endpoints with concurrent execution
- **Retry Logic**: Built-in retry mechanism for failed API requests
- **Screenshot Capture**: Take screenshots of web pages
- **Screen Recording**: Record browser sessions (experimental)
- **Structured Logging**: Comprehensive JSON logging of all operations
- **Flexible HTTP Methods**: Support for GET, POST, PUT, DELETE, etc.
- **Response Analysis**: Preview response content and headers
- **Performance Metrics**: Track response times and page load metrics

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Usage

### Basic Usage

Navigate to a URL and test API endpoints:
```bash
python cli.py --url https://example.com --test-endpoints /api/users,/api/posts
```

### Advanced Examples

Test with specific HTTP method and retries:
```bash
python cli.py --url https://api.github.com --test-endpoints /users/octocat --method GET --retry 3 --verbose
```

Take a screenshot:
```bash
python cli.py --url https://example.com --screenshot screenshot.png
```

Click an element and wait for selector:
```bash
python cli.py --url https://example.com --click-selector "button.login" --wait-selector ".dashboard"
```

Run in headed mode with screen recording:
```bash
python cli.py --url https://example.com --headed --record
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | URL to launch in Playwright (required) | - |
| `--test-endpoints` | Comma-separated list of API endpoints | - |
| `--click-selector` | CSS selector to click after page load | - |
| `--wait-selector` | CSS selector to wait for before continuing | - |
| `--method` | HTTP method for API testing | GET |
| `--timeout` | Request timeout in seconds | 30 |
| `--retry` | Number of retry attempts for API requests | 0 |
| `--headless` | Run browser in headless mode | true |
| `--headed` | Run browser in headed mode | false |
| `--screenshot` | Take screenshot and save to specified path | - |
| `--record` | Record screen session (experimental) | false |
| `--verbose` | Enable verbose output | false |
| `--log-file` | Path to write structured log file | auto-generated |

## Output

The tool provides:

1. **Console Summary**: Real-time status updates and final summary
2. **Structured Logs**: Detailed JSON logs of all operations
3. **API Results**: Status codes, response times, and content previews
4. **Performance Metrics**: Page load times and browser metrics
5. **Screenshots/Videos**: Visual captures when requested

### Sample Output

```
=== Play Curl Session Summary ===
URL: https://api.github.com
Total time: 2.34s
Page title: GitHub API
API endpoints tested: 2
API success rate: 2/2 (100.0%)
Log file: logs/play_curl_20240122_143052.json
=== End Summary ===
```

## Architecture

The tool consists of several components:

- **cli.py**: Main command-line interface and orchestration
- **browser_debugger.py**: Playwright browser automation wrapper
- **api_tester.py**: HTTP client for API endpoint testing
- **logger.py**: Structured logging with JSON output
- **utils.py**: Utility functions for validation and formatting

## Log Structure

Structured logs include events such as:

- `session_start`: Session initialization
- `phase`: Different execution phases
- `browser_*`: Browser-related events
- `api_*`: API testing events
- `success`/`warning`/`error`: Status messages

## Requirements

- Python 3.7+
- Playwright >= 1.40.0
- httpx >= 0.25.0
- asyncio-compat >= 0.7.0

## Error Handling

The tool includes comprehensive error handling for:

- Network timeouts and connection errors
- Invalid selectors or missing elements
- HTTP errors and API failures
- Browser launch failures
- File I/O operations

All errors are logged with context and appropriate exit codes are returned.

## Development

The tool is built with async/await patterns and uses:

- **Playwright** for browser automation
- **httpx** for async HTTP requests
- **asyncio** for concurrent operations
- **argparse** for CLI argument parsing

## License

MIT License - see LICENSE file for details.