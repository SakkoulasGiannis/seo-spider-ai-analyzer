#!/usr/bin/env python3
"""
SEO Auditor με Ollama & ChatGPT
Διαβάζει τα αποτελέσματα του scrapper και δημιουργεί SEO audit
"""

import json
import os
import sys
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Any
import time
from datetime import datetime
from abc import ABC, abstractmethod
from urllib.parse import urlparse

class LLMProvider(ABC):
    """Abstract base class για LLM providers"""
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Ελέγχει αν η σύνδεση είναι διαθέσιμη"""
        pass
    
    @abstractmethod
    def send_prompt(self, prompt: str, context: str = "") -> str:
        """Στέλνει prompt και επιστρέφει απάντηση"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict:
        """Επιστρέφει πληροφορίες για το model"""
        pass

class OllamaProvider(LLMProvider):
    """Ollama LLM Provider"""
    
    def __init__(self, url: str = "http://localhost:11434", model: str = "deepseek-coder:6.7b"):
        self.url = url.rstrip('/')
        self.model = model
        self.timeout = 180  # Default timeout
        
    def test_connection(self) -> bool:
        """Ελέγχει αν το Ollama είναι διαθέσιμο"""
        try:
            response = requests.get(f"{self.url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                print(f"✅ Ollama connected. Available models: {model_names}")
                
                # Check if our model is available
                if any(self.model in name for name in model_names):
                    print(f"✅ Model {self.model} is available")
                    return True
                else:
                    print(f"⚠️  Model {self.model} not found. Available: {model_names}")
                    # Use first available model
                    if model_names:
                        self.model = model_names[0].split(':')[0]
                        print(f"🔄 Switching to: {self.model}")
                        return True
                    return False
            return False
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            return False
    
    def send_prompt(self, prompt: str, context: str = "") -> str:
        """Στέλνει prompt στο Ollama"""
        full_prompt = f"{prompt}\n\nContext:\n{context}" if context else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_ctx": 8192
            }
        }
        
        try:
            print(f"🤖 Sending request to Ollama ({self.model})...")
            response = requests.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error sending to Ollama: {e}"
    
    def get_model_info(self) -> Dict:
        """Επιστρέφει πληροφορίες για το Ollama model"""
        return {
            "provider": "Ollama",
            "model": self.model,
            "url": self.url,
            "type": "local"
        }

class ChatGPTProvider(LLMProvider):
    """ChatGPT/OpenAI LLM Provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = 180  # Default timeout
        
    def test_connection(self) -> bool:
        """Ελέγχει αν το OpenAI API είναι διαθέσιμο"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models = response.json().get('data', [])
                model_ids = [m['id'] for m in models]
                print(f"✅ OpenAI API connected. Available models: {len(model_ids)} total")
                
                if self.model in model_ids:
                    print(f"✅ Model {self.model} is available")
                    return True
                else:
                    print(f"⚠️  Model {self.model} not found in your account")
                    # Try to use gpt-3.5-turbo as fallback
                    if "gpt-3.5-turbo" in model_ids:
                        self.model = "gpt-3.5-turbo"
                        print(f"🔄 Switching to: {self.model}")
                        return True
                    return False
            else:
                print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Cannot connect to OpenAI API: {e}")
            return False
    
    def send_prompt(self, prompt: str, context: str = "") -> str:
        """Στέλνει prompt στο ChatGPT"""
        
        # Combine prompt and context
        if context:
            messages = [
                {"role": "system", "content": "Είσαι ειδικός SEO auditor. Αναλύεις websites και δίνεις πρακτικές συστάσεις."},
                {"role": "user", "content": f"{prompt}\n\nContext:\n{context}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "Είσαι ειδικός SEO auditor. Αναλύεις websites και δίνεις πρακτικές συστάσεις."},
                {"role": "user", "content": prompt}
            ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"🤖 Sending request to ChatGPT ({self.model})...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error sending to ChatGPT: {e}"
    
    def get_model_info(self) -> Dict:
        """Επιστρέφει πληροφορίες για το ChatGPT model"""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "url": self.base_url,
            "type": "api"
        }

class SEOAuditor:
    def __init__(self, path: str, llm_provider: LLMProvider = None):
        self.path = Path(path)
        self.llm_provider = llm_provider
        self.single_file_mode = False
        self.single_file_data = None
        
        # Check if path is a single JSON file or folder
        if self.path.is_file() and self.path.suffix == '.json':
            # Single file mode
            self.single_file_mode = True
            self.crawl_folder = self.path.parent
            
            # Load the single JSON file
            with open(self.path, 'r', encoding='utf-8') as f:
                self.single_file_data = json.load(f)
            
            print(f"📄 Single page mode: {self.path.name}")
            print(f"📁 From crawl: {self.crawl_folder}")
            
            # Try to load summary from parent folder
            self.summary = {}
            for potential_summary in [
                self.crawl_folder / "_summary.json",           # Same folder
                self.crawl_folder.parent / "_summary.json",    # Parent folder (if in language subfolder)
                self.crawl_folder.parent.parent / "_summary.json"  # Grandparent folder
            ]:
                if potential_summary.exists():
                    with open(potential_summary, 'r', encoding='utf-8') as f:
                        self.summary = json.load(f)
                    break
                    
        else:
            # Folder mode (original behavior)
            self.crawl_folder = self.path
            
            # Validation
            if not self.crawl_folder.exists():
                raise FileNotFoundError(f"Crawl folder not found: {path}")
            
            # Load summary if exists
            summary_file = self.crawl_folder / "_summary.json"
            self.summary = {}
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    self.summary = json.load(f)
            
            print(f"📁 Loaded crawl data from: {self.crawl_folder}")
        
        if self.llm_provider:
            model_info = self.llm_provider.get_model_info()
            print(f"🤖 Using {model_info['provider']}: {model_info['model']}")
        else:
            print("⚠️  No LLM provider configured")
    
    def test_llm_connection(self) -> bool:
        """Ελέγχει αν το LLM provider είναι διαθέσιμο"""
        if not self.llm_provider:
            print("❌ No LLM provider configured")
            return False
        return self.llm_provider.test_connection()
    
    def send_to_llm(self, prompt: str, context: str = "") -> str:
        """Στέλνει prompt στο LLM provider και επιστρέφει την απάντηση"""
        if not self.llm_provider:
            return "❌ No LLM provider configured"
        
        # Check context size and handle large contexts
        if len(context) > 6000:
            print("⚠️  Large context detected, using chunked analysis")
            return self.chunked_analysis(prompt, context)
        
        return self.llm_provider.send_prompt(prompt, context)
    
    def chunked_analysis(self, prompt: str, context: str) -> str:
        """Χειρίζεται μεγάλα contexts με chunking"""
        try:
            # Split context into manageable chunks
            context_data = json.loads(context)
            
            # Create a simplified summary for analysis
            if isinstance(context_data, dict):
                simplified_context = {}
                
                # Keep only essential data
                essential_keys = ['basic_info', 'content_metrics', 'technical_metrics', 'images_and_links']
                for key in essential_keys:
                    if key in context_data:
                        simplified_context[key] = context_data[key]
                
                # Add a sample of detailed data if available
                if 'headings_sample' in context_data:
                    simplified_context['headings_sample'] = context_data['headings_sample'][:5]
                
                if 'content_quality' in context_data:
                    content_quality = context_data['content_quality'].copy()
                    if 'keyword_analysis' in content_quality:
                        content_quality['keyword_analysis'] = content_quality['keyword_analysis'][:3]
                    simplified_context['content_quality'] = content_quality
                
                simplified_json = json.dumps(simplified_context, ensure_ascii=False, indent=2)
                
                # Add note about simplified analysis
                modified_prompt = prompt + "\n\n⚠️ **Σημείωση**: Λόγω μεγέθους δεδομένων, η ανάλυση βασίζεται σε τα πιο σημαντικά στοιχεία."
                
                return self.llm_provider.send_prompt(modified_prompt, simplified_json)
            else:
                # Fallback to basic summary
                return self.llm_provider.send_prompt(prompt, context[:4000] + "...")
                
        except Exception as e:
            print(f"⚠️  Chunked analysis failed: {e}")
            # Fallback to truncated context
            return self.llm_provider.send_prompt(prompt, context[:4000] + "...")
    
    def load_page_data(self, language: str = None) -> List[Dict]:
        """Φορτώνει όλα τα JSON αρχεία από τον φάκελο (με υποστήριξη γλωσσών)"""
        page_files = []
        
        # Single file mode
        if self.single_file_mode:
            detected_lang = self.single_file_data.get('detected_language', 'unknown')
            
            # Filter by language if specified
            if language and detected_lang != language:
                print(f"⚠️  Single file language '{detected_lang}' doesn't match requested '{language}'")
                return []
            
            page_files.append({
                'filename': self.path.name,
                'language': detected_lang,
                'data': self.single_file_data
            })
            
            print(f"📄 Single file loaded: {self.path.name} (language: {detected_lang})")
            return page_files
        
        # Folder mode (original behavior)
        # Check for language-based folder structure first
        language_folders = [folder for folder in self.crawl_folder.iterdir() if folder.is_dir()]
        
        if language_folders:
            # New structure with language folders
            folders_to_process = []
            
            if language:
                # Load specific language
                lang_folder = self.crawl_folder / language
                if lang_folder.exists():
                    folders_to_process = [lang_folder]
                else:
                    print(f"⚠️  Language folder '{language}' not found")
                    return []
            else:
                # Load all languages
                folders_to_process = language_folders
            
            for lang_folder in folders_to_process:
                lang_code = lang_folder.name
                for json_file in lang_folder.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            page_files.append({
                                'filename': json_file.name,
                                'language': lang_code,
                                'data': data
                            })
                    except Exception as e:
                        print(f"⚠️  Error loading {json_file}: {e}")
        else:
            # Fallback to old structure (root folder)
            for json_file in self.crawl_folder.glob("*.json"):
                if json_file.name != "_summary.json":
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            detected_lang = data.get('detected_language', 'unknown')
                            
                            # Filter by language if specified
                            if language and detected_lang != language:
                                continue
                                
                            page_files.append({
                                'filename': json_file.name,
                                'language': detected_lang,
                                'data': data
                            })
                    except Exception as e:
                        print(f"⚠️  Error loading {json_file}: {e}")
        
        if language:
            print(f"📄 Loaded {len(page_files)} page files for language '{language}'")
        else:
            print(f"📄 Loaded {len(page_files)} page files from all languages")
        
        return page_files
    
    def summarize_page_data(self, page_data: Dict) -> Dict:
        """Συνοπτική περίληψη σημαντικών SEO δεδομένων μιας σελίδας"""
        url = page_data.get('url', 'Unknown')
        
        # Basic meta
        meta = page_data.get('meta_data', {})
        
        # Headings
        headings = page_data.get('headings', {})
        
        # Images
        images = page_data.get('images', {})
        
        # Links
        links = page_data.get('links', {})
        
        # Content
        content = page_data.get('content_analysis', {})
        
        # Performance
        perf = page_data.get('performance_metrics', {})
        
        # Technical SEO
        tech = page_data.get('technical_seo', {})
        
        summary = {
            'url': url,
            'title': meta.get('title', '')[:100],  # Limit length
            'title_length': meta.get('title_length', 0),
            'description': meta.get('description', '')[:200],  # Limit length
            'description_length': meta.get('description_length', 0),
            'h1_count': headings.get('h1_count', 0),
            'total_headings': headings.get('total_headings', 0),
            'word_count': content.get('total_word_count', 0),
            'images_total': images.get('total_images', 0),
            'images_without_alt': images.get('images_without_alt', 0),
            'internal_links': links.get('total_internal', 0),
            'external_links': links.get('total_external', 0),
            'page_size_kb': perf.get('content_size_kb', 0),
            'load_time_ms': perf.get('response_time_ms', 0),
            'has_canonical': tech.get('has_canonical', False),
            'has_ssl': tech.get('has_ssl', False),
            'status_code': page_data.get('status_code', 0)
        }
        
        return summary
    
    def chunk_data(self, data: str, max_chars: int = 6000) -> List[str]:
        """Χωρίζει μεγάλα δεδομένα σε chunks"""
        if len(data) <= max_chars:
            return [data]
        
        chunks = []
        words = data.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_chars:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
                else:
                    # Single word too long, force add
                    chunks.append(word[:max_chars])
                    current_chunk = []
                    current_length = 0
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def audit_overview(self) -> str:
        """Δημιουργεί γενικό SEO audit overview"""
        if not self.summary:
            return "❌ No summary data available for overview audit"
        
        prompt = """You are an experienced SEO expert. Perform a detailed audit of the following web page:

        URL: {page_summary['url']}

        Your response must include:

        ## OVERALL SCORE (0–100)
        ## DETAILED FINDINGS

        ### POSITIVE POINTS
        - What the page does well

        ### ISSUES FOUND
        - Critical and medium-priority SEO problems

        ### TECHNICAL METRICS
        - Load speed
        - Mobile optimization
        - Security and HTTPS
        - Structured data and technical SEO tags

        ### CONTENT ANALYSIS
        - Title and meta description quality
        - Heading structure
        - Keyword usage
        - Content depth and clarity
        - **Content Relevance & Search Intent**
            - Does the content satisfy the intent behind likely search queries?
            - What type of user is this content targeting?
            - If the content is lacking, **explain what is missing**.
            - **Provide improved examples**: suggest a better paragraph, title, or CTA based on the expected user intent.

        ### LINKING STRUCTURE
        - Internal links and their quality
        - External links and anchor text relevance

        ### MOBILE & ACCESSIBILITY
        - Mobile usability
        - Accessibility issues

        ## RECOMMENDATIONS (WITH EXAMPLES)
        1. Immediate (high-priority) fixes with examples
        2. Mid-term improvements
        3. Long-term content or UX suggestions

        ## ACTIONABLE NEXT STEPS
        Give clear, specific instructions, including improved content examples if possible (e.g., “Replace paragraph X with...” or “Add a comparison table between A and B”).

        Respond in Greek as the page content, use markdown formatting and emojis where helpful. Be as specific and example-driven as possible."""


        context = json.dumps(self.summary, ensure_ascii=False, indent=2)
        
        return self.send_to_llm(prompt, context)
    
    def audit_single_page(self) -> str:
        """Αναλύει μια μεμονωμένη σελίδα σε βάθος"""
        if not self.single_file_mode:
            return "❌ Single page audit only available in single file mode"
        
        page_summary = self.summarize_page_data(self.single_file_data)
        
        prompt = f"""You are an experienced SEO expert. Perform a detailed audit of the following web page:

        URL: {page_summary['url']}

        Your response must include:

        ## OVERALL SCORE (0–100)
        ## DETAILED FINDINGS

        ### POSITIVE POINTS
        - What the page does well

        ### ISSUES FOUND
        - Critical and medium-priority SEO problems

        ### TECHNICAL METRICS
        - Load speed
        - Mobile optimization
        - Security and HTTPS
        - Structured data and technical SEO tags

        ### CONTENT ANALYSIS
        - Title and meta description quality
        - Heading structure
        - Keyword usage
        - Content depth and clarity
        - **Content Relevance & Search Intent**
           - Does the content satisfy the intent behind likely search queries?
           - What type of user is this content targeting?
           - If the content is lacking, **explain what is missing**.
           - **Provide improved examples**: suggest a better paragraph, title, or CTA based on the expected user intent.

        ### LINKING STRUCTURE
        - Internal links and their quality
        - External links and anchor text relevance

        ### MOBILE & ACCESSIBILITY
        - Mobile usability
        - Accessibility issues

        ## RECOMMENDATIONS (WITH EXAMPLES)
        1. Immediate (high-priority) fixes with examples
        2. Mid-term improvements
        3. Long-term content or UX suggestions

        ## ACTIONABLE NEXT STEPS
        Give clear, specific instructions, including improved content examples if possible (e.g., “Replace paragraph X with...” or “Add a comparison table between A and B”).

        Respond in Greek as the page content, use markdown formatting and emojis where helpful. Be as specific and example-driven as possible."""
                
        # Create optimized context for single page analysis
        context = self.create_optimized_context(page_summary)
        
        return self.send_to_llm(prompt, context)
    
    def create_optimized_context(self, page_summary: Dict) -> str:
        """Δημιουργεί βελτιστοποιημένο context για ανάλυση"""
        # Create a focused context with the most important SEO data
        optimized_data = {
            'basic_info': {
                'url': page_summary['url'],
                'title': page_summary['title'],
                'title_length': page_summary['title_length'],
                'description': page_summary['description'],
                'description_length': page_summary['description_length'],
                'status_code': page_summary['status_code']
            },
            'content_metrics': {
                'word_count': page_summary['word_count'],
                'h1_count': page_summary['h1_count'],
                'total_headings': page_summary['total_headings']
            },
            'technical_metrics': {
                'page_size_kb': page_summary['page_size_kb'],
                'load_time_ms': page_summary['load_time_ms'],
                'has_canonical': page_summary['has_canonical'],
                'has_ssl': page_summary['has_ssl']
            },
            'images_and_links': {
                'images_total': page_summary['images_total'],
                'images_without_alt': page_summary['images_without_alt'],
                'internal_links': page_summary['internal_links'],
                'external_links': page_summary['external_links']
            }
        }
        
        # Add detailed data if available and not too large
        if self.single_file_data:
            # Add key detailed sections that are manageable
            try:
                # Meta data
                meta_data = self.single_file_data.get('meta_data', {})
                if meta_data:
                    optimized_data['meta_details'] = {
                        'viewport': meta_data.get('viewport', ''),
                        'robots': meta_data.get('robots', ''),
                        'charset': meta_data.get('charset', '')
                    }
                
                # Headings structure (first 10 only)
                headings = self.single_file_data.get('headings', {})
                if headings and headings.get('structure'):
                    optimized_data['headings_sample'] = headings['structure'][:10]
                
                # Content analysis (key metrics only)
                content_analysis = self.single_file_data.get('content_analysis', {})
                if content_analysis:
                    optimized_data['content_quality'] = {
                        'reading_time_minutes': content_analysis.get('reading_time_minutes', 0),
                        'language_detection': content_analysis.get('language_detection', {}),
                        'keyword_analysis': content_analysis.get('keyword_analysis', {}).get('top_keywords', [])[:5]
                    }
                
                # Technical SEO
                technical_seo = self.single_file_data.get('technical_seo', {})
                if technical_seo:
                    optimized_data['seo_technical'] = {
                        'canonical_url': technical_seo.get('canonical_url', ''),
                        'has_favicon': technical_seo.get('has_favicon', False),
                        'has_hreflang': technical_seo.get('has_hreflang', False)
                    }
                
                # Performance metrics
                performance = self.single_file_data.get('performance_metrics', {})
                if performance:
                    optimized_data['performance_details'] = {
                        'gzip_enabled': performance.get('gzip_enabled', False),
                        'security_score': performance.get('security_headers', {}).get('security_score', 0)
                    }
                
                # Mobile optimization
                mobile = self.single_file_data.get('mobile_optimization', {})
                if mobile:
                    optimized_data['mobile_details'] = {
                        'mobile_optimization_score': mobile.get('mobile_optimization_score', 0),
                        'has_viewport_meta': mobile.get('has_viewport_meta', False),
                        'viewport_content': mobile.get('viewport_content', '')
                    }
                
            except Exception as e:
                print(f"⚠️  Warning: Could not extract detailed data: {e}")
        
        # Convert to JSON with size limit
        context = json.dumps(optimized_data, ensure_ascii=False, indent=2)
        
        # Final size check - if still too large, use basic summary only
        if len(context) > 4000:
            print("⚠️  Large data detected, using summarized context")
            context = json.dumps(optimized_data['basic_info'], ensure_ascii=False, indent=2)
        
        return context

    def audit_page_by_page(self, max_pages: int = 5) -> str:
        """Αναλύει σελίδα-σελίδα (περιορισμένος αριθμός λόγω μεγέθους)"""
        # If single file mode, use the detailed single page audit
        if self.single_file_mode:
            return self.audit_single_page()
        
        page_files = self.load_page_data()
        
        if not page_files:
            return "❌ No page data found for detailed audit"
        
        # Limit number of pages to analyze
        pages_to_analyze = page_files[:max_pages]
        
        results = []
        
        for i, page_file in enumerate(pages_to_analyze, 1):
            print(f"🔍 Analyzing page {i}/{len(pages_to_analyze)}: {page_file['filename']}")
            
            # Summarize page data
            page_summary = self.summarize_page_data(page_file['data'])
            
            prompt = f"""You are an experienced SEO expert. Perform a detailed audit of the following web page:

            URL: {page_summary['url']}

            Your response must include:

            ## OVERALL SCORE (0–100)
            ## DETAILED FINDINGS

            ### POSITIVE POINTS
            - What the page does well

            ### ISSUES FOUND
            - Critical and medium-priority SEO problems

            ### TECHNICAL METRICS
            - Load speed
            - Mobile optimization
            - Security and HTTPS
            - Structured data and technical SEO tags

            ### CONTENT ANALYSIS
            - Title and meta description quality
            - Heading structure
            - Keyword usage
            - Content depth and clarity
            - **Content Relevance & Search Intent**
               - Does the content satisfy the intent behind likely search queries?
               - What type of user is this content targeting?
               - If the content is lacking, **explain what is missing**.
               - **Provide improved examples**: suggest a better paragraph, title, or CTA based on the expected user intent.

            ### LINKING STRUCTURE
            - Internal links and their quality
            - External links and anchor text relevance

            ### MOBILE & ACCESSIBILITY
            - Mobile usability
            - Accessibility issues

            ## RECOMMENDATIONS (WITH EXAMPLES)
            1. Immediate (high-priority) fixes with examples
            2. Mid-term improvements
            3. Long-term content or UX suggestions

            ## ACTIONABLE NEXT STEPS
            Give clear, specific instructions, including improved content examples if possible (e.g., “Replace paragraph X with...” or “Add a comparison table between A and B”).

            Respond in Greek as the page content, use markdown formatting and emojis where helpful. Be as specific and example-driven as possible."""


            
            context = json.dumps(page_summary, ensure_ascii=False, indent=2)
            
            audit_result = self.send_to_llm(prompt, context)
            results.append(f"## Page {i}: {page_summary['url']}\n\n{audit_result}\n\n---\n")
            
            # Small delay to avoid overwhelming LLM
            time.sleep(1)
        
        return "\n".join(results)
    
    def audit_technical_seo(self) -> str:
        """Εστιάζει στα τεχνικά SEO στοιχεία"""
        page_files = self.load_page_data()
        
        if not page_files:
            return "❌ No page data found for technical audit"
        
        # Collect technical data from all pages
        technical_issues = []
        
        for page_file in page_files:
            data = page_file['data']
            url = data.get('url', 'Unknown')
            
            # Extract technical issues
            issues = {
                'url': url,
                'status_code': data.get('status_code', 0),
                'has_canonical': data.get('technical_seo', {}).get('has_canonical', False),
                'has_ssl': data.get('technical_seo', {}).get('has_ssl', False),
                'load_time': data.get('performance_metrics', {}).get('response_time_ms', 0),
                'page_size': data.get('performance_metrics', {}).get('content_size_kb', 0),
                'security_score': data.get('performance_metrics', {}).get('security_headers', {}).get('security_score', 0),
                'mobile_score': data.get('mobile_optimization', {}).get('mobile_optimization_score', 0)
            }
            
            technical_issues.append(issues)
        
        prompt = """Είσαι τεχνικός SEO ειδικός. Ανάλυσε τα τεχνικά δεδομένα και παράγε report:

Παρέχεις:
1. 🔧 **Τεχνική βαθμολογία** (0-100)
2. 🚨 **Κρίσιμα τεχνικά προβλήματα**
3. ⚡ **Performance issues**
4. 🔒 **Security προβλήματα**
5. 📱 **Mobile optimization status**
6. 🛠️ **Άμεσες ενέργειες** (priοritized list)

Απάντησε στα ελληνικά με πρακτικές συστάσεις."""
        
        context = json.dumps(technical_issues[:10], ensure_ascii=False, indent=2)  # Limit to 10 pages
        
        return self.send_to_llm(prompt, context)
    
    def generate_full_audit(self, output_file: str = None) -> str:
        """Δημιουργεί πλήρες SEO audit"""
        print("🎯 Starting comprehensive SEO audit...")
        
        audit_results = []
        
        if self.single_file_mode:
            # Single page detailed audit
            print("📄 Performing detailed single page analysis...")
            single_page_audit = self.audit_single_page()
            audit_results.append("# 📄 DETAILED PAGE ANALYSIS\n\n" + single_page_audit)
            
            # Get page info
            url = self.single_file_data.get('url', 'Unknown')
            domain = urlparse(url).netloc if url != 'Unknown' else 'Unknown'
            page_title = f"Single Page: {self.path.name}"
        else:
            # Multi-page audit (original behavior)
            # 1. Overview Audit
            print("📊 Generating overview audit...")
            overview = self.audit_overview()
            audit_results.append("# 📊 SEO AUDIT OVERVIEW\n\n" + overview)
            
            # 2. Technical SEO Audit
            print("🔧 Analyzing technical SEO...")
            technical = self.audit_technical_seo()
            audit_results.append("# 🔧 TECHNICAL SEO ANALYSIS\n\n" + technical)
            
            # 3. Page-by-Page Analysis (limited)
            print("📄 Analyzing individual pages...")
            page_analysis = self.audit_page_by_page(max_pages=3)
            audit_results.append("# 📄 PAGE-BY-PAGE ANALYSIS (Sample)\n\n" + page_analysis)
            
            # Get domain info
            domain = self.summary.get('crawl_info', {}).get('domain', 'Unknown')
            page_title = f"Domain: {domain}"
        
        # Combine all results
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get LLM info
        if self.llm_provider:
            model_info = self.llm_provider.get_model_info()
            llm_info = f"{model_info['provider']} {model_info['model']}"
        else:
            llm_info = "No LLM Provider"
        
        audit_type = "Single Page" if self.single_file_mode else "Multi-Page"
        pages_analyzed = 1 if self.single_file_mode else self.summary.get('crawl_info', {}).get('total_pages_crawled', 0)
        
        full_audit = f"""# 🎯 SEO AUDIT REPORT
**{page_title}**  
**Audit Type:** {audit_type}  
**Generated:** {timestamp}  
**Audit Tool:** SEO Auditor + {llm_info}  

---

{chr(10).join(audit_results)}

---

## 📋 AUDIT METADATA
- **Source:** {self.path}
- **Pages analyzed:** {pages_analyzed}
- **LLM Provider:** {llm_info}
- **Generation time:** {timestamp}
"""
        
        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_audit)
            print(f"💾 Full audit saved to: {output_path}")
        
        return full_audit

def main():
    parser = argparse.ArgumentParser(description="SEO Auditor με Ollama & ChatGPT")
    parser.add_argument("path", help="Φάκελος με crawl δεδομένα ή μεμονωμένο JSON αρχείο")
    
    # LLM Provider options
    llm_group = parser.add_argument_group('LLM Provider Options')
    llm_group.add_argument("--provider", choices=['ollama', 'chatgpt'], default='ollama', 
                          help="LLM Provider (default: ollama)")
    llm_group.add_argument("--model", default="deepseek-coder:6.7b", 
                          help="Model name (Ollama: deepseek-coder:6.7b, ChatGPT: gpt-3.5-turbo)")
    llm_group.add_argument("--ollama-url", default="http://localhost:11434", 
                          help="Ollama server URL")
    llm_group.add_argument("--openai-api-key", help="OpenAI API Key (για ChatGPT)")
    llm_group.add_argument("--openai-base-url", default="https://api.openai.com/v1", 
                          help="OpenAI API Base URL")
    
    # Audit options
    audit_group = parser.add_argument_group('Audit Options')
    audit_group.add_argument("--output", help="Output file για το audit report")
    audit_group.add_argument("--mode", choices=['overview', 'technical', 'pages', 'full'], 
                            default='full', help="Τύπος audit")
    audit_group.add_argument("--language", help="Ανάλυση συγκεκριμένης γλώσσας (el, en, fr, de, es, it)")
    audit_group.add_argument("--list-languages", action="store_true", help="Εμφάνιση διαθέσιμων γλωσσών")
    audit_group.add_argument("--timeout", type=int, default=180, help="Timeout σε δευτερόλεπτα (default: 180)")
    
    args = parser.parse_args()
    
    try:
        # Create LLM Provider based on choice
        llm_provider = None
        
        if args.provider == 'ollama':
            llm_provider = OllamaProvider(args.ollama_url, args.model)
            llm_provider.timeout = args.timeout  # Set custom timeout
        elif args.provider == 'chatgpt':
            if not args.openai_api_key:
                # Try to get from environment
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    print("❌ OpenAI API key required for ChatGPT. Use --openai-api-key or set OPENAI_API_KEY env var")
                    sys.exit(1)
            else:
                api_key = args.openai_api_key
            
            llm_provider = ChatGPTProvider(api_key, args.model, args.openai_base_url)
            llm_provider.timeout = args.timeout  # Set custom timeout
        
        # Initialize auditor
        auditor = SEOAuditor(args.path, llm_provider)
        
        # Handle list languages request
        if args.list_languages:
            if auditor.single_file_mode:
                detected_lang = auditor.single_file_data.get('detected_language', 'unknown')
                print(f"🌍 Single file language: {detected_lang}")
            else:
                print("🌍 Available languages in crawl data:")
                lang_dist = auditor.summary.get('crawl_info', {}).get('language_distribution', {})
                if lang_dist:
                    for lang, stats in lang_dist.items():
                        print(f"  {lang}: {stats['pages']} pages")
                else:
                    # Check folders directly
                    language_folders = [folder.name for folder in auditor.crawl_folder.iterdir() if folder.is_dir()]
                    if language_folders:
                        print(f"  Found language folders: {', '.join(language_folders)}")
                    else:
                        print("  No language-specific organization found")
            sys.exit(0)
        
        # Test connection
        if not auditor.test_llm_connection():
            print("❌ Cannot proceed without LLM connection")
            sys.exit(1)
        
        # Store language filter
        auditor.language_filter = args.language
        
        # Run audit based on mode
        if args.mode == 'overview':
            result = auditor.audit_overview()
        elif args.mode == 'technical':
            result = auditor.audit_technical_seo()
        elif args.mode == 'pages':
            result = auditor.audit_page_by_page()
        else:  # full
            result = auditor.generate_full_audit(args.output)
        
        # Print result
        print("\n" + "="*50)
        print("🎯 SEO AUDIT RESULTS")
        print("="*50)
        print(result)
        
    except KeyboardInterrupt:
        print("\n⏹️  Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
