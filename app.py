"""
Azure Video Upload Web Application
Flask backend with Azure Blob Storage integration
Uses Managed Identity for secure authentication
"""
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential
from werkzeug.utils import secure_filename
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

# Azure Storage configuration
AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'videos')

# Initialize Azure Blob Service Client with Managed Identity
try:
    if AZURE_STORAGE_ACCOUNT_NAME:
        # Use DefaultAzureCredential for authentication
        # In Azure App Service, this will use the managed identity
        credential = DefaultAzureCredential()
        account_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        logger.info("✅ Azure Blob Storage client initialized with Managed Identity")
    else:
        blob_service_client = None
        logger.warning("⚠️ Azure Storage account name not configured")
except Exception as e:
    blob_service_client = None
    logger.error(f"❌ Failed to initialize Azure Blob Storage client: {str(e)}")


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def get_content_type(filename):
    """Get content type based on file extension"""
    extension = get_file_extension(filename)
    content_types = {
        'mp4': 'video/mp4',
        'mov': 'video/quicktime',
        'avi': 'video/x-msvideo',
        'mkv': 'video/x-matroska',
        'webm': 'video/webm'
    }
    return content_types.get(extension, 'application/octet-stream')


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    azure_configured = blob_service_client is not None
    auth_method = 'managed-identity' if AZURE_STORAGE_ACCOUNT_NAME else 'not-configured'
    return jsonify({
        'status': 'healthy',
        'azure_storage': 'connected' if azure_configured else 'not_configured',
        'auth_method': auth_method,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload video file to Azure Blob Storage"""
    try:
        # Check if Azure Storage is configured
        if not blob_service_client:
            return jsonify({
                'success': False,
                'error': 'Azure Storage not configured',
                'message': 'Please configure AZURE_STORAGE_CONNECTION_STRING environment variable'
            }), 500
        
        # Check if files are present in request
        if 'files[]' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided',
                'message': 'Please select files to upload'
            }), 400
        
        files = request.files.getlist('files[]')
        
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'error': 'No files selected',
                'message': 'Please select at least one file to upload'
            }), 400
        
        uploaded_files = []
        errors = []
        
        for file in files:
            try:
                # Validate file
                if not file or file.filename == '':
                    continue
                
                if not allowed_file(file.filename):
                    errors.append({
                        'filename': file.filename,
                        'error': 'Invalid file type',
                        'message': f'Only {", ".join(ALLOWED_EXTENSIONS).upper()} files are allowed'
                    })
                    continue
                
                # Generate unique blob name
                original_filename = secure_filename(file.filename)
                file_extension = get_file_extension(original_filename)
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                
                # Get blob client
                container_client = blob_service_client.get_container_client(CONTAINER_NAME)
                
                # Create container if it doesn't exist
                try:
                    container_client.create_container()
                    logger.info(f"✅ Container '{CONTAINER_NAME}' created")
                except Exception as e:
                    if "ContainerAlreadyExists" not in str(e):
                        logger.warning(f"Container creation: {str(e)}")
                
                blob_client = container_client.get_blob_client(unique_filename)
                
                # Upload file with content type
                content_settings = ContentSettings(content_type=get_content_type(original_filename))
                blob_client.upload_blob(
                    file,
                    overwrite=True,
                    content_settings=content_settings
                )
                
                # Get blob URL
                blob_url = blob_client.url
                
                uploaded_files.append({
                    'filename': original_filename,
                    'blob_name': unique_filename,
                    'size': file.content_length or 0,
                    'url': blob_url,
                    'content_type': get_content_type(original_filename),
                    'uploaded_at': datetime.utcnow().isoformat()
                })
                
                logger.info(f"✅ Uploaded: {original_filename} → {unique_filename}")
                
            except Exception as e:
                logger.error(f"❌ Error uploading {file.filename}: {str(e)}")
                errors.append({
                    'filename': file.filename,
                    'error': 'Upload failed',
                    'message': str(e)
                })
        
        # Prepare response
        response = {
            'success': len(uploaded_files) > 0,
            'files': uploaded_files,
            'total': len(uploaded_files)
        }
        
        if errors:
            response['errors'] = errors
            response['error_count'] = len(errors)
        
        status_code = 200 if uploaded_files else 400
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error',
            'message': str(e)
        }), 500


@app.route('/api/videos', methods=['GET'])
def list_videos():
    """List all uploaded videos from Azure Blob Storage"""
    try:
        # Check if Azure Storage is configured
        if not blob_service_client:
            return jsonify({
                'success': False,
                'error': 'Azure Storage not configured',
                'message': 'Please configure AZURE_STORAGE_CONNECTION_STRING environment variable'
            }), 500
        
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # Check if container exists
        try:
            container_client.get_container_properties()
        except Exception:
            return jsonify({
                'success': True,
                'videos': [],
                'total': 0,
                'message': 'No videos uploaded yet'
            })
        
        # List blobs
        blobs = container_client.list_blobs()
        videos = []
        
        for blob in blobs:
            videos.append({
                'id': blob.name,
                'filename': blob.name,
                'size': blob.size,
                'url': f"{container_client.url}/{blob.name}",
                'content_type': blob.content_settings.content_type if blob.content_settings else 'video/mp4',
                'uploaded_at': blob.last_modified.isoformat() if blob.last_modified else None
            })
        
        return jsonify({
            'success': True,
            'videos': videos,
            'total': len(videos)
        })
        
    except Exception as e:
        logger.error(f"❌ Error listing videos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error',
            'message': str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large',
        'message': 'Maximum file size is 100MB'
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    logger.error(f"❌ Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
