import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import hashlib
from pathlib import Path
import logging
import argparse
import sys
from typing import Dict, List, Set, Optional

class SEOScraper:
    def __init__(self, base_url: str, output_dir: str = "crawl_data"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create timestamp for this crawl
        self.crawl_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.crawl_dir = Path(self.output_dir) / self.domain / self.crawl_timestamp
        self.crawl_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.crawl_dir / 'crawl.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Tracking
        self.visited_urls: Set[str] = set()
        self.to_crawl: Set[str] = set()
        self.errors: List[Dict] = []
        self.pages_data: Dict[str, Dict] = {}
        
    def is_internal_url(self, url: str) -> bool:
        """Ελέγχει αν το URL είναι εσωτερικό"""
        if not url:
            return False
            
        parsed = urlparse(url)
        
        # If no domain, it's relative (internal)
        if not parsed.netloc:
            return True
            
        # Check if same domain
        return parsed.netloc.lower() == self.domain.lower()
    
    def url_to_filename(self, url: str) -> str:
        """Μετατρέπει URL σε safe filename"""
        # Remove protocol and domain
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Handle homepage
        if not path or path == '/':
            return 'homepage.json'
        
        # Clean path and create filename
        path = path.strip('/')
        
        # Replace slashes with underscores
        filename = path.replace('/', '_')
        
        # Remove or replace problematic characters
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        
        # Ensure it ends with .json
        if not filename.endswith('.json'):
            filename += '.json'
            
        # Handle very long filenames
        if len(filename) > 100:
            filename = filename[:95] + '.json'
            
        return filename
    
    def extract_page_data(self, url: str, response: requests.Response) -> Dict:
        """Εξάγει όλα τα SEO δεδομένα από μία σελίδα"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Basic page info
        page_data = {
            'url': url,
            'status_code': response.status_code,
            'timestamp': time.time(),
            'page_size': len(response.content),
            'load_time': response.elapsed.total_seconds(),
            'crawl_date': self.crawl_timestamp
        }
        
        # Meta data
        page_data['meta_data'] = self.extract_meta_data(soup)
        
        # Headings
        page_data['headings'] = self.extract_headings(soup)
        
        # Images
        page_data['images'] = self.extract_images(soup, url)
        
        # Links
        page_data['links'] = self.extract_links(soup, url)
        
        # Content analysis
        page_data['content_analysis'] = self.extract_content_analysis(soup)
        
        # Technical SEO
        page_data['technical_seo'] = self.extract_technical_seo(soup, response)
        
        # Social meta
        page_data['social_meta'] = self.extract_social_meta(soup)
        
        # Schema markup
        page_data['schema_markup'] = self.extract_schema_markup(soup)
        
        # Performance metrics
        page_data['performance_metrics'] = {
            'response_time_ms': response.elapsed.total_seconds() * 1000,
            'content_size_kb': len(response.content) / 1024,
            'gzip_enabled': 'gzip' in response.headers.get('Content-Encoding', ''),
            'cache_headers': self.extract_cache_headers(response),
            'security_headers': self.extract_security_headers(response)
        }
        
        # Advanced SEO analysis
        page_data['advanced_seo'] = self.extract_advanced_seo(soup, response)
        
        # Accessibility analysis
        page_data['accessibility'] = self.extract_accessibility_analysis(soup)
        
        # Mobile optimization
        page_data['mobile_optimization'] = self.extract_mobile_optimization(soup)
        
        # Internal linking analysis
        page_data['internal_linking'] = self.analyze_internal_linking(soup, url)
        
        # Page speed insights simulation
        page_data['page_speed_insights'] = self.simulate_page_speed_insights(response, soup)
        
        # Competitive analysis data
        page_data['competitive_analysis'] = self.extract_competitive_signals(soup)
        
        # Core Web Vitals simulation
        page_data['core_web_vitals'] = self.simulate_core_web_vitals(response, soup)
        
        return page_data
    
    def extract_meta_data(self, soup: BeautifulSoup) -> Dict:
        """Εξάγει meta δεδομένα"""
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ''
        
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag.get('content', '').strip() if description_tag else ''
        
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords_tag.get('content', '').strip() if keywords_tag else None
        
        return {
            'title': title,
            'title_length': len(title),
            'description': description,
            'description_length': len(description),
            'keywords': keywords,
            'charset': self.get_charset(soup),
            'viewport': self.get_viewport(soup),
            'robots': self.get_robots(soup)
        }
    
    def extract_headings(self, soup: BeautifulSoup) -> Dict:
        """Εξάγει headings structure"""
        headings = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        structure = []
        
        for level in range(1, 7):
            tags = soup.find_all(f'h{level}')
            for tag in tags:
                text = tag.get_text().strip()
                heading_data = {'text': text, 'length': len(text)}
                headings[f'h{level}'].append(heading_data)
                structure.append({'level': level, 'text': text, 'length': len(text)})
        
        return {
            'headings': headings,
            'structure': structure,
            'h1_count': len(headings['h1']),
            'total_headings': sum(len(headings[f'h{i}']) for i in range(1, 7))
        }
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Εξάγει image δεδομένα"""
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src', '')
            if src:
                src = urljoin(base_url, src)
            
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'has_alt': bool(img.get('alt')),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', '')
            })
        
        images_without_alt = sum(1 for img in images if not img['has_alt'])
        images_with_lazy_loading = sum(1 for img in images if img['loading'] == 'lazy')
        
        return {
            'images': images,
            'total_images': len(images),
            'images_without_alt': images_without_alt,
            'images_with_lazy_loading': images_with_lazy_loading
        }
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Εξάγει link δεδομένα"""
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            
            # Skip empty hrefs, javascript, mailto, tel
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
                
            full_url = urljoin(base_url, href)
            
            # Clean URL (remove fragments)
            if '#' in full_url:
                full_url = full_url.split('#')[0]
            
            link_data = {
                'url': full_url,
                'text': link.get_text().strip(),
                'title': link.get('title', ''),
                'rel': link.get('rel', []),
                'target': link.get('target', ''),
                'is_nofollow': 'nofollow' in link.get('rel', [])
            }
            
            if self.is_internal_url(full_url):
                internal_links.append(link_data)
                # Add to crawl queue if not already visited or queued
                if full_url not in self.visited_urls and full_url not in self.to_crawl:
                    self.to_crawl.add(full_url)
                    self.logger.debug(f"Added to crawl queue: {full_url}")
            else:
                external_links.append(link_data)
        
        return {
            'internal_links': internal_links,
            'external_links': external_links,
            'total_internal': len(internal_links),
            'total_external': len(external_links),
            'nofollow_links': sum(1 for link in internal_links + external_links if link['is_nofollow'])
        }
    
    def detect_page_language(self, soup: BeautifulSoup, url: str) -> str:
        """Ανιχνεύει τη γλώσσα της σελίδας"""
        # 1. Check HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            lang = html_tag.get('lang').lower()
            if lang.startswith('el'):
                return 'el'
            elif lang.startswith('en'):
                return 'en'
            elif lang.startswith('fr'):
                return 'fr'
            elif lang.startswith('de'):
                return 'de'
            elif lang.startswith('es'):
                return 'es'
            elif lang.startswith('it'):
                return 'it'
        
        # 2. Check URL patterns
        url_lower = url.lower()
        if '/el/' in url_lower or '/gr/' in url_lower or url_lower.endswith('/el') or url_lower.endswith('/gr'):
            return 'el'
        elif '/en/' in url_lower or url_lower.endswith('/en'):
            return 'en'
        elif '/fr/' in url_lower or url_lower.endswith('/fr'):
            return 'fr'
        elif '/de/' in url_lower or url_lower.endswith('/de'):
            return 'de'
        elif '/es/' in url_lower or url_lower.endswith('/es'):
            return 'es'
        elif '/it/' in url_lower or url_lower.endswith('/it'):
            return 'it'
        
        # 3. Content-based language detection
        full_text = soup.get_text()
        greek_chars = len(re.findall(r'[Α-Ωα-ωάέήίόύώ]', full_text))
        english_chars = len(re.findall(r'[A-Za-z]', full_text))
        french_chars = len(re.findall(r'[àâäéèêëïîôöùûüÿç]', full_text, re.I))
        german_chars = len(re.findall(r'[äöüß]', full_text, re.I))
        spanish_chars = len(re.findall(r'[ñáéíóúü]', full_text, re.I))
        italian_chars = len(re.findall(r'[àèéìíîòóù]', full_text, re.I))
        
        total_special_chars = greek_chars + french_chars + german_chars + spanish_chars + italian_chars
        
        if total_special_chars > 0:
            if greek_chars > max(french_chars, german_chars, spanish_chars, italian_chars):
                return 'el'
            elif french_chars > max(german_chars, spanish_chars, italian_chars):
                return 'fr'
            elif german_chars > max(spanish_chars, italian_chars):
                return 'de'
            elif spanish_chars > italian_chars:
                return 'es'
            elif italian_chars > 0:
                return 'it'
        
        # 4. Common words detection
        text_lower = full_text.lower()
        greek_words = ['και', 'είναι', 'για', 'από', 'στο', 'στη', 'με', 'που', 'αυτό', 'μας', 'σας']
        english_words = ['the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'they', 'have']
        french_words = ['le', 'de', 'et', 'dans', 'les', 'des', 'est', 'pour', 'que', 'une']
        german_words = ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich']
        spanish_words = ['el', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te']
        italian_words = ['il', 'di', 'che', 'e', 'la', 'per', 'in', 'un', 'è', 'non']
        
        greek_score = sum(1 for word in greek_words if word in text_lower)
        english_score = sum(1 for word in english_words if word in text_lower)
        french_score = sum(1 for word in french_words if word in text_lower)
        german_score = sum(1 for word in german_words if word in text_lower)
        spanish_score = sum(1 for word in spanish_words if word in text_lower)
        italian_score = sum(1 for word in italian_words if word in text_lower)
        
        scores = {
            'el': greek_score,
            'en': english_score,
            'fr': french_score,
            'de': german_score,
            'es': spanish_score,
            'it': italian_score
        }
        
        max_score = max(scores.values())
        if max_score > 2:  # Threshold for confidence
            return max(scores, key=scores.get)
        
        # 5. Default fallback
        if english_chars > greek_chars:
            return 'en'
        elif greek_chars > 0:
            return 'el'
        else:
            return 'unknown'

    def extract_content_analysis(self, soup: BeautifulSoup) -> Dict:
        """Εξάγει λεπτομερή content analysis"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Get main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|post', re.I)) or soup
        
        # Extract all text
        full_text = soup.get_text()
        main_text = main_content.get_text() if main_content != soup else full_text
        
        # Clean text
        full_text_clean = ' '.join(full_text.split())
        main_text_clean = ' '.join(main_text.split())
        
        # Word analysis
        words = full_text_clean.split()
        main_words = main_text_clean.split()
        
        # Calculate ratios
        html_content = str(soup)
        text_to_html_ratio = len(full_text_clean) / len(html_content) if len(html_content) > 0 else 0
        code_to_text_ratio = (len(html_content) - len(full_text_clean)) / len(html_content) if len(html_content) > 0 else 0
        
        # Language detection (simple)
        greek_chars = len(re.findall(r'[Α-Ωα-ωάέήίόύώ]', full_text_clean))
        english_chars = len(re.findall(r'[A-Za-z]', full_text_clean))
        total_chars = greek_chars + english_chars
        
        language_detection = {
            'greek_percentage': round(greek_chars / total_chars * 100, 1) if total_chars > 0 else 0,
            'english_percentage': round(english_chars / total_chars * 100, 1) if total_chars > 0 else 0,
            'primary_language': 'greek' if greek_chars > english_chars else 'english' if english_chars > 0 else 'unknown'
        }
        
        # Content density analysis
        paragraphs = soup.find_all('p')
        avg_paragraph_length = sum(len(p.get_text().split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        # Readability metrics (simplified)
        sentences = len(re.findall(r'[.!?]+', full_text_clean))
        avg_sentence_length = len(words) / sentences if sentences > 0 else 0
        
        # Keyword density analysis (top 10 words)
        word_freq = {}
        for word in words:
            word_lower = word.lower().strip('.,!?";:()[]')
            if len(word_lower) > 3 and word_lower not in ['που', 'για', 'από', 'στο', 'στη', 'στις', 'στον', 'με', 'τα', 'το', 'τη', 'την', 'του', 'της', 'τις', 'τους', 'και', 'είναι', 'the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'they', 'have', 'more', 'your', 'will', 'been', 'were', 'said', 'each', 'which', 'their']:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keyword_density = [{'word': word, 'count': count, 'density': round(count/len(words)*100, 2)} for word, count in top_keywords]
        
        return {
            'total_word_count': len(words),
            'main_content_word_count': len(main_words),
            'character_count': len(full_text_clean),
            'character_count_with_spaces': len(full_text),
            'text_to_html_ratio': round(text_to_html_ratio, 4),
            'code_to_text_ratio': round(code_to_text_ratio, 4),
            'reading_time_minutes': round(len(words) / 200, 1),
            'language_detection': language_detection,
            'content_structure': {
                'paragraph_count': len(paragraphs),
                'average_paragraph_length': round(avg_paragraph_length, 1),
                'sentence_count': sentences,
                'average_sentence_length': round(avg_sentence_length, 1)
            },
            'keyword_analysis': {
                'top_keywords': keyword_density,
                'keyword_diversity': len(word_freq),
                'repeated_words': sum(1 for count in word_freq.values() if count > 3)
            },
            'content_quality_indicators': {
                'has_main_content': main_content != soup,
                'content_depth_score': min(100, len(main_words) / 10),  # Score out of 100
                'readability_score': max(0, min(100, 100 - (avg_sentence_length - 15) * 2))  # Simplified readability
            }
        }
    
    def extract_technical_seo(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Εξάγει technical SEO δεδομένα"""
        canonical = soup.find('link', rel='canonical')
        canonical_url = canonical['href'] if canonical else None
        
        return {
            'has_sitemap_link': bool(soup.find('link', rel='sitemap')),
            'has_robots_txt_link': bool(soup.find('link', href=lambda x: x and 'robots.txt' in x)),
            'has_canonical': bool(canonical),
            'canonical_url': canonical_url,
            'has_hreflang': bool(soup.find('link', rel='alternate', hreflang=True)),
            'has_favicon': bool(soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')),
            'has_ssl': response.url.startswith('https://'),
            'response_headers': dict(response.headers)
        }
    
    def extract_social_meta(self, soup: BeautifulSoup) -> Dict:
        """Εξάγει social media meta tags"""
        og_tags = {}
        twitter_tags = {}
        
        # Open Graph tags
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            property_name = meta.get('property', '').replace('og:', '')
            og_tags[property_name] = meta.get('content', '')
        
        # Twitter Card tags
        for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            name = meta.get('name', '').replace('twitter:', '')
            twitter_tags[name] = meta.get('content', '')
        
        return {
            'open_graph': og_tags,
            'twitter_card': twitter_tags,
            'has_og_tags': len(og_tags) > 0,
            'has_twitter_tags': len(twitter_tags) > 0
        }
    
    def extract_schema_markup(self, soup: BeautifulSoup) -> Dict:
        """Εξάγει schema markup με λεπτομερή ανάλυση"""
        schemas = []
        schema_types = set()
        
        # JSON-LD schema
        json_ld_schemas = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schema_data = json.loads(script.string)
                json_ld_schemas.append(schema_data)
                schemas.append({
                    'format': 'json-ld',
                    'data': schema_data,
                    'type': schema_data.get('@type', 'Unknown') if isinstance(schema_data, dict) else 'Complex'
                })
                
                # Extract schema types
                if isinstance(schema_data, dict):
                    if '@type' in schema_data:
                        schema_types.add(schema_data['@type'])
                    elif '@graph' in schema_data:
                        for item in schema_data['@graph']:
                            if isinstance(item, dict) and '@type' in item:
                                schema_types.add(item['@type'])
            except json.JSONDecodeError as e:
                schemas.append({
                    'format': 'json-ld',
                    'error': f'Invalid JSON: {str(e)}',
                    'raw_content': script.string[:200] + '...' if len(script.string) > 200 else script.string
                })
        
        # Microdata
        microdata_items = []
        for element in soup.find_all(attrs={'itemtype': True}):
            itemtype = element.get('itemtype', '')
            itemscope = element.get('itemscope') is not None
            
            # Extract properties
            properties = {}
            for prop_elem in element.find_all(attrs={'itemprop': True}):
                prop_name = prop_elem.get('itemprop')
                prop_value = self._extract_microdata_value(prop_elem)
                properties[prop_name] = prop_value
            
            microdata_item = {
                'format': 'microdata',
                'itemtype': itemtype,
                'itemscope': itemscope,
                'properties': properties
            }
            
            microdata_items.append(microdata_item)
            schemas.append(microdata_item)
            schema_types.add(itemtype.split('/')[-1] if '/' in itemtype else itemtype)
        
        # RDFa detection
        rdfa_items = []
        for element in soup.find_all(attrs={'typeof': True}):
            rdfa_items.append({
                'format': 'rdfa',
                'typeof': element.get('typeof'),
                'vocab': element.get('vocab', ''),
                'prefix': element.get('prefix', '')
            })
            schemas.append(rdfa_items[-1])
        
        # Structured data validation
        validation_results = self._validate_common_schemas(schemas)
        
        return {
            'schemas': schemas,
            'json_ld_count': len(json_ld_schemas),
            'microdata_count': len(microdata_items),
            'rdfa_count': len(rdfa_items),
            'schema_count': len(schemas),
            'schema_types': list(schema_types),
            'has_schema_markup': len(schemas) > 0,
            'validation': validation_results,
            'recommended_schemas': self._get_recommended_schemas(soup)
        }
    
    def _extract_microdata_value(self, element):
        """Εξάγει την τιμή από microdata property"""
        if element.name in ['meta']:
            return element.get('content', '')
        elif element.name in ['img', 'audio', 'video', 'source', 'iframe']:
            return element.get('src', '')
        elif element.name == 'a':
            return element.get('href', '')
        elif element.name in ['time']:
            return element.get('datetime', element.get_text().strip())
        else:
            return element.get_text().strip()
    
    def _validate_common_schemas(self, schemas) -> Dict:
        """Βασική validation για κοινά schemas"""
        validation = {
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        for schema in schemas:
            if schema.get('format') == 'json-ld' and 'data' in schema:
                data = schema['data']
                schema_type = data.get('@type', '') if isinstance(data, dict) else ''
                
                if schema_type == 'Organization':
                    if not data.get('name'):
                        validation['errors'].append('Organization schema missing required "name" property')
                    if not data.get('url'):
                        validation['warnings'].append('Organization schema should include "url" property')
                
                elif schema_type == 'LocalBusiness':
                    required = ['name', 'address', 'telephone']
                    for req in required:
                        if not data.get(req):
                            validation['errors'].append(f'LocalBusiness schema missing required "{req}" property')
                
                elif schema_type == 'WebPage':
                    if not data.get('name') and not data.get('headline'):
                        validation['warnings'].append('WebPage schema should include "name" or "headline"')
        
        return validation
    
    def _get_recommended_schemas(self, soup: BeautifulSoup) -> List[str]:
        """Προτείνει schemas βάσει περιεχομένου"""
        recommendations = []
        
        # Check for contact info
        if soup.find('address') or soup.find(string=re.compile(r'\d{10,}')):  # Phone-like numbers
            recommendations.append('LocalBusiness')
        
        # Check for articles/blog posts
        if soup.find('article') or soup.find('time'):
            recommendations.append('Article')
        
        # Check for products
        if soup.find(string=re.compile(r'price|€|\$|cost', re.I)):
            recommendations.append('Product')
        
        # Check for events
        if soup.find(string=re.compile(r'event|conference|meeting', re.I)):
            recommendations.append('Event')
        
        return recommendations
    
    def extract_cache_headers(self, response: requests.Response) -> Dict:
        """Αναλύει cache headers"""
        headers = response.headers
        return {
            'cache_control': headers.get('Cache-Control', ''),
            'expires': headers.get('Expires', ''),
            'etag': headers.get('ETag', ''),
            'last_modified': headers.get('Last-Modified', ''),
            'has_cache_headers': bool(headers.get('Cache-Control') or headers.get('Expires'))
        }
    
    def extract_security_headers(self, response: requests.Response) -> Dict:
        """Αναλύει security headers"""
        headers = response.headers
        security_score = 0
        max_score = 8
        
        security_headers = {
            'strict_transport_security': headers.get('Strict-Transport-Security', ''),
            'content_security_policy': headers.get('Content-Security-Policy', ''),
            'x_frame_options': headers.get('X-Frame-Options', ''),
            'x_content_type_options': headers.get('X-Content-Type-Options', ''),
            'x_xss_protection': headers.get('X-XSS-Protection', ''),
            'referrer_policy': headers.get('Referrer-Policy', ''),
            'permissions_policy': headers.get('Permissions-Policy', ''),
            'content_type': headers.get('Content-Type', '')
        }
        
        # Score calculation
        if security_headers['strict_transport_security']: security_score += 1
        if security_headers['content_security_policy']: security_score += 1
        if security_headers['x_frame_options']: security_score += 1
        if security_headers['x_content_type_options']: security_score += 1
        if security_headers['x_xss_protection']: security_score += 1
        if security_headers['referrer_policy']: security_score += 1
        if security_headers['permissions_policy']: security_score += 1
        if 'charset' in security_headers['content_type'].lower(): security_score += 1
        
        security_headers['security_score'] = round(security_score / max_score * 100, 1)
        security_headers['missing_headers'] = [
            header for header, value in security_headers.items() 
            if not value and header not in ['security_score', 'missing_headers']
        ]
        
        return security_headers
    
    def extract_advanced_seo(self, soup: BeautifulSoup, response: requests.Response) -> Dict:
        """Προηγμένη SEO ανάλυση"""
        
        # URL structure analysis
        url = response.url
        parsed_url = urlparse(url)
        url_analysis = {
            'url_length': len(url),
            'path_depth': len([p for p in parsed_url.path.split('/') if p]),
            'has_parameters': bool(parsed_url.query),
            'has_fragment': bool(parsed_url.fragment),
            'url_readability': self.analyze_url_readability(parsed_url.path),
            'breadcrumb_trail': self.extract_breadcrumbs(soup)
        }
        
        # Meta robots analysis
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        robots_analysis = {
            'robots_content': robots_meta.get('content', '') if robots_meta else '',
            'is_indexable': 'noindex' not in (robots_meta.get('content', '') if robots_meta else ''),
            'is_followable': 'nofollow' not in (robots_meta.get('content', '') if robots_meta else ''),
            'allows_caching': 'noarchive' not in (robots_meta.get('content', '') if robots_meta else '')
        }
        
        # Title and meta optimization
        title_element = soup.find('title')
        title_text = title_element.get_text().strip() if title_element else ''
        
        title_analysis = {
            'title_keyword_placement': self.analyze_keyword_placement(title_text),
            'title_has_brand': self.has_brand_in_title(title_text),
            'title_uniqueness_score': self.calculate_title_uniqueness(title_text)
        }
        
        # Content optimization
        content_optimization = {
            'heading_hierarchy_correct': self.check_heading_hierarchy(soup),
            'content_keywords_distribution': self.analyze_content_keywords(soup),
            'internal_link_optimization': self.analyze_internal_link_anchor_text(soup),
            'content_freshness_indicators': self.find_content_freshness_indicators(soup)
        }
        
        return {
            'url_analysis': url_analysis,
            'robots_analysis': robots_analysis,
            'title_analysis': title_analysis,
            'content_optimization': content_optimization
        }
    
    def extract_accessibility_analysis(self, soup: BeautifulSoup) -> Dict:
        """Ανάλυση προσβασιμότητας"""
        
        accessibility_score = 0
        max_score = 10
        issues = []
        
        # Alt text για images
        images = soup.find_all('img')
        images_with_alt = sum(1 for img in images if img.get('alt'))
        if images:
            alt_percentage = images_with_alt / len(images) * 100
            if alt_percentage > 90: accessibility_score += 2
            elif alt_percentage > 70: accessibility_score += 1
            if alt_percentage < 100:
                issues.append(f"{len(images) - images_with_alt} images χωρίς alt text")
        else:
            accessibility_score += 2
        
        # Form labels
        forms = soup.find_all('form')
        inputs = soup.find_all('input', type=['text', 'email', 'password', 'tel'])
        labeled_inputs = sum(1 for inp in inputs if inp.get('id') and soup.find('label', attrs={'for': inp.get('id')}))
        if inputs:
            if labeled_inputs == len(inputs): accessibility_score += 1
            else: issues.append(f"{len(inputs) - labeled_inputs} form inputs χωρίς labels")
        else:
            accessibility_score += 1
        
        # Heading structure
        h1_count = len(soup.find_all('h1'))
        if h1_count == 1: accessibility_score += 1
        elif h1_count == 0: issues.append("Λείπει H1")
        elif h1_count > 1: issues.append(f"Πολλαπλά H1 ({h1_count})")
        
        # Links με descriptive text
        links = soup.find_all('a', href=True)
        generic_link_text = ['click here', 'read more', 'here', 'more', 'εδώ', 'περισσότερα', 'κλικ εδώ']
        generic_links = sum(1 for link in links if link.get_text().strip().lower() in generic_link_text)
        if links:
            if generic_links == 0: accessibility_score += 1
            else: issues.append(f"{generic_links} links με γενικό text")
        else:
            accessibility_score += 1
        
        # Color contrast (βασική ανίχνευση)
        inline_styles = soup.find_all(attrs={'style': True})
        color_issues = sum(1 for elem in inline_styles if 'color:' in elem.get('style', '') and 'background' in elem.get('style', ''))
        if color_issues > 0:
            issues.append(f"Πιθανά color contrast προβλήματα σε {color_issues} elements")
        else:
            accessibility_score += 1
        
        # Language declaration
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            accessibility_score += 1
        else:
            issues.append("Λείπει lang attribute στο HTML")
        
        # Skip links
        skip_links = soup.find_all('a', href=re.compile(r'^#'))
        if any('skip' in link.get_text().lower() for link in skip_links):
            accessibility_score += 1
        else:
            accessibility_score += 0.5  # Partial credit if other fragment links exist
        
        # Tables με headers
        tables = soup.find_all('table')
        if tables:
            tables_with_headers = sum(1 for table in tables if table.find('th') or table.find('thead'))
            if tables_with_headers == len(tables):
                accessibility_score += 1
            else:
                issues.append(f"{len(tables) - tables_with_headers} tables χωρίς proper headers")
        else:
            accessibility_score += 1
        
        return {
            'accessibility_score': round(accessibility_score / max_score * 100, 1),
            'issues': issues,
            'images_alt_coverage': round(images_with_alt / len(images) * 100, 1) if images else 100,
            'form_label_coverage': round(labeled_inputs / len(inputs) * 100, 1) if inputs else 100,
            'has_proper_headings': h1_count == 1,
            'has_language_declaration': bool(html_tag and html_tag.get('lang')) if soup.find('html') else False
        }
    
    def extract_mobile_optimization(self, soup: BeautifulSoup) -> Dict:
        """Ανάλυση mobile optimization"""
        
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        viewport_content = viewport_meta.get('content', '') if viewport_meta else ''
        
        mobile_score = 0
        max_score = 8
        issues = []
        
        # Viewport meta
        if viewport_meta:
            mobile_score += 2
            if 'width=device-width' in viewport_content:
                mobile_score += 1
            else:
                issues.append("Viewport meta δεν περιέχει width=device-width")
        else:
            issues.append("Λείπει viewport meta tag")
        
        # Responsive images
        images = soup.find_all('img')
        responsive_images = sum(1 for img in images if img.get('srcset') or img.get('sizes'))
        if images:
            if responsive_images / len(images) > 0.5:
                mobile_score += 1
            else:
                issues.append("Λίγες responsive images")
        else:
            mobile_score += 1
        
        # Touch-friendly elements
        buttons = soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'])
        if buttons:
            mobile_score += 1
        
        # Font sizes (βασική ανίχνευση)
        small_text_elements = soup.find_all(attrs={'style': re.compile(r'font-size:\s*[0-9]+px')})
        small_fonts = []
        for elem in small_text_elements:
            style = elem.get('style', '')
            if 'font-size:' in style:
                match = re.search(r'font-size:\s*([0-9]+)px', style)
                if match and int(match.group(1)) < 14:
                    small_fonts.append(elem)
        
        if len(small_fonts) == 0:
            mobile_score += 1
        else:
            issues.append(f"{len(small_fonts)} elements με πολύ μικρά fonts")
        
        # Media queries (στο CSS - βασική ανίχνευση)
        style_tags = soup.find_all('style')
        has_media_queries = any('@media' in style.get_text() for style in style_tags)
        if has_media_queries:
            mobile_score += 1
        else:
            issues.append("Δεν βρέθηκαν media queries στο inline CSS")
        
        # AMP detection
        amp_tags = soup.find_all(['amp-img', 'amp-video']) or soup.find('html', attrs={'amp': True})
        is_amp = bool(amp_tags)
        if is_amp:
            mobile_score += 1
        
        return {
            'mobile_optimization_score': round(mobile_score / max_score * 100, 1),
            'has_viewport_meta': bool(viewport_meta),
            'viewport_content': viewport_content,
            'responsive_images_percentage': round(responsive_images / len(images) * 100, 1) if images else 0,
            'is_amp': is_amp,
            'mobile_issues': issues,
            'mobile_friendly_indicators': {
                'proper_viewport': 'width=device-width' in viewport_content,
                'has_responsive_images': responsive_images > 0,
                'touch_elements': len(buttons)
            }
        }
    
    def analyze_internal_linking(self, soup: BeautifulSoup, current_url: str) -> Dict:
        """Ανάλυση internal linking structure"""
        
        internal_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            if self.is_internal_url(full_url):
                internal_links.append({
                    'url': full_url,
                    'anchor_text': link.get_text().strip(),
                    'title': link.get('title', ''),
                    'position': 'navigation' if link.find_parent(['nav', 'header']) else 'content',
                    'is_image_link': bool(link.find('img')),
                    'rel_attributes': link.get('rel', [])
                })
        
        # Anchor text analysis
        anchor_texts = [link['anchor_text'] for link in internal_links if link['anchor_text']]
        anchor_text_analysis = {
            'total_internal_links': len(internal_links),
            'unique_anchor_texts': len(set(anchor_texts)),
            'empty_anchor_texts': len([link for link in internal_links if not link['anchor_text']]),
            'image_links': len([link for link in internal_links if link['is_image_link']]),
            'navigation_links': len([link for link in internal_links if link['position'] == 'navigation']),
            'content_links': len([link for link in internal_links if link['position'] == 'content'])
        }
        
        return {
            'internal_links': internal_links[:20],  # Limit to first 20 for file size
            'anchor_text_analysis': anchor_text_analysis,
            'linking_recommendations': self.get_linking_recommendations(anchor_text_analysis)
        }
    
    def simulate_page_speed_insights(self, response: requests.Response, soup: BeautifulSoup) -> Dict:
        """Προσομοιώνει PageSpeed Insights metrics"""
        
        # Basic performance calculations
        load_time_ms = response.elapsed.total_seconds() * 1000
        content_size_kb = len(response.content) / 1024
        
        # Count resources
        css_links = len(soup.find_all('link', rel='stylesheet'))
        js_scripts = len(soup.find_all('script', src=True))
        images = len(soup.find_all('img', src=True))
        
        # Simulate scores (0-100)
        performance_score = max(0, min(100, 100 - (load_time_ms / 50)))  # Penalty for slow loading
        performance_score -= min(20, css_links * 2)  # CSS penalty
        performance_score -= min(20, js_scripts * 1.5)  # JS penalty
        performance_score -= min(10, max(0, images - 10))  # Too many images penalty
        
        # Simulate Core Web Vitals
        lcp = min(4000, load_time_ms + (content_size_kb * 2))  # Largest Contentful Paint
        fid = max(50, min(300, js_scripts * 10))  # First Input Delay
        cls = min(0.25, images * 0.01)  # Cumulative Layout Shift
        
        # Performance opportunities
        opportunities = []
        if css_links > 5:
            opportunities.append(f"Μειώστε CSS files ({css_links} files)")
        if js_scripts > 5:
            opportunities.append(f"Μειώστε JavaScript files ({js_scripts} files)")
        if content_size_kb > 1000:
            opportunities.append(f"Μειώστε page size ({content_size_kb:.1f}KB)")
        if images > 20:
            opportunities.append(f"Βελτιστοποιήστε images ({images} images)")
        
        # Check for optimization features
        has_lazy_loading = bool(soup.find('img', loading='lazy'))
        has_preload = bool(soup.find('link', rel='preload'))
        has_prefetch = bool(soup.find('link', rel='prefetch'))
        
        return {
            'performance_score': round(max(0, performance_score), 1),
            'core_web_vitals': {
                'lcp': round(lcp, 1),
                'fid': round(fid, 1),
                'cls': round(cls, 3),
                'lcp_rating': 'good' if lcp < 2500 else 'needs_improvement' if lcp < 4000 else 'poor',
                'fid_rating': 'good' if fid < 100 else 'needs_improvement' if fid < 300 else 'poor',
                'cls_rating': 'good' if cls < 0.1 else 'needs_improvement' if cls < 0.25 else 'poor'
            },
            'metrics': {
                'load_time_ms': round(load_time_ms, 1),
                'content_size_kb': round(content_size_kb, 1),
                'css_files': css_links,
                'js_files': js_scripts,
                'image_count': images
            },
            'optimization_features': {
                'has_lazy_loading': has_lazy_loading,
                'has_preload': has_preload,
                'has_prefetch': has_prefetch,
                'gzip_enabled': 'gzip' in response.headers.get('Content-Encoding', '')
            },
            'opportunities': opportunities,
            'overall_rating': 'good' if performance_score > 80 else 'needs_improvement' if performance_score > 50 else 'poor'
        }
    
    def extract_competitive_signals(self, soup: BeautifulSoup) -> Dict:
        """Εξάγει signals για competitive analysis"""
        
        # Social proof indicators
        social_proof = {
            'testimonials': len(soup.find_all(string=re.compile(r'testimonial|review|αξιολόγηση', re.I))),
            'client_logos': len(soup.find_all('img', alt=re.compile(r'client|customer|πελάτης', re.I))),
            'awards': len(soup.find_all(string=re.compile(r'award|certification|βραβείο|πιστοποίηση', re.I))),
            'case_studies': len(soup.find_all('a', href=re.compile(r'case-study|portfolio|έργα', re.I)))
        }
        
        # Contact information
        contact_info = {
            'phone_numbers': len(re.findall(r'(\+\d{1,3}[\s-]?)?\(?\d{3,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}', soup.get_text())),
            'email_addresses': len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())),
            'addresses': len(soup.find_all(string=re.compile(r'\d+.*street|avenue|road|οδός|λεωφόρος', re.I))),
            'contact_forms': len(soup.find_all('form'))
        }
        
        # Business indicators
        business_indicators = {
            'pricing_mentions': len(soup.find_all(string=re.compile(r'price|cost|€|pricing|τιμή|κόστος', re.I))),
            'service_pages': len(soup.find_all('a', href=re.compile(r'service|υπηρεσία', re.I))),
            'about_page': bool(soup.find('a', href=re.compile(r'about|σχετικά', re.I))),
            'blog_section': bool(soup.find('a', href=re.compile(r'blog|news|άρθρα|νέα', re.I)))
        }
        
        # Technology indicators
        tech_signals = {
            'cms_indicators': self.detect_cms(soup),
            'analytics_tools': self.detect_analytics(soup),
            'marketing_tools': self.detect_marketing_tools(soup),
            'security_indicators': self.detect_security_features(soup)
        }
        
        return {
            'social_proof': social_proof,
            'contact_accessibility': contact_info,
            'business_maturity': business_indicators,
            'technology_stack': tech_signals,
            'competitive_strength_score': self.calculate_competitive_score(social_proof, contact_info, business_indicators)
        }
    
    def simulate_core_web_vitals(self, response: requests.Response, soup: BeautifulSoup) -> Dict:
        """Προσομοιώνει Core Web Vitals metrics"""
        
        # Simulate based on actual measurable factors
        content_size = len(response.content)
        load_time_ms = response.elapsed.total_seconds() * 1000
        
        # Count elements that affect CWV
        images = soup.find_all('img')
        scripts = soup.find_all('script')
        
        # Largest Contentful Paint (LCP) simulation
        large_images = len([img for img in images if img.get('width') and img.get('width').isdigit() and int(img.get('width')) > 500])
        lcp_estimate = load_time_ms + (large_images * 200) + (content_size / 1000)
        
        # First Input Delay (FID) simulation
        blocking_scripts = len([script for script in scripts if not script.get('async') and not script.get('defer')])
        fid_estimate = max(50, blocking_scripts * 20)
        
        # Cumulative Layout Shift (CLS) simulation
        images_without_dimensions = len([img for img in images if not (img.get('width') and img.get('height'))])
        ads_elements = len(soup.find_all(attrs={'class': re.compile(r'ad|banner', re.I)}))
        cls_estimate = (images_without_dimensions * 0.02) + (ads_elements * 0.05)
        
        # First Contentful Paint (FCP)
        fcp_estimate = load_time_ms * 0.6  # Usually 60% of total load time
        
        # Time to Interactive (TTI)
        tti_estimate = load_time_ms + (len(scripts) * 100)
        
        return {
            'lcp': {
                'value': round(lcp_estimate, 1),
                'rating': 'good' if lcp_estimate < 2500 else 'needs_improvement' if lcp_estimate < 4000 else 'poor',
                'threshold_good': 2500,
                'threshold_poor': 4000
            },
            'fid': {
                'value': round(fid_estimate, 1),
                'rating': 'good' if fid_estimate < 100 else 'needs_improvement' if fid_estimate < 300 else 'poor',
                'threshold_good': 100,
                'threshold_poor': 300
            },
            'cls': {
                'value': round(cls_estimate, 3),
                'rating': 'good' if cls_estimate < 0.1 else 'needs_improvement' if cls_estimate < 0.25 else 'poor',
                'threshold_good': 0.1,
                'threshold_poor': 0.25
            },
            'fcp': {
                'value': round(fcp_estimate, 1),
                'rating': 'good' if fcp_estimate < 1800 else 'needs_improvement' if fcp_estimate < 3000 else 'poor'
            },
            'tti': {
                'value': round(tti_estimate, 1),
                'rating': 'good' if tti_estimate < 3800 else 'needs_improvement' if tti_estimate < 7300 else 'poor'
            },
            'overall_cwv_rating': self.calculate_overall_cwv_rating(lcp_estimate, fid_estimate, cls_estimate),
            'improvement_suggestions': self.get_cwv_improvement_suggestions(lcp_estimate, fid_estimate, cls_estimate, images, scripts)
        }
    
    # Helper methods
    def get_charset(self, soup: BeautifulSoup) -> str:
        """Επιστρέφει charset"""
        charset_meta = soup.find('meta', charset=True)
        if charset_meta:
            return charset_meta.get('charset', '')
        
        content_type_meta = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
        if content_type_meta:
            content = content_type_meta.get('content', '')
            if 'charset=' in content:
                return content.split('charset=')[1].strip()
        
        return 'utf-8'
    
    def get_viewport(self, soup: BeautifulSoup) -> str:
        """Επιστρέφει viewport"""
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        return viewport_meta.get('content', '') if viewport_meta else ''
    
    def get_robots(self, soup: BeautifulSoup) -> str:
        """Επιστρέφει robots directive"""
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        return robots_meta.get('content', '') if robots_meta else ''
    
    def analyze_url_readability(self, path: str) -> Dict:
        """Αναλύει την readability του URL"""
        score = 100
        issues = []
        
        if len(path) > 100:
            score -= 20
            issues.append("URL πολύ μεγάλο")
        
        if '_' in path:
            score -= 10
            issues.append("Underscore στο URL (προτιμήστε hyphens)")
        
        if re.search(r'[A-Z]', path):
            score -= 10
            issues.append("Κεφαλαία γράμματα στο URL")
        
        if re.search(r'[^a-zA-Z0-9\-/]', path):
            score -= 15
            issues.append("Ειδικοί χαρακτήρες στο URL")
        
        return {
            'readability_score': max(0, score),
            'issues': issues,
            'word_count': len([p for p in path.split('/') if p]),
            'uses_hyphens': '-' in path,
            'descriptive': not bool(re.search(r'\d{3,}|[a-f0-9]{8,}', path))  # No long numbers or hex
        }
    
    def extract_breadcrumbs(self, soup: BeautifulSoup) -> Dict:
        """Εξάγει breadcrumb information"""
        breadcrumbs = []
        
        # Common breadcrumb selectors
        breadcrumb_selectors = [
            'nav[aria-label*="breadcrumb" i]',
            '.breadcrumb',
            '.breadcrumbs',
            '[role="navigation"] ol',
            '[role="navigation"] ul'
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb_nav = soup.select(selector)
            if breadcrumb_nav:
                links = breadcrumb_nav[0].find_all('a')
                breadcrumbs = [{'text': link.get_text().strip(), 'url': link.get('href', '')} for link in links]
                break
        
        # Check for JSON-LD BreadcrumbList
        json_ld_breadcrumbs = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'BreadcrumbList':
                    json_ld_breadcrumbs = data.get('itemListElement', [])
                elif isinstance(data, dict) and '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'BreadcrumbList':
                            json_ld_breadcrumbs = item.get('itemListElement', [])
            except:
                pass
        
        return {
            'html_breadcrumbs': breadcrumbs,
            'json_ld_breadcrumbs': json_ld_breadcrumbs,
            'has_breadcrumbs': len(breadcrumbs) > 0 or len(json_ld_breadcrumbs) > 0,
            'breadcrumb_depth': max(len(breadcrumbs), len(json_ld_breadcrumbs))
        }
    
    def analyze_keyword_placement(self, title: str) -> Dict:
        """Αναλύει την τοποθέτηση keywords στον title"""
        words = title.lower().split()
        
        return {
            'starts_with_keyword': len(words) > 0 and len(words[0]) > 3,
            'keyword_density': len([w for w in words if len(w) > 3]) / len(words) if words else 0,
            'has_brand_last': any(brand in words[-2:] for brand in ['company', 'ltd', 'inc', 'corp']) if len(words) > 1 else False
        }
    
    def has_brand_in_title(self, title: str) -> bool:
        """Ελέγχει αν υπάρχει brand name στον title"""
        brand_indicators = ['|', '-', '::', '•', '—']
        return any(indicator in title.lower() for indicator in brand_indicators)
    
    def calculate_title_uniqueness(self, title: str) -> int:
        """Υπολογίζει uniqueness score για τον title"""
        # Simple uniqueness based on common patterns
        common_patterns = ['home', 'welcome', 'index', 'main', 'default']
        score = 100
        
        for pattern in common_patterns:
            if pattern in title.lower():
                score -= 20
        
        return max(0, score)
    
    def check_heading_hierarchy(self, soup: BeautifulSoup) -> Dict:
        """Ελέγχει την ιεραρχία των headings"""
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    'level': level,
                    'text': heading.get_text().strip(),
                    'position': len(headings)
                })
        
        issues = []
        hierarchy_correct = True
        
        if not headings:
            return {'correct': False, 'issues': ['Δεν υπάρχουν headings'], 'headings': []}
        
        # Check if starts with H1
        if headings[0]['level'] != 1:
            hierarchy_correct = False
            issues.append('Δεν ξεκινά με H1')
        
        # Check for level skipping
        for i in range(1, len(headings)):
            current_level = headings[i]['level']
            prev_level = headings[i-1]['level']
            
            if current_level > prev_level + 1:
                hierarchy_correct = False
                issues.append(f'Παράλειψη level: από H{prev_level} σε H{current_level}')
        
        return {
            'correct': hierarchy_correct,
            'issues': issues,
            'headings': headings,
            'total_headings': len(headings),
            'h1_count': len([h for h in headings if h['level'] == 1])
        }
    
    def analyze_content_keywords(self, soup: BeautifulSoup) -> Dict:
        """Αναλύει την κατανομή keywords στο περιεχόμενο"""
        # Get text from different sections
        title_text = soup.find('title').get_text() if soup.find('title') else ''
        h1_text = ' '.join([h.get_text() for h in soup.find_all('h1')])
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc_text = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract main content (remove nav, header, footer)
        content_soup = soup.__copy__()
        for element in content_soup(['nav', 'header', 'footer', 'aside', 'script', 'style']):
            element.decompose()
        main_content = content_soup.get_text()
        
        # Simple keyword extraction from title
        title_keywords = set(word.lower().strip('.,!?') for word in title_text.split() if len(word) > 3)
        
        keyword_placement = {}
        for keyword in title_keywords:
            keyword_placement[keyword] = {
                'in_title': keyword in title_text.lower(),
                'in_h1': keyword in h1_text.lower(),
                'in_meta_description': keyword in meta_desc_text.lower(),
                'in_content': keyword in main_content.lower(),
                'content_frequency': main_content.lower().count(keyword)
            }
        
        return {
            'extracted_keywords': list(title_keywords),
            'keyword_placement': keyword_placement,
            'keyword_optimization_score': self.calculate_keyword_score(keyword_placement)
        }
    
    def calculate_keyword_score(self, keyword_placement: Dict) -> int:
        """Υπολογίζει keyword optimization score"""
        if not keyword_placement:
            return 0
        
        total_score = 0
        for keyword, placement in keyword_placement.items():
            keyword_score = 0
            if placement['in_title']: keyword_score += 25
            if placement['in_h1']: keyword_score += 20
            if placement['in_meta_description']: keyword_score += 15
            if placement['in_content']: keyword_score += 10
            
            # Bonus for frequency (but not over-optimization)
            freq = placement['content_frequency']
            if 2 <= freq <= 5:
                keyword_score += 10
            elif freq > 5:
                keyword_score -= 5  # Penalty for over-optimization
            
            total_score += keyword_score
        
        return min(100, total_score // len(keyword_placement))
    
    def analyze_internal_link_anchor_text(self, soup: BeautifulSoup) -> Dict:
        """Αναλύει το anchor text των internal links"""
        internal_links = soup.find_all('a', href=True)
        
        anchor_analysis = {
            'total_links': 0,
            'descriptive_anchors': 0,
            'generic_anchors': 0,
            'branded_anchors': 0,
            'image_links': 0,
            'empty_anchors': 0
        }
        
        generic_terms = ['click here', 'read more', 'here', 'more', 'εδώ', 'περισσότερα', 'κλικ', 'δες εδώ']
        brand_terms = ['home', 'αρχική', 'homepage', 'main']
        
        for link in internal_links:
            href = link.get('href', '')
            if href.startswith('/') or href.startswith('#') or not href.startswith('http'):
                anchor_analysis['total_links'] += 1
                anchor_text = link.get_text().strip().lower()
                
                if not anchor_text:
                    if link.find('img'):
                        anchor_analysis['image_links'] += 1
                    else:
                        anchor_analysis['empty_anchors'] += 1
                elif any(term in anchor_text for term in generic_terms):
                    anchor_analysis['generic_anchors'] += 1
                elif any(term in anchor_text for term in brand_terms):
                    anchor_analysis['branded_anchors'] += 1
                else:
                    anchor_analysis['descriptive_anchors'] += 1
        
        return anchor_analysis
    
    def find_content_freshness_indicators(self, soup: BeautifulSoup) -> Dict:
        """Αναζητά indicators για content freshness"""
        freshness_indicators = {
            'has_dates': False,
            'has_last_updated': False,
            'has_time_elements': False,
            'copyright_year': None,
            'estimated_freshness': 'unknown'
        }
        
        # Look for time elements
        time_elements = soup.find_all('time')
        if time_elements:
            freshness_indicators['has_time_elements'] = True
            freshness_indicators['has_dates'] = True
        
        # Look for date patterns in text
        date_patterns = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}', soup.get_text())
        if date_patterns:
            freshness_indicators['has_dates'] = True
        
        # Look for "last updated" indicators
        text = soup.get_text().lower()
        update_indicators = ['last updated', 'τελευταία ενημέρωση', 'updated on', 'ενημερώθηκε']
        if any(indicator in text for indicator in update_indicators):
            freshness_indicators['has_last_updated'] = True
        
        # Copyright year
        copyright_match = re.search(r'copyright.*?(\d{4})', text)
        if copyright_match:
            freshness_indicators['copyright_year'] = int(copyright_match.group(1))
        
        # Estimate freshness
        current_year = datetime.now().year
        if freshness_indicators['copyright_year']:
            if current_year - freshness_indicators['copyright_year'] <= 1:
                freshness_indicators['estimated_freshness'] = 'fresh'
            elif current_year - freshness_indicators['copyright_year'] <= 3:
                freshness_indicators['estimated_freshness'] = 'moderate'
            else:
                freshness_indicators['estimated_freshness'] = 'stale'
        
        return freshness_indicators
    
    def get_linking_recommendations(self, anchor_analysis: Dict) -> List[str]:
        """Δημιουργεί συστάσεις για internal linking"""
        recommendations = []
        
        total = anchor_analysis.get('total_links', anchor_analysis.get('total_internal_links', 0))
        if total == 0:
            return ['Προσθέστε internal links για καλύτερη navigation']
        
        generic_anchors = anchor_analysis.get('generic_anchors', 0)
        descriptive_anchors = anchor_analysis.get('descriptive_anchors', 0)
        empty_anchors = anchor_analysis.get('empty_anchors', 0)
        
        generic_ratio = generic_anchors / total if total > 0 else 0
        if generic_ratio > 0.3:
            recommendations.append('Μειώστε τα generic anchor texts (click here, read more)')
        
        descriptive_ratio = descriptive_anchors / total if total > 0 else 0
        if descriptive_ratio < 0.5:
            recommendations.append('Χρησιμοποιήστε πιο descriptive anchor texts')
        
        if empty_anchors > 0:
            recommendations.append('Προσθέστε alt text σε image links')
        
        if total < 5:
            recommendations.append('Προσθέστε περισσότερα internal links')
        elif total > 100:
            recommendations.append('Μειώστε τον αριθμό internal links')
        
        return recommendations
    
    def detect_cms(self, soup: BeautifulSoup) -> Dict:
        """Ανιχνεύει το CMS που χρησιμοποιείται"""
        cms_indicators = {
            'wordpress': bool(soup.find(attrs={'class': re.compile(r'wp-', re.I)}) or 
                            soup.find('meta', attrs={'name': 'generator', 'content': re.compile(r'wordpress', re.I)})),
            'drupal': bool(soup.find('meta', attrs={'name': 'generator', 'content': re.compile(r'drupal', re.I)})),
            'joomla': bool(soup.find('meta', attrs={'name': 'generator', 'content': re.compile(r'joomla', re.I)})),
            'shopify': bool(soup.find('script', src=re.compile(r'shopify', re.I))),
            'wix': bool(soup.find('meta', attrs={'name': 'generator', 'content': re.compile(r'wix', re.I)})),
            'squarespace': bool(soup.find('script', src=re.compile(r'squarespace', re.I))),
            'custom': True  # Default assumption
        }
        
        detected_cms = [cms for cms, detected in cms_indicators.items() if detected and cms != 'custom']
        if detected_cms:
            cms_indicators['custom'] = False
        
        return {
            'detected_cms': detected_cms[0] if detected_cms else 'custom',
            'cms_indicators': cms_indicators,
            'confidence': 'high' if detected_cms else 'low'
        }
    
    def detect_analytics(self, soup: BeautifulSoup) -> List[str]:
        """Ανιχνεύει analytics tools"""
        analytics_tools = []
        
        scripts_text = ' '.join([script.get_text() for script in soup.find_all('script')])
        
        if 'google-analytics' in scripts_text or 'gtag' in scripts_text or 'ga(' in scripts_text:
            analytics_tools.append('Google Analytics')
        
        if 'googletagmanager' in scripts_text:
            analytics_tools.append('Google Tag Manager')
        
        if 'facebook.net' in scripts_text or 'fbevents' in scripts_text:
            analytics_tools.append('Facebook Pixel')
        
        if 'hotjar' in scripts_text:
            analytics_tools.append('Hotjar')
        
        if 'mouseflow' in scripts_text:
            analytics_tools.append('Mouseflow')
        
        return analytics_tools
    
    def detect_marketing_tools(self, soup: BeautifulSoup) -> List[str]:
        """Ανιχνεύει marketing tools"""
        marketing_tools = []
        
        scripts_text = ' '.join([script.get_text() for script in soup.find_all('script')])
        
        if 'mailchimp' in scripts_text:
            marketing_tools.append('MailChimp')
        
        if 'hubspot' in scripts_text:
            marketing_tools.append('HubSpot')
        
        if 'intercom' in scripts_text:
            marketing_tools.append('Intercom')
        
        if 'zendesk' in scripts_text:
            marketing_tools.append('Zendesk')
        
        if 'crisp' in scripts_text:
            marketing_tools.append('Crisp Chat')
        
        return marketing_tools
    
    def detect_security_features(self, soup: BeautifulSoup) -> List[str]:
        """Ανιχνεύει security features"""
        security_features = []
        
        # Check for CSRF tokens
        if soup.find('input', attrs={'name': re.compile(r'csrf|token', re.I)}):
            security_features.append('CSRF Protection')
        
        # Check for captcha
        if soup.find(attrs={'class': re.compile(r'captcha|recaptcha', re.I)}):
            security_features.append('Captcha')
        
        # Check for SSL indicators in content
        if 'https://' in soup.get_text():
            security_features.append('SSL Awareness')
        
        return security_features
    
    def calculate_competitive_score(self, social_proof: Dict, contact_info: Dict, business_indicators: Dict) -> int:
        """Υπολογίζει competitive strength score"""
        score = 0
        
        # Social proof scoring
        score += min(20, social_proof['testimonials'] * 5)
        score += min(15, social_proof['client_logos'] * 3)
        score += min(10, social_proof['awards'] * 5)
        score += min(10, social_proof['case_studies'] * 2)
        
        # Contact accessibility scoring
        score += min(15, contact_info['phone_numbers'] * 8)
        score += min(10, contact_info['email_addresses'] * 5)
        score += min(10, contact_info['contact_forms'] * 10)
        
        # Business maturity scoring
        if business_indicators['about_page']: score += 5
        if business_indicators['blog_section']: score += 5
        score += min(5, business_indicators['service_pages'])
        
        return min(100, score)
    
    def calculate_overall_cwv_rating(self, lcp: float, fid: float, cls: float) -> str:
        """Υπολογίζει overall Core Web Vitals rating"""
        good_count = 0
        if lcp < 2500: good_count += 1
        if fid < 100: good_count += 1
        if cls < 0.1: good_count += 1
        
        if good_count == 3:
            return 'good'
        elif good_count >= 2:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def get_cwv_improvement_suggestions(self, lcp: float, fid: float, cls: float, images, scripts) -> List[str]:
        """Δημιουργεί συστάσεις για Core Web Vitals"""
        suggestions = []
        
        if lcp > 2500:
            suggestions.append('Βελτιστοποιήστε το Largest Contentful Paint με image optimization')
            suggestions.append('Χρησιμοποιήστε CDN για faster content delivery')
        
        if fid > 100:
            suggestions.append('Μειώστε το First Input Delay με async/defer JavaScript')
            suggestions.append('Μειώστε blocking scripts')
        
        if cls > 0.1:
            suggestions.append('Προσθέστε dimensions σε images για stable layout')
            suggestions.append('Αποφύγετε dynamic content insertions')
        
        if len(images) > 20:
            suggestions.append('Χρησιμοποιήστε lazy loading για images')
        
        if len(scripts) > 10:
            suggestions.append('Συνδυάστε και minimize JavaScript files')
        
        return suggestions
    
    def crawl_page(self, url: str) -> Optional[Dict]:
        """Κάνει crawl μία σελίδα"""
        try:
            self.logger.info(f"Crawling: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                page_data = self.extract_page_data(url, response)
                
                # Detect page language
                page_language = self.detect_page_language(soup, url)
                page_data['detected_language'] = page_language
                
                # Create language-specific folder
                lang_folder = self.crawl_dir / page_language
                lang_folder.mkdir(parents=True, exist_ok=True)
                
                # Generate filename
                filename = self.url_to_filename(url)
                
                # Save individual page file in language folder
                page_file = lang_folder / filename
                with open(page_file, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"Saved: {page_language}/{filename}")
                return page_data
            else:
                error = {
                    'url': url,
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}'
                }
                self.errors.append(error)
                self.logger.warning(f"Error {response.status_code}: {url}")
                
        except Exception as e:
            error = {
                'url': url,
                'error': str(e)
            }
            self.errors.append(error)
            self.logger.error(f"Exception crawling {url}: {e}")
        
        return None
    
    def create_summary(self) -> Dict:
        """Δημιουργεί summary για το crawl"""
        # Load all page data from language folders
        all_pages_data = {}
        language_stats = {}
        
        # Check for language folders first, then fallback to root folder
        language_folders = [folder for folder in self.crawl_dir.iterdir() if folder.is_dir()]
        
        if language_folders:
            # New structure with language folders
            for lang_folder in language_folders:
                lang_code = lang_folder.name
                language_stats[lang_code] = {'pages': 0, 'files': []}
                
                page_files = list(lang_folder.glob('*.json'))
                for page_file in page_files:
                    try:
                        with open(page_file, 'r', encoding='utf-8') as f:
                            page_data = json.load(f)
                            all_pages_data[page_data['url']] = page_data
                            language_stats[lang_code]['pages'] += 1
                            language_stats[lang_code]['files'].append(page_file.name)
                    except Exception as e:
                        self.logger.warning(f"Error loading {page_file}: {e}")
        else:
            # Fallback to old structure (root folder)
            page_files = list(self.crawl_dir.glob('*.json'))
            for page_file in page_files:
                if page_file.name != '_summary.json':
                    try:
                        with open(page_file, 'r', encoding='utf-8') as f:
                            page_data = json.load(f)
                            all_pages_data[page_data['url']] = page_data
                            # Detect language for old structure
                            lang = page_data.get('detected_language', 'unknown')
                            if lang not in language_stats:
                                language_stats[lang] = {'pages': 0, 'files': []}
                            language_stats[lang]['pages'] += 1
                            language_stats[lang]['files'].append(page_file.name)
                    except Exception as e:
                        self.logger.warning(f"Error loading {page_file}: {e}")
        
        # Calculate summary statistics
        total_images = sum(page.get('images', {}).get('total_images', 0) for page in all_pages_data.values())
        images_without_alt = sum(page.get('images', {}).get('images_without_alt', 0) for page in all_pages_data.values())
        total_internal_links = sum(page.get('links', {}).get('total_internal', 0) for page in all_pages_data.values())
        total_external_links = sum(page.get('links', {}).get('total_external', 0) for page in all_pages_data.values())
        
        # SEO issues
        pages_without_title = sum(1 for page in all_pages_data.values() if not page.get('meta_data', {}).get('title'))
        pages_without_description = sum(1 for page in all_pages_data.values() if not page.get('meta_data', {}).get('description'))
        pages_without_h1 = sum(1 for page in all_pages_data.values() if page.get('headings', {}).get('h1_count', 0) == 0)
        pages_with_multiple_h1 = sum(1 for page in all_pages_data.values() if page.get('headings', {}).get('h1_count', 0) > 1)
        
        # Performance
        load_times = [page.get('load_time', 0) for page in all_pages_data.values()]
        avg_load_time = sum(load_times) / len(load_times) if load_times else 0
        slow_pages = sum(1 for time in load_times if time > 3)
        
        # Content
        word_counts = [page.get('content_analysis', {}).get('total_word_count', 0) for page in all_pages_data.values()]
        avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
        pages_with_low_content = sum(1 for count in word_counts if count < 300)
        
        summary = {
            'crawl_info': {
                'domain': self.domain,
                'base_url': self.base_url,
                'crawl_timestamp': self.crawl_timestamp,
                'crawl_date': datetime.now().isoformat(),
                'total_pages_crawled': len(all_pages_data),
                'total_errors': len(self.errors),
                'language_distribution': language_stats
            },
            'seo_overview': {
                'total_images': total_images,
                'images_without_alt': images_without_alt,
                'alt_text_coverage': round((total_images - images_without_alt) / total_images * 100, 1) if total_images > 0 else 100,
                'total_internal_links': total_internal_links,
                'total_external_links': total_external_links
            },
            'seo_issues': {
                'pages_without_title': pages_without_title,
                'pages_without_description': pages_without_description,
                'pages_without_h1': pages_without_h1,
                'pages_with_multiple_h1': pages_with_multiple_h1
            },
            'performance': {
                'average_load_time_seconds': round(avg_load_time, 2),
                'slow_pages_over_3s': slow_pages,
                'performance_score': round(max(0, 100 - (slow_pages / len(load_times) * 100)), 1) if load_times else 100
            },
            'content': {
                'average_word_count': round(avg_word_count, 1),
                'pages_with_low_content': pages_with_low_content
            },
            'errors': self.errors
        }
        
        return summary
    
    def crawl_domain(self, max_pages: int = 100) -> str:
        """Κάνει crawl ολόκληρο το domain"""
        self.logger.info(f"Starting crawl of {self.domain}")
        self.logger.info(f"Max pages: {max_pages}")
        
        # Add starting URL
        self.to_crawl.add(self.base_url)
        
        crawled_count = 0
        while self.to_crawl and crawled_count < max_pages:
            # Get next URL to crawl
            url = self.to_crawl.pop()
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Skip non-HTML URLs
            if any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js', '.xml', '.txt']):
                continue
                
            self.visited_urls.add(url)
            page_data = self.crawl_page(url)
            
            if page_data:
                crawled_count += 1
                self.logger.info(f"Progress: {crawled_count}/{max_pages} pages crawled")
                
            # Small delay to be respectful
            time.sleep(0.5)
        
        # Create summary
        self.logger.info("Creating summary...")
        summary = self.create_summary()
        summary_file = self.crawl_dir / '_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Crawl completed!")
        self.logger.info(f"📊 {crawled_count} pages crawled")
        self.logger.info(f"📁 Results saved in: {self.crawl_dir}")
        self.logger.info(f"📄 Found {len(self.to_crawl)} additional URLs")
        
        # Log language distribution
        lang_dist = summary.get('crawl_info', {}).get('language_distribution', {})
        if lang_dist:
            self.logger.info("🌍 Language distribution:")
            for lang, stats in lang_dist.items():
                self.logger.info(f"  {lang}: {stats['pages']} pages")
        
        return str(self.crawl_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SEO Domain Scraper")
    parser.add_argument("url", help="The URL of the website to scrape")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum number of pages to crawl")
    args = parser.parse_args()

    scraper = SEOScraper(args.url)
    output_dir = scraper.crawl_domain(max_pages=args.max_pages)
    print(f"Crawl completed! Check results in: {output_dir}")
