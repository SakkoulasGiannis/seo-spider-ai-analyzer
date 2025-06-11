# 🎯 SEO Auditor με Ollama & ChatGPT

Αυτό το εργαλείο διαβάζει τα αποτελέσματα του scrapper και δημιουργεί λεπτομερές SEO audit χρησιμοποιώντας Ollama ή ChatGPT.

## 📋 Προαπαιτούμενα

### Επιλογή 1: Ollama (Local)
1. **Ollama εγκατεστημένο** και τρέχει στο σύστημά σας
2. **Model** κατεβασμένο στο Ollama (π.χ. deepseek-coder, llama2, κλπ)
3. **Python 3.7+**

### Επιλογή 2: ChatGPT (API)
1. **OpenAI API Key**
2. **Python 3.7+**

### Εγκατάσταση Ollama & Models

```bash
# Εγκατάσταση Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Κατέβασμα models
ollama pull deepseek-coder:6.7b
ollama pull llama2
ollama pull mistral

# Έλεγχος διαθέσιμων models
ollama list
```

### Εγκατάσταση ChatGPT
```bash
# Θέστε το OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Ή περάστε το ως παράμετρο
--openai-api-key "your-api-key-here"
```

### Εγκατάσταση Python dependencies

```bash
pip install -r requirements_auditor.txt
```

## 🚀 Χρήση

### Βασική χρήση (Ollama)
```bash
# Ανάλυση ολόκληρου φακέλου
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52

# Ανάλυση μεμονωμένης σελίδας
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52/el/etairia.json
```

### Με ChatGPT
```bash
# Ολόκληρος φάκελος με ChatGPT
export OPENAI_API_KEY="your-key"
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52 --provider chatgpt

# Μεμονωμένη σελίδα με ChatGPT
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52/el/etairia.json --provider chatgpt --openai-api-key "your-key"

# Με ChatGPT-4 για λεπτομερή ανάλυση
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52/el/etairia.json --provider chatgpt --model gpt-4
```

### Περισσότερες επιλογές
```bash
# Πλήρες audit με αποθήκευση σε αρχείο (φάκελος)
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52 --output audit_report.md

# Λεπτομερή ανάλυση μεμονωμένης σελίδας με αποθήκευση
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52/el/etairia.json --output etairia_audit.md

# Μόνο overview (για φακέλους)
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52 --mode overview

# Συγκεκριμένη γλώσσα (φάκελος)
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52 --language el

# Λίστα διαθέσιμων γλωσσών
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52 --list-languages

# Διαφορετικό Ollama model για μεμονωμένη σελίδα
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52/el/etairia.json --model llama2

# Custom Ollama server
python seo_auditor.py crawl_data/domain/2025-06-11_15-44-52 --ollama-url http://192.168.1.100:11434
```

## 📊 Τύποι Audit

### 🗂️ **Multi-Page Audit** (φάκελος)

#### 1. **Overview** (`--mode overview`)
- Συνολική βαθμολογία SEO
- Κύρια ευρήματα
- Κρίσιμα προβλήματα
- Top 5 συστάσεις

#### 2. **Technical** (`--mode technical`)
- Τεχνική βαθμολογία
- Performance issues
- Security προβλήματα
- Mobile optimization
- Άμεσες ενέργειες

#### 3. **Pages** (`--mode pages`)
- Σελίδα-σελίδα ανάλυση
- Ατομική βαθμολογία
- Προβλήματα ανά σελίδα
- Συγκεκριμένες συστάσεις

#### 4. **Full** (default)
- Όλα τα παραπάνω
- Συνολικό report
- Metadata crawl

### 📄 **Single Page Audit** (JSON αρχείο)

Για μεμονωμένα αρχεία, το audit είναι πάντα λεπτομερές και περιλαμβάνει:

- **🎯 Συνολική βαθμολογία** (0-100)
- **📊 Λεπτομερή ευρήματα** ανά κατηγορία
- **🔧 Τεχνικά στοιχεία** (performance, security, mobile)
- **📝 Περιεχόμενο** (title, meta, headings, content quality)
- **🔗 Linking** (internal/external links, anchor text)
- **📱 Mobile & Accessibility**
- **💡 Συστάσεις προτεραιότητας** (high/medium/low)
- **🎯 Actionable next steps**

## 🎛️ Παράμετροι

### LLM Provider Options
| Παράμετρος | Περιγραφή | Default |
|------------|-----------|---------|
| `--provider` | LLM Provider (ollama/chatgpt) | `ollama` |
| `--model` | Model name | `deepseek-coder:6.7b` |
| `--ollama-url` | URL του Ollama server | `http://localhost:11434` |
| `--openai-api-key` | OpenAI API Key για ChatGPT | None |
| `--openai-base-url` | OpenAI API Base URL | `https://api.openai.com/v1` |

### Audit Options
| Παράμετρος | Περιγραφή | Default |
|------------|-----------|---------|
| `path` | Φάκελος ή JSON αρχείο για ανάλυση | **Required** |
| `--output` | Αρχείο εξόδου για το report | None (εκτύπωση) |
| `--mode` | Τύπος audit (μόνο για φακέλους) | `full` |
| `--language` | Γλώσσα για ανάλυση (el, en, fr, de, es, it) | None (όλες) |
| `--list-languages` | Εμφάνιση διαθέσιμων γλωσσών | False |

## 🔧 Τεχνικές λεπτομέρειες

### Διαχείριση μεγάλων δεδομένων
- **Chunking**: Χωρίζει μεγάλα δεδομένα σε κομμάτια των 6KB
- **Summarization**: Συνοψίζει δεδομένα σελίδων για να χωρούν στο context
- **Pagination**: Αναλύει περιορισμένο αριθμό σελίδων για λεπτομερή audit

### Context Window Management
- Χρησιμοποιεί 8K context window
- Προτεραιοποιεί τα πιο σημαντικά SEO δεδομένα
- Αυτόματη περικοπή περιεχομένου

### Error Handling
- Graceful fallback αν δεν υπάρχει το επιθυμητό model
- Timeout protection (2 λεπτά ανά request)
- Validation των input φακέλων

## 📝 Παράδειγμα εξόδου

```markdown
# 📊 SEO AUDIT OVERVIEW

🎯 **Συνολική βαθμολογία SEO**: 72/100

📊 **Κύρια ευρήματα**:
✅ Καλή χρήση SSL σε όλες τις σελίδες
✅ Proper H1 structure
❌ 45% εικόνων χωρίς alt text
❌ Αργός χρόνος φόρτωσης (3.2s μέσος όρος)

🚨 **Κρίσιμα προβλήματα**:
1. Λείπουν meta descriptions σε 8 σελίδες
2. Duplicate H1 tags
3. Large image files (>500KB)

💡 **Top 5 συστάσεις**:
1. Προσθήκη alt text σε εικόνες
2. Βελτιστοποίηση εικόνων (WebP format)
3. Συμπίεση CSS/JS
4. Προσθήκη meta descriptions
5. Implement lazy loading
```

## ⚠️ Περιορισμοί

- **Model dependency**: Χρειάζεται Ollama με κατάλληλο model
- **Context limits**: Μεγάλα sites χωρίζονται σε chunks
- **Processing time**: 1-2 λεπτά ανά σελίδα
- **Memory usage**: Μπορεί να χρησιμοποιήσει αρκετή μνήμη για μεγάλα crawls

## 🔍 Troubleshooting

### Ollama connection errors
```bash
# Έλεγχος αν τρέχει το Ollama
ollama list

# Restart Ollama service
sudo systemctl restart ollama
```

### Memory issues
```bash
# Για μεγάλα crawls, χρησιμοποιήστε mode-specific audits
python seo_auditor.py folder --mode overview
```

### Model not found
```bash
# Download required model
ollama pull deepseek-coder
ollama pull llama2
```