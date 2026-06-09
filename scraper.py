#!/usr/bin/env python3
"""
Scraper for copying blog posts from Cnblogs to local blog project.
Fetches blog post titles, content, and images.
"""

import os
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class CnblogsScraper:
    # Invalid filesystem characters that should be removed/replaced
    INVALID_FS_CHARS = r'[<>:"/\\|?*]'
    PROBLEMATIC_POSTS = {
        '0056', '0102', '0130', '0135', '0152', '0170', '0185', '0204', '0241'
    }
    
    @staticmethod
    def sanitize_title(title):
        """
        Sanitize a title to be safe for use in directory names.
        Handles:
        - Trailing whitespace
        - Special filesystem characters
        - Unclosed parentheses
        - Chinese characters properly
        """
        if not title:
            return 'untitled'
        
        # Strip leading/trailing whitespace
        title = title.strip()
        
        # Replace invalid filesystem characters with underscore
        title = re.sub(CnblogsScraper.INVALID_FS_CHARS, '_', title)
        
        # Collapse multiple underscores
        title = re.sub(r'_+', '_', title)
        
        # Remove trailing underscore if present
        title = title.rstrip('_')
        
        return title
    def __init__(self, username="barneywill", base_url="https://www.cnblogs.com"):
        self.username = username
        self.base_url = base_url
        self.blog_url = f"{base_url}/{username}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.problematic_titles_log = []
        
    def get_blog_posts_links(self):
        """Extract all blog post links from paginated archive pages."""
        posts = []
        posts_urls = set()  # Track URLs to avoid duplicates
        
        print("Fetching blog posts from all paginated archives...")
        try:
            # The main archive page is paginated: /barneywill/p/?Page=1, /barneywill/p/?Page=2, etc.
            archive_list_url = f"{self.blog_url}/p/"
            
            for page in range(1, 500):  # Fetch up to 500 pages to be comprehensive
                try:
                    page_url = f"{archive_list_url}?Page={page}"
                    print(f"Fetching page {page}...")
                    
                    response = self.session.get(page_url, timeout=10)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract post links from this page
                    page_posts = 0
                    
                    # Find all post links - they typically have href like /barneywill/p/12345678.html
                    for link in soup.find_all('a', href=re.compile(r'/barneywill/p/\d+\.html')):
                        href = link.get('href')
                        if href:
                            full_url = urljoin(self.base_url, href)
                            
                            # Avoid duplicates
                            if full_url not in posts_urls:
                                title = link.get_text(strip=True)
                                if title and title not in ['', '[置顶]', '阅读全文']:
                                    posts.append({
                                        'url': full_url,
                                        'title': title
                                    })
                                    posts_urls.add(full_url)
                                    page_posts += 1
                    
                    if page_posts == 0:
                        print(f"Page {page}: No posts found, stopping pagination")
                        break
                    
                    print(f"Page {page}: Found {page_posts} posts (Total: {len(posts)})")
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"Error fetching page {page}: {e}")
                    break
            
            print(f"\nTotal posts found: {len(posts)}")
            
        except Exception as e:
            print(f"Error fetching blog posts: {e}")
        
        return posts
    
    def fetch_blog_post(self, post_url):
        """Fetch a single blog post with its content and images."""
        try:
            response = self.session.get(post_url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title - try multiple selectors
            title = 'Untitled'
            
            # Try h1 with id = post-title
            title_elem = soup.find('h1', id='post-title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                # Try a.postTitle
                title_elem = soup.find('a', class_='postTitle')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    # Try h1.postTitle
                    title_elem = soup.find('h1', class_='postTitle')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    else:
                        # Try any h1 in the post header
                        header = soup.find('div', id='header')
                        if header:
                            h1 = header.find('h1')
                            if h1:
                                title = h1.get_text(strip=True)
            
            # Extract content
            content_elem = soup.find('div', id='cnblogs_post_body')
            if not content_elem:
                content_elem = soup.find('div', class_='blogpost-body')
            
            content = str(content_elem) if content_elem else ''
            
            # Extract images from content
            images = []
            if content_elem:
                for img in content_elem.find_all('img'):
                    img_src = img.get('src', '')
                    if img_src:
                        images.append(img_src)
            
            # Extract publish date - try multiple selectors
            publish_date = None
            date_elem = soup.find('span', id='publish_time')
            if date_elem:
                publish_date = date_elem.get_text(strip=True)
            else:
                # Try class selector
                date_elem = soup.find('span', class_='publish_time')
                if date_elem:
                    publish_date = date_elem.get_text(strip=True)
            
            return {
                'title': title,
                'content': content,
                'images': images,
                'publish_date': publish_date,
                'url': post_url
            }
        
        except Exception as e:
            print(f"Error fetching post {post_url}: {e}")
            return None
    
    def download_image(self, image_url, save_dir):
        """Download image and return local path."""
        try:
            if not image_url:
                return None
            
            # Skip certain image URLs
            if 'cnblogs.com/images' in image_url or 'common.cnblogs.com' in image_url:
                # Handle Cnblogs image URLs
                pass
            
            response = self.session.get(image_url, timeout=10)
            if response.status_code == 200:
                # Generate filename from URL
                filename = image_url.split('/')[-1].split('?')[0]
                if not filename:
                    filename = f"image_{int(time.time())}"
                
                if not filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    # Try to infer extension from content-type
                    content_type = response.headers.get('content-type', '')
                    if 'png' in content_type:
                        filename += '.png'
                    elif 'jpeg' in content_type or 'jpg' in content_type:
                        filename += '.jpg'
                    else:
                        filename += '.jpg'
                
                filepath = os.path.join(save_dir, filename)
                os.makedirs(save_dir, exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filename
        
        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
        
        return None
    
    def save_blog_posts(self, posts_data, output_dir="./posts"):
        """Save blog posts to local directory."""
        os.makedirs(output_dir, exist_ok=True)
        
        index = []
        
        for i, post in enumerate(posts_data, 1):
            if not post:
                continue
            
            # Create post directory with sanitized title
            post_id = str(i).zfill(4)
            sanitized_title = self.sanitize_title(post['title'])
            # Limit to 50 chars after sanitization
            post_dir_name = f"{post_id}_{sanitized_title[:50]}"
            post_dir = os.path.join(output_dir, post_dir_name)
            
            # Log if title was problematic
            if post_id in self.PROBLEMATIC_POSTS and sanitized_title != post['title'][:50]:
                self.problematic_titles_log.append({
                    'id': post_id,
                    'original': post['title'][:50],
                    'sanitized': sanitized_title[:50],
                    'reason': 'special_characters'
                })
            
            try:
                os.makedirs(post_dir, exist_ok=True)
            except Exception as e:
                print(f"  ERROR creating directory: {e}")
                print(f"  Original title: {post['title']}")
                print(f"  Sanitized title: {sanitized_title}")
                self.problematic_titles_log.append({
                    'id': post_id,
                    'original': post['title'],
                    'error': str(e)
                })
                continue
            
            # Save images
            image_mapping = {}
            images_dir = os.path.join(post_dir, "images")
            for img_url in post['images']:
                local_filename = self.download_image(img_url, images_dir)
                if local_filename:
                    image_mapping[img_url] = f"./images/{local_filename}"
                    print(f"  Downloaded image: {local_filename}")
            
            # Update content with local image paths
            content = post['content']
            for old_url, new_path in image_mapping.items():
                content = content.replace(old_url, new_path)
            
            # Save post metadata and content
            post_data = {
                'title': post['title'],
                'publish_date': post['publish_date'],
                'original_url': post['url'],
                'images': list(image_mapping.values()),
                'content_html': content
            }
            
            with open(os.path.join(post_dir, 'post.json'), 'w', encoding='utf-8') as f:
                json.dump(post_data, f, ensure_ascii=False, indent=2)
            
            with open(os.path.join(post_dir, 'content.html'), 'w', encoding='utf-8') as f:
                f.write(content)
            
            index.append({
                'id': post_id,
                'title': post['title'],
                'publish_date': post['publish_date'],
                'original_url': post['url'],
                'directory': post_dir_name
            })
            
            print(f"[{i}] Saved: {post['title']}")
            time.sleep(0.5)  # Be respectful
        
        # Save index
        with open(os.path.join(output_dir, 'index.json'), 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        return len(index)
    
    def run(self):
        """Run the scraper."""
        print("=" * 60)
        print(f"Cnblogs Blog Scraper")
        print(f"Username: {self.username}")
        print("=" * 60)
        
        print("\nStep 1: Fetching blog post links...")
        posts_links = self.get_blog_posts_links()
        
        if not posts_links:
            print("No posts found. Exiting.")
            return
        
        print(f"\nStep 2: Fetching {len(posts_links)} blog posts...")
        posts_data = []
        for i, post_link in enumerate(posts_links, 1):
            print(f"\n[{i}/{len(posts_links)}] Fetching: {post_link['title']}")
            post_data = self.fetch_blog_post(post_link['url'])
            if post_data:
                posts_data.append(post_data)
            time.sleep(0.5)
        
        print(f"\nStep 3: Saving {len(posts_data)} posts to disk...")
        saved_count = self.save_blog_posts(posts_data)
        
        # Report on problematic titles
        if self.problematic_titles_log:
            print("\n" + "=" * 60)
            print(f"⚠️  Found {len(self.problematic_titles_log)} posts with problematic titles:")
            for item in self.problematic_titles_log:
                if 'error' in item:
                    print(f"  [{item['id']}] ERROR: {item['error']}")
                else:
                    print(f"  [{item['id']}] Sanitized: {item['original']} → {item['sanitized']}")
            
            # Save log
            with open('problematic_titles.json', 'w', encoding='utf-8') as f:
                json.dump(self.problematic_titles_log, f, ensure_ascii=False, indent=2)
            print("  Detailed log saved to: problematic_titles.json")
        
        print("\n" + "=" * 60)
        print(f"Success! Saved {saved_count} blog posts")
        print("=" * 60)


if __name__ == "__main__":
    scraper = CnblogsScraper("barneywill")
    scraper.run()
