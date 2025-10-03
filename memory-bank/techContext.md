# Memory Bank: Technical Context

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: Flask 3.0+
- **Azure SDK**: azure-storage-blob (v12.x)
- **CORS**: flask-cors 4.0+
- **Configuration**: python-dotenv 1.0+
- **Production Server**: Gunicorn 21.2+

### Frontend
- **Core**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3.x (CDN)
- **HTTP Client**: Fetch API (native browser support)
- **File Handling**: File API, FormData API

### Infrastructure
- **Compute**: Azure App Service (Linux, Python 3.11 runtime, B1 Basic tier)
- **Storage**: Azure Blob Storage (Standard performance, Hot access tier)
- **Container**: Single blob container named "videos"
- **Region**: [To be determined based on user location]

## Development Environment

### Required Tools
- Python 3.11 or higher
- pip (Python package manager)
- Azure CLI (for deployment and resource management)
- Git (version control)
- Text editor/IDE (VS Code recommended)
- Web browser (Chrome/Firefox/Safari for testing)

### Setup Instructions

1. **Install Python 3.11+**
   - macOS: `brew install python@3.11` or download from python.org
   - Verify: `python3 --version`

2. **Install Azure CLI**
   - macOS: `brew install azure-cli`
   - Verify: `az --version`
   - Login: `az login`

3. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd az-storage-upload-web-app
   ```

4. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add Azure Storage connection string
   - Configure other environment variables

7. **Run Local Development Server**
   ```bash
   python app.py
   # or
   flask run
   ```

## Dependencies

### Python Packages (requirements.txt)
```
Flask>=3.0.0
azure-storage-blob>=12.19.0
python-dotenv>=1.0.0
flask-cors>=4.0.0
gunicorn>=21.2.0
```

### Frontend Dependencies (CDN)
- Bootstrap 5.3.x: https://cdn.jsdelivr.net/npm/bootstrap@5.3.x/dist/css/bootstrap.min.css
- Bootstrap JS: https://cdn.jsdelivr.net/npm/bootstrap@5.3.x/dist/js/bootstrap.bundle.min.js

### Azure Resources (External Dependencies)
- Azure Storage Account
- Azure Blob Container
- Azure App Service

## Technical Constraints

### File Upload Constraints
- **Maximum file size**: 100MB per file (MVP limitation)
- **Supported formats**: mp4, mov, avi, mkv, webm
- **Upload method**: HTTP POST multipart/form-data
- **Timeout**: 300 seconds (5 minutes) for upload operations

### Azure Service Constraints
- **App Service**: B1 Basic tier (1.75GB RAM, 100 total ACU)
- **Storage**: Standard performance tier (scalable, but not premium speed)
- **Blob naming**: Must follow Azure blob naming conventions
- **Connection**: Requires stable internet connection for Azure operations

### Browser Compatibility
- **Target browsers**: Modern browsers with ES6+ support
- **Required APIs**: File API, FormData API, Fetch API
- **Minimum versions**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+

## Infrastructure

### Local Development
- **Server**: Flask development server (localhost:5000)
- **Storage**: Azure Blob Storage (connection via internet)
- **Configuration**: .env file for environment variables

### Production (Azure)
- **Hosting**: Azure App Service (Linux)
- **Runtime**: Python 3.11
- **Web Server**: Gunicorn WSGI server
- **Storage**: Azure Blob Storage (same as development)
- **Configuration**: Azure App Service Application Settings
- **Logging**: Azure App Service diagnostic logs
- **Monitoring**: Azure Application Insights (optional enhancement)

### Network Architecture
```
User Browser → Azure App Service (Flask API) → Azure Blob Storage
                     ↓
              Application Logs
```

### Environment Variables Required
- `AZURE_STORAGE_CONNECTION_STRING`: Connection string for Azure Storage Account
- `AZURE_STORAGE_CONTAINER_NAME`: Name of blob container (default: "videos")
- `FLASK_ENV`: development or production
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 100)

## Security Considerations

### Current Implementation (MVP)
1. **Backend Proxy Pattern**
   - Client never directly accesses Azure Storage
   - All uploads go through Flask backend
   - Storage credentials never exposed to client

2. **Input Validation**
   - Server-side file type validation
   - Server-side file size validation
   - Sanitized blob names (prevent injection)

3. **CORS Configuration**
   - Controlled CORS policy on Flask API
   - Only necessary origins allowed

4. **Environment Variables**
   - Sensitive data in environment variables
   - .env file excluded from version control
   - Azure App Settings for production secrets

### Future Enhancements (Post-MVP)
1. **Authentication & Authorization**
   - User authentication (Azure AD, OAuth)
   - Role-based access control
   - Per-user storage quotas

2. **SAS Token Implementation**
   - Generate SAS tokens with limited permissions
   - Time-limited access to blobs
   - Reduced backend load for large files

3. **HTTPS Enforcement**
   - Force HTTPS for all connections
   - HSTS headers

4. **Rate Limiting**
   - Prevent abuse of upload endpoint
   - Per-user rate limits

5. **Malware Scanning**
   - Scan uploaded files for malware
   - Integration with Azure Defender

## Performance Considerations

### Current Design
- **Streaming uploads**: Azure SDK supports streaming to avoid memory issues
- **Asynchronous operations**: Consider async Flask for better concurrency
- **CDN for static assets**: Bootstrap loaded from CDN (fast, cached)

### Optimization Opportunities
- Implement chunked uploads for large files
- Add upload progress tracking with websockets
- Use Azure CDN for blob delivery
- Implement blob compression
- Add caching headers for static content

## Deployment Architecture

### Development → Production Pipeline
1. Local development with .env configuration
2. Git commit and push to repository
3. Azure App Service deployment (Git or ZIP deploy)
4. Automatic environment variable configuration from App Settings
5. Application restart and health check

### Deployment Commands
```bash
# Login to Azure
az login

# Create Resource Group (one-time)
az group create --name <resource-group> --location <region>

# Create Storage Account (one-time)
az storage account create --name <storage-account> --resource-group <resource-group>

# Create App Service Plan (one-time)
az appservice plan create --name <plan-name> --resource-group <resource-group> --sku B1 --is-linux

# Create Web App (one-time)
az webapp create --name <app-name> --resource-group <resource-group> --plan <plan-name> --runtime "PYTHON:3.11"

# Configure App Settings
az webapp config appsettings set --name <app-name> --resource-group <resource-group> --settings AZURE_STORAGE_CONNECTION_STRING="<connection-string>"

# Deploy Application
az webapp deploy --name <app-name> --resource-group <resource-group> --src-path <zip-file>
```
