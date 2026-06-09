#!/usr/bin/env python3
"""
Generate individual HTML pages for each blog post using Style 3 template.
Converts posts from posts/ directory to HTML files in post/ directory.
Uses original Chinese content.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Use absolute paths based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(SCRIPT_DIR, 'orignal_posts')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'post')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_post_number(directory_name):
    """Extract post number from directory name like '0001_Title'."""
    return directory_name.split('_')[0]

def format_date(date_str):
    """Format date string for display."""
    if not date_str:
        return 'Unknown Date'
    try:
        return datetime.fromisoformat(date_str).strftime('%B %d, %Y')
    except:
        return date_str

def load_post_json(post_path):
    """Load post metadata from post.json."""
    json_file = os.path.join(post_path, 'post.json')
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_post_content(post_path):
    """Load post HTML content from content.html."""
    content_file = os.path.join(post_path, 'content.html')
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return '<p>[Post content is unavailable]</p>'

def generate_html_page(post_num, metadata, content):
    """Generate HTML page using Style 3 template."""
    
    title = metadata.get('title', 'Untitled Post')
    publish_date = format_date(metadata.get('publish_date'))
    original_url = metadata.get('original_url', '#')
    
    # Extract read time estimate (word count / 250 words per minute)
    read_time = '5 min read'  # default
    try:
        word_count = len(content.split())
        read_time = f'{max(1, word_count // 250)} min read'
    except:
        pass
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #3a3f47 0%, #5a6270 100%);
            min-height: 100vh;
            color: #333;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        /* Header Navigation */
        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .header h1 {{
            font-size: 24px;
            color: #3a3f47;
            font-weight: 600;
        }}

        .nav-links {{
            display: flex;
            gap: 20px;
        }}

        .nav-links a {{
            text-decoration: none;
            color: #5a6270;
            font-weight: 500;
            transition: color 0.3s;
            padding: 8px 16px;
            border-radius: 4px;
            background: #f0f0f0;
        }}

        .nav-links a:hover {{
            background: #3a3f47;
            color: white;
        }}

        /* Post Container */
        .post {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            margin-bottom: 30px;
        }}

        /* Post Header */
        .post-header {{
            background: linear-gradient(135deg, #3a3f47 0%, #5a6270 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .post-header h1 {{
            font-size: 36px;
            margin-bottom: 20px;
            line-height: 1.4;
            font-weight: 700;
        }}

        .post-meta {{
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 14px;
            opacity: 0.9;
            flex-wrap: wrap;
        }}

        .post-meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .meta-icon {{
            width: 20px;
            height: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            font-size: 12px;
        }}

        /* Post Content */
        .post-content {{
            padding: 40px 30px;
            line-height: 1.8;
        }}

        .post-content h2 {{
            font-size: 24px;
            margin: 30px 0 15px 0;
            color: #3a3f47;
            border-left: 4px solid #5a6270;
            padding-left: 15px;
        }}

        .post-content h3 {{
            font-size: 18px;
            margin: 20px 0 10px 0;
            color: #5a6270;
        }}

        .post-content p {{
            margin-bottom: 15px;
            color: #555;
        }}

        .post-content code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #d63384;
        }}

        .post-content pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 20px 0;
            border-left: 4px solid #5a6270;
        }}

        .post-content pre code {{
            color: #333;
            padding: 0;
            background: none;
        }}

        .post-content ul, .post-content ol {{
            margin: 15px 0 15px 30px;
        }}

        .post-content li {{
            margin-bottom: 8px;
        }}

        .post-content blockquote {{
            border-left: 4px solid #5a6270;
            padding: 15px 20px;
            margin: 20px 0;
            background: #f9f9f9;
            color: #666;
            font-style: italic;
        }}

        .post-content img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border-radius: 6px;
        }}

        /* Post Footer */
        .post-footer {{
            background: #f8f9fa;
            padding: 30px;
            border-top: 1px solid #eee;
        }}

        .post-tags {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}

        .tag {{
            background: linear-gradient(135deg, #3a3f47 0%, #5a6270 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            transition: transform 0.2s;
        }}

        .tag:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(58, 63, 71, 0.3);
        }}

        .post-navigation {{
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-top: 20px;
        }}

        .nav-button {{
            flex: 1;
            padding: 15px 20px;
            background: linear-gradient(135deg, #3a3f47 0%, #5a6270 100%);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            text-decoration: none;
            text-align: center;
        }}

        .nav-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(58, 63, 71, 0.3);
        }}

        .nav-button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        /* External Link */
        .original-link {{
            background: white;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .original-link a {{
            color: #5a6270;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }}

        .original-link a:hover {{
            color: #3a3f47;
            text-decoration: underline;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .post-header h1 {{
                font-size: 24px;
            }}

            .post-meta {{
                flex-direction: column;
                gap: 10px;
            }}

            .post-content {{
                padding: 25px 20px;
            }}

            .nav-links {{
                flex-direction: column;
                gap: 10px;
            }}

            .header {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}

            .post-navigation {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Navigation -->
        <div class="header">
            <h1>📚 博客</h1>
            <div class="nav-links">
                <a href="index.html">首页</a>
                <a href="#about">关于</a>
                <a href="#contact">联系</a>
            </div>
        </div>

        <!-- Original Link -->
        <div class="original-link">
            <a href="{original_url}" target="_blank">🔗 查看原始文章</a>
        </div>

        <!-- Blog Post -->
        <article class="post">
            <!-- Post Header -->
            <div class="post-header">
                <h1>{title}</h1>
                <div class="post-meta">
                    <div class="post-meta-item">
                        <span class="meta-icon">📅</span>
                        <span>{publish_date}</span>
                    </div>
                    <div class="post-meta-item">
                        <span class="meta-icon">📖</span>
                        <span>{read_time}</span>
                    </div>
                </div>
            </div>

            <!-- Post Content -->
            <div class="post-content">
                {content}
            </div>

            <!-- Post Footer -->
            <div class="post-footer">
                <div class="post-navigation">
                    <button class="nav-button" onclick="window.history.back()">← 上一篇</button>
                    <button class="nav-button" onclick="window.location.href='index.html'">返回首页</button>
                    <button class="nav-button" onclick="window.history.forward()">下一篇 →</button>
                </div>
            </div>
        </article>
    </div>
</body>
</html>"""
    
    return html_template

def main():
    """Main conversion process."""
    
    # Scan posts directory directly
    posts_path = Path(POSTS_DIR)
    post_dirs = sorted([d for d in posts_path.iterdir() if d.is_dir() and d.name[0].isdigit()])
    
    if not post_dirs:
        print(f"❌ No post directories found in {POSTS_DIR}")
        return
    
    total_posts = len(post_dirs)
    print(f"🔄 Converting {total_posts} posts to HTML pages...")
    print(f"📁 Output directory: {OUTPUT_DIR}/")
    print()
    
    successful = 0
    failed = 0
    
    for i, post_dir in enumerate(post_dirs, 1):
        try:
            # Extract post number from directory name
            dir_name = post_dir.name
            post_num = dir_name.split('_')[0]
            
            # Load post data
            metadata = load_post_json(str(post_dir))
            content = load_post_content(str(post_dir))
            
            # Generate HTML
            html_content = generate_html_page(post_num, metadata, content)
            
            # Save HTML file
            output_file = os.path.join(OUTPUT_DIR, f'{post_num}.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            successful += 1
            title = metadata.get('title', 'Untitled')[:40]
            print(f"✅ [{i:3d}/{total_posts}] {post_num}.html - {title}...")
            
        except Exception as e:
            failed += 1
            print(f"❌ [{i:3d}/{total_posts}] Error: {str(e)}")
    
    print()
    print("=" * 60)
    print(f"📊 Conversion Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Output directory: {OUTPUT_DIR}/")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for i, post_dir in enumerate(post_dirs, 1):
        try:
            # Extract post number from directory name
            dir_name = post_dir.name
            post_num = dir_name.split('_')[0]
            
            # Load post data
            metadata = load_post_json(post_dir)
            content = load_post_content(post_dir)
            
            # Generate HTML
            html_content = generate_html_page(post_num, metadata, content)
            
            # Save HTML file
            output_file = os.path.join(OUTPUT_DIR, f'{post_num}.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            successful += 1
            title = metadata.get('title', 'Untitled')[:40]
            print(f"✅ [{i:3d}/{total_posts}] {post_num}.html - {title}...")
            
        except Exception as e:
            failed += 1
            print(f"❌ [{i:3d}/{total_posts}] Error: {str(e)}")

if __name__ == '__main__':
    main()
