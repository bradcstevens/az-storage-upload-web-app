# Memory Bank: System Patterns

## Architecture Overview

This application follows a **Backend Proxy Pattern** for secure cloud storage integration. The architecture consists of three main layers:

1. **Presentation Layer**: Static HTML/CSS/JavaScript frontend
2. **Application Layer**: Flask REST API backend
3. **Storage Layer**: Azure Blob Storage

The backend acts as a secure proxy between the client and Azure Storage, ensuring storage credentials are never exposed to end users.

## Design Patterns

### 1. Backend Proxy Pattern
**Purpose**: Secure access to cloud storage without exposing credentials

**Implementation**:
- Client uploads files to Flask API endpoint
- Flask API validates and processes upload request
- Flask API uses Azure SDK to upload to Blob Storage
- Flask API returns upload status to client

**Benefits**:
- Security: Storage credentials protected
- Control: Centralized validation and business logic
- Flexibility: Easy to add authentication/authorization later

### 2. RESTful API Design
**Purpose**: Clean, predictable API interface

**Endpoints**:
- `POST /api/upload` - Upload video files
- `GET /api/videos` - List uploaded videos
- `GET /health` - Health check endpoint

**Benefits**:
- Standardized HTTP methods
- Stateless operations
- Easy to test and document

### 3. Configuration Management Pattern
**Purpose**: Environment-specific configuration

**Implementation**:
- Development: `.env` file with python-dotenv
- Production: Azure App Service Application Settings
- Code reads from environment variables

**Benefits**:
- Separation of config from code
- Security: Secrets not in version control
- Portability: Easy environment switching

### 4. Separation of Concerns
**Purpose**: Modular, maintainable code structure

**Structure**:
```
/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── routes/
│   ├── upload.py       # Upload endpoint logic
│   └── videos.py       # Video listing logic
├── services/
│   └── azure_storage.py # Azure Blob Storage operations
├── utils/
│   └── validators.py   # File validation utilities
├── static/
│   ├── css/           # Styles
│   └── js/            # Client-side JavaScript
└── templates/
    └── index.html     # Main HTML template
```

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   User Browser  │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │ HTTP/HTTPS
         │ (Fetch API)
         ↓
┌─────────────────┐
│  Azure App      │
│  Service        │
│  (Flask API)    │
└────────┬────────┘
         │ Azure SDK
         │ (azure-storage-blob)
         ↓
┌─────────────────┐
│  Azure Blob     │
│  Storage        │
│  (videos        │
│   container)    │
└─────────────────┘
```

### Component Architecture

#### Frontend Components
1. **Upload Interface**
   - File input / drag-and-drop zone
   - Multiple file selection support
   - Client-side validation (UX)
   - Progress indication (visual feedback)

2. **Video List Display**
   - Fetches list from API
   - Displays video metadata
   - Provides blob URLs for access

3. **Error Handling**
   - Display API errors to user
   - Network error handling
   - Validation error messages

#### Backend Components
1. **Flask Application (app.py)**
   - Application initialization
   - Route registration
   - CORS configuration
   - Error handling

2. **Upload Service**
   - Accept multipart file uploads
   - Validate file type and size
   - Generate unique blob names
   - Stream upload to Azure
   - Return upload results

3. **Video Service**
   - List blobs from container
   - Extract blob metadata
   - Generate blob URLs
   - Return JSON response

4. **Azure Storage Service**
   - Initialize BlobServiceClient
   - Upload blob operations
   - List blob operations
   - Handle Azure SDK exceptions

5. **Validation Utilities**
   - File extension validation
   - MIME type validation
   - File size validation
   - Input sanitization

### Data Flow

#### Upload Flow
```
1. User selects video file(s)
   ↓
2. Client validates file (type, size)
   ↓
3. Client sends POST to /api/upload
   ↓
4. Flask receives multipart/form-data
   ↓
5. Flask validates file (server-side)
   ↓
6. Flask generates unique blob name
   ↓
7. Flask uploads to Azure Blob Storage
   ↓
8. Azure returns upload confirmation
   ↓
9. Flask returns success response
   ↓
10. Client displays success message
```

#### List Videos Flow
```
1. Client sends GET to /api/videos
   ↓
2. Flask queries Azure Blob Storage
   ↓
3. Azure returns list of blobs
   ↓
4. Flask formats blob metadata
   ↓
5. Flask returns JSON response
   ↓
6. Client displays video list
```

### Error Handling Flow
```
Error Occurs
   ↓
Azure SDK Exception? → Flask catches → Logs error → Returns 500
   ↓
Validation Error? → Flask catches → Returns 400 with message
   ↓
Network Error? → Client catches → Displays retry option
```

## Integration Patterns

### Azure Blob Storage Integration

**Connection Management**:
- Single BlobServiceClient instance
- Connection string from environment variable
- Lazy initialization pattern

**Upload Strategy**:
- Stream-based upload (memory efficient)
- Unique blob names: `timestamp_uuid_originalname.ext`
- Content-type detection from file extension
- Overwrite protection with unique names

**Error Handling**:
- Catch Azure SDK exceptions
- Retry logic for transient failures (future)
- Graceful degradation

### CORS Integration

**Flask-CORS Configuration**:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # MVP: Allow all, restrict in production
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### Frontend-Backend Integration

**Upload Request**:
```javascript
const formData = new FormData();
formData.append('file', file);

fetch('/api/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => /* handle success */)
.catch(error => /* handle error */);
```

**List Request**:
```javascript
fetch('/api/videos')
    .then(response => response.json())
    .then(videos => /* display videos */)
    .catch(error => /* handle error */);
```

## Best Practices

### Security Best Practices
1. **Never expose credentials to client**
   - Use backend proxy pattern
   - Environment variables for secrets
   - No hardcoded credentials

2. **Validate all inputs**
   - Client-side (UX)
   - Server-side (security)
   - Whitelist allowed file types

3. **Use HTTPS in production**
   - Azure App Service provides free SSL
   - Force HTTPS redirects

### Code Quality Best Practices
1. **Separation of concerns**
   - Routes handle HTTP
   - Services handle business logic
   - Utilities handle reusable functions

2. **Error handling**
   - Try-catch blocks for Azure operations
   - Meaningful error messages
   - Proper HTTP status codes

3. **Configuration management**
   - Environment variables for all config
   - Validation of required variables
   - Sensible defaults where appropriate

### Performance Best Practices
1. **Streaming uploads**
   - Use Azure SDK streaming
   - Avoid loading entire file into memory

2. **Async operations** (future)
   - Consider async Flask for better concurrency
   - Non-blocking I/O

3. **CDN for static assets**
   - Bootstrap from CDN
   - Browser caching

### Deployment Best Practices
1. **Version pinning**
   - Pin dependency versions in requirements.txt
   - Test before updating dependencies

2. **Environment parity**
   - Test with production-like configuration
   - Use same Python version locally and in Azure

3. **Health checks**
   - Implement /health endpoint
   - Monitor application availability

### Scalability Considerations
1. **Stateless design**
   - No session storage in application
   - Easy to scale horizontally

2. **Cloud-native architecture**
   - Leverage Azure managed services
   - Auto-scaling capabilities (future)

3. **Resource optimization**
   - Appropriate App Service tier (B1 for MVP)
   - Storage lifecycle policies (future)

## Future Enhancements

### Architecture Evolution
1. **Add authentication layer**
   - Azure AD integration
   - OAuth 2.0 support
   - User-specific storage containers

2. **Implement caching**
   - Redis cache for video metadata
   - Reduce storage API calls

3. **Add message queue**
   - Azure Queue Storage for async processing
   - Video transcoding pipeline

4. **Microservices split** (if needed)
   - Separate upload service
   - Separate listing service
   - API gateway pattern

### Pattern Enhancements
1. **Circuit breaker pattern**
   - Handle Azure service outages gracefully
   - Fallback mechanisms

2. **Retry pattern with exponential backoff**
   - Automatic retry for transient failures
   - Configurable retry policies

3. **Repository pattern**
   - Abstract storage operations
   - Easy to switch storage providers

## Documentation Standards

### Code Documentation
- Docstrings for all functions
- Inline comments for complex logic
- Type hints for parameters and returns

### API Documentation
- Endpoint descriptions
- Request/response examples
- Error response documentation
- OpenAPI/Swagger specification (future)
