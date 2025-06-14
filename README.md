# 🕷️ SEO Spider Analyzer

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://coff.ee/sakkoulas)

A comprehensive Python-based SEO crawler and auditor that scrapes websites, analyzes technical SEO metrics, and generates detailed audit reports using AI (Ollama/ChatGPT). Features multi-language support, performance analysis, and competitive insights.

## ✨ Features

### 🔍 Web Scraping & Crawling
- **Domain-wide crawling** with configurable page limits
- **Multi-language detection** and organization
- **Intelligent URL filtering** and deduplication
- **Respectful crawling** with rate limiting
- **Error handling** and comprehensive logging

### 📊 SEO Analysis
- **Technical SEO metrics** (meta tags, headings, canonical URLs)
- **Content analysis** (word count, keyword density, readability)
- **Image optimization** (alt text, lazy loading, responsive images)
- **Internal/external link analysis** with anchor text evaluation
- **Schema markup detection** (JSON-LD, Microdata, RDFa)
- **Mobile optimization** assessment
- **Accessibility analysis** (WCAG compliance indicators)
- **Performance metrics** simulation
- **Core Web Vitals** estimation

### 🤖 AI-Powered Auditing
- **Ollama integration** for local AI analysis
- **ChatGPT/OpenAI API** support for cloud-based analysis
- **Intelligent context handling** for large datasets
- **Multi-language audit reports** (Greek/English)
- **Actionable recommendations** with examples
- **Single page or domain-wide** audit modes

### 📈 Advanced Features
- **Competitive analysis** signals
- **Security headers** evaluation
- **Cache optimization** analysis
- **Social media meta tags** detection
- **Breadcrumb analysis**
- **Content freshness** indicators

## 🚀 Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Required Python Packages
```bash
pip install requests beautifulsoup4 pathlib argparse
```

### Optional: AI Providers Setup

#### For Ollama (Local AI)
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model: `ollama pull deepseek-coder:6.7b`
3. Start Ollama server: `ollama serve`

#### For ChatGPT/OpenAI
1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Set environment variable: `export OPENAI_API_KEY="your-key-here"`

## 📖 Usage

### Basic Web Scraping
```bash
# Crawl a website (max 50 pages)
python scrapper.py https://example.com --max-pages 50

# Crawl more pages
python scrapper.py https://example.com --max-pages 100
```

### SEO Auditing

#### Full Domain Audit
```bash
# Using Ollama (local)
python seo_auditor.py /path/to/crawl/data --provider ollama

# Using ChatGPT
python seo_auditor.py /path/to/crawl/data --provider chatgpt --openai-api-key YOUR_KEY

# Audit specific language
python seo_auditor.py /path/to/crawl/data --language el --provider ollama
```

#### Single Page Analysis
```bash
# Analyze a single page file
python seo_auditor.py /path/to/page.json --provider ollama --output audit_report.md
```

#### Audit Modes
```bash
# Overview audit only
python seo_auditor.py /path/to/crawl/data --mode overview

# Technical SEO focus
python seo_auditor.py /path/to/crawl/data --mode technical

# Page-by-page analysis
python seo_auditor.py /path/to/crawl/data --mode pages

# Full comprehensive audit
python seo_auditor.py /path/to/crawl/data --mode full --output full_audit.md
```

### Command Line Options

#### Scraper Options
- `--max-pages`: Maximum pages to crawl (default: 50)

#### Auditor Options
- `--provider`: AI provider (ollama/chatgpt)
- `--model`: Model name (default: deepseek-coder:6.7b for Ollama, gpt-3.5-turbo for ChatGPT)
- `--mode`: Audit type (overview/technical/pages/full)
- `--language`: Target language (el/en/fr/de/es/it)
- `--output`: Output file for audit report
- `--timeout`: Request timeout in seconds (default: 180)
- `--list-languages`: Show available languages in crawl data

## 📁 Project Structure

```
├── scrapper.py          # Main web scraping tool
├── seo_auditor.py       # AI-powered SEO auditor
├── crawl_data/          # Output directory for scraped data
│   └── domain.com/
│       └── 2024-01-15_10-30-00/
│           ├── el/      # Greek pages
│           ├── en/      # English pages
│           ├── _summary.json
│           └── crawl.log
└── README.md
```

## 📊 Output Examples

### Crawl Data Structure
Each page is saved as a JSON file containing:
- Basic page information (URL, status, load time)
- Meta data analysis (title, description, keywords)
- Content analysis (word count, readability, language)
- Technical SEO metrics (canonical, schema, security)
- Performance metrics (Core Web Vitals simulation)
- Accessibility analysis
- Mobile optimization assessment

### Audit Report Example
```markdown
# 🎯 SEO AUDIT REPORT
**Domain: example.com**
**Generated:** 2024-01-15 10:30:00

## 📊 OVERALL SCORE: 78/100

### ✅ POSITIVE POINTS
- Strong technical SEO foundation
- Good mobile optimization
- Proper heading hierarchy

### 🚨 ISSUES FOUND
- 15% of images missing alt text
- Page load time above 3 seconds
- Missing meta descriptions on 3 pages

### 🛠️ ACTIONABLE NEXT STEPS
1. Optimize image alt attributes
2. Implement lazy loading for images
3. Add meta descriptions to missing pages
```

## 🌐 Multi-Language Support

The tool automatically detects and organizes content by language:
- **Detection methods**: HTML lang attribute, URL patterns, content analysis
- **Supported languages**: Greek (el), English (en), French (fr), German (de), Spanish (es), Italian (it)
- **Organization**: Separate folders for each detected language
- **Filtering**: Audit specific languages using `--language` parameter

## 🤖 AI Provider Comparison

| Feature | Ollama (Local) | ChatGPT (Cloud) |
|---------|----------------|-----------------|
| **Cost** | Free | Pay-per-use |
| **Privacy** | Complete | Data sent to OpenAI |
| **Speed** | Depends on hardware | Generally faster |
| **Quality** | Good with right model | Excellent |
| **Offline** | ✅ Yes | ❌ No |

## 🔧 Configuration

### Ollama Configuration
```bash
# Custom Ollama server
python seo_auditor.py /path/to/data --ollama-url http://localhost:11434

# Different model
python seo_auditor.py /path/to/data --model codellama:13b
```

### ChatGPT Configuration
```bash
# Custom API endpoint
python seo_auditor.py /path/to/data --provider chatgpt --openai-base-url https://api.openai.com/v1

# Different model
python seo_auditor.py /path/to/data --provider chatgpt --model gpt-4
```

## 🐛 Troubleshooting

### Common Issues

**Ollama Connection Failed**
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve
```

**Large Context Errors**
- The tool automatically handles large datasets by chunking
- Reduce crawl size with `--max-pages` for initial testing

**Memory Issues**
- Use `--mode overview` for lighter analysis
- Process single pages instead of full domains

**Timeout Issues**
- Increase timeout: `--timeout 300`
- Check network connectivity
- Use local Ollama instead of cloud APIs

## 📝 Examples

### Complete Workflow
```bash
# Step 1: Crawl website
python scrapper.py https://example.com --max-pages 30

# Step 2: List available languages
python seo_auditor.py ./crawl_data/example.com/2024-01-15_10-30-00 --list-languages

# Step 3: Audit Greek content with Ollama
python seo_auditor.py ./crawl_data/example.com/2024-01-15_10-30-00 --language el --provider ollama --output audit_el.md

# Step 4: Technical audit with ChatGPT
python seo_auditor.py ./crawl_data/example.com/2024-01-15_10-30-00 --mode technical --provider chatgpt --output technical_audit.md
```

### Single Page Analysis
```bash
# Analyze specific page
python seo_auditor.py ./crawl_data/example.com/2024-01-15_10-30-00/el/homepage.json --provider ollama
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 👨‍💻 Author

**Giannis Sakkoulas**  
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://coff.ee/sakkoulas)


🌐 [weborange.gr](https://weborange.gr)

---

*Built with ❤️ for the SEO community*
