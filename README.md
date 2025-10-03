# Azure Video Upload Web Application

A production-ready Flask web application for uploading videos to Azure Blob Storage, featuring private networking, managed identity authentication, and optional Microsoft Entra ID user authentication.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)

## 🌟 Features

- **📤 Video Upload**: Drag-and-drop or file picker interface for uploading videos
- **🔒 Private Networking**: VNet integration with private endpoints for secure communication
- **🔐 Managed Identity**: Passwordless authentication to Azure Storage using system-assigned managed identity
- **👤 Optional Authentication**: Microsoft Entra ID (Azure AD) integration for user authentication
- **🏗️ Infrastructure as Code**: Complete Azure Bicep templates for reproducible deployments
- **📊 Health Monitoring**: Built-in health check endpoint for monitoring
- **🎨 Modern UI**: Responsive Bootstrap 5 interface with drag-and-drop support
- **📱 Mobile Friendly**: Works seamlessly on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) (2.77.0+)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) (1.19.0+)
- Active Azure subscription
- Python 3.11+ (for local development)

### Deploy to Azure (Recommended)

```bash
# Clone the repository
git clone https://github.com/bradcstevens/az-storage-upload-web-app.git
cd az-storage-upload-web-app

# Login to Azure
azd auth login

# Deploy infrastructure and application
azd up
```

That's it! The deployment takes ~5-8 minutes and creates all necessary Azure resources.

## 📚 Documentation

- **[Deployment Checklist](docs/DEPLOYMENT-CHECKLIST.md)** - Step-by-step deployment guide with verification steps
- **[Authentication Guide](AUTHENTICATION-GUIDE.md)** - How to enable Microsoft Entra ID authentication
- **[Storage Access Guide](docs/STORAGE-ACCESS-GUIDE.md)** - Access and manage blob storage with Storage Explorer
- **[Infrastructure README](infra/README.md)** - Detailed Bicep module documentation

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ↓
┌─────────────────────────────────────┐
│  Azure App Service (Linux/Python)   │
│  ┌───────────────────────────────┐  │
│  │  Flask Application            │  │
│  │  - Gunicorn WSGI Server       │  │
│  │  - System Managed Identity    │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  Optional: Easy Auth V2       │  │
│  │  (Microsoft Entra ID)         │  │
│  └───────────────────────────────┘  │
└──────┬──────────────────────────────┘
       │ Private VNet
       │ Integration
       ↓
┌─────────────────────────────────────┐
│  Virtual Network                    │
│  ┌─────────────┐  ┌──────────────┐ │
│  │ App Service │  │   Private    │ │
│  │   Subnet    │  │   Endpoint   │ │
│  │             │  │   Subnet     │ │
│  └─────────────┘  └──────┬───────┘ │
└───────────────────────────┼─────────┘
                            │
                            ↓
                   ┌────────────────┐
                   │ Azure Storage  │
                   │ (Private only) │
                   │ ┌────────────┐ │
                   │ │   videos   │ │
                   │ │ container  │ │
                   │ └────────────┘ │
                   └────────────────┘
```

## 🔐 Security Features

- ✅ **Zero secrets**: Managed Identity eliminates need for storage keys
- ✅ **Private networking**: Storage accessible only via private endpoint
- ✅ **HTTPS only**: TLS 1.2+ enforced on all connections
- ✅ **Optional user auth**: Microsoft Entra ID integration available
- ✅ **RBAC**: Role-based access control for storage
- ✅ **Automatic permissions**: Deployment account gets Storage Blob Data Contributor

## 💻 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AZURE_STORAGE_ACCOUNT_NAME="your-storage-account"
export CONTAINER_NAME="videos"
export FLASK_ENV="development"

# Run locally
python app.py
```

Visit http://localhost:8000

## 🔧 Configuration

### Default Deployment (No Authentication)

```bash
azd up
```

Perfect for development and testing.

### Production Deployment (With Authentication)

```bash
# Set environment variables
export ENABLE_AUTHENTICATION=true
export AUTH_CLIENT_ID="<your-azure-ad-app-id>"
export AUTH_CLIENT_SECRET="<your-client-secret>"

# Deploy
azd up
```

See [Authentication Guide](AUTHENTICATION-GUIDE.md) for complete setup.

## 📦 Infrastructure Components

| Resource | Description | SKU |
|----------|-------------|-----|
| **App Service Plan** | Hosts the Flask application | B1 Basic (Linux) |
| **App Service** | Python 3.11 runtime with Gunicorn | - |
| **Storage Account** | Blob storage for videos | Standard LRS |
| **Virtual Network** | Private networking | - |
| **Private Endpoint** | Secure storage access | - |
| **Managed Identity** | Passwordless authentication | System-assigned |

**Estimated Cost**: ~$20-25/month

## 🧪 Testing

### Health Check

```bash
curl https://<your-app-name>.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "azure_storage": "connected",
  "auth_method": "managed-identity"
}
```

### Video Upload

1. Navigate to your application URL
2. Drag-and-drop a video file (MP4, AVI, MOV, WMV)
3. Click "Upload"
4. Verify success message

## 🛠️ Technologies

- **Backend**: Python 3.11, Flask, Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5
- **Cloud**: Azure App Service, Azure Blob Storage, Azure VNet
- **IaC**: Azure Bicep, Azure Developer CLI (azd)
- **Authentication**: Azure Managed Identity, Microsoft Entra ID (optional)

## 📊 Supported Video Formats

- MP4 (`.mp4`)
- AVI (`.avi`)
- MOV (`.mov`)
- WMV (`.wmv`)

Maximum file size: 100 MB (configurable)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- UI powered by [Bootstrap 5](https://getbootstrap.com/)
- Icons from [Bootstrap Icons](https://icons.getbootstrap.com/)

## 📞 Support

- **Documentation**: Check the [docs](docs/) folder
- **Issues**: [GitHub Issues](https://github.com/bradcstevens/az-storage-upload-web-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bradcstevens/az-storage-upload-web-app/discussions)

---

**Made with ❤️ using Azure and Python**
