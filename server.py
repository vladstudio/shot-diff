#!/usr/bin/env python3
"""
Simple web server for shot-diff image comparison.
Usage: python server.py
Access: https://shot-diff.kadoa.dev/?i1=URL_TO_IMAGE1&i2=URL_TO_IMAGE2
"""

import os
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse
import requests
from flask import Flask, request, send_file, jsonify
from shot_diff import ShotDiff

app = Flask(__name__)

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
TIMEOUT = 30  # seconds
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def is_valid_image_url(url):
    """Basic URL validation."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and parsed.netloc
    except:
        return False

def download_image(url, filepath):
    """Download image from URL to filepath."""
    headers = {
        'User-Agent': 'shot-diff/1.0'
    }
    
    response = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
    response.raise_for_status()
    
    # Check content length
    content_length = response.headers.get('content-length')
    if content_length and int(content_length) > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {content_length} bytes")
    
    # Check content type
    content_type = response.headers.get('content-type', '').lower()
    if not any(ct in content_type for ct in ['image/jpeg', 'image/png', 'image/webp']):
        raise ValueError(f"Invalid content type: {content_type}")
    
    # Download with size limit
    with open(filepath, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                downloaded += len(chunk)
                if downloaded > MAX_FILE_SIZE:
                    raise ValueError("File too large during download")
                f.write(chunk)

@app.route('/')
def compare_images():
    """Main endpoint for image comparison."""
    try:
        # Get URL parameters
        img1_url = request.args.get('i1')
        img2_url = request.args.get('i2')
        
        if not img1_url or not img2_url:
            return jsonify({'error': 'Missing i1 or i2 parameters'}), 400
        
        # Validate URLs
        if not is_valid_image_url(img1_url) or not is_valid_image_url(img2_url):
            return jsonify({'error': 'Invalid image URLs'}), 400
        
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix='shotdiff_'))
        
        try:
            # Generate unique filenames
            session_id = str(uuid.uuid4())[:8]
            img1_path = temp_dir / f"img1_{session_id}.png"
            img2_path = temp_dir / f"img2_{session_id}.png"
            
            # Download images
            download_image(img1_url, img1_path)
            download_image(img2_url, img2_path)
            
            # Run shot diff
            shot_diff = ShotDiff()
            results = shot_diff.compare_images(str(img1_path), str(img2_path), str(temp_dir))
            
            overlay_path = results['overlay_path']
            
            # Return the overlay image
            return send_file(overlay_path, mimetype='image/png')
            
        finally:
            # Cleanup temporary files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download image: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)