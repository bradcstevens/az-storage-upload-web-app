# Memory Bank: Style Guide

## Design System (Updated 2025-10-02)

### Design Tokens

#### Color Palette
```css
/* Primary Colors - Azure Brand */
--primary-500: #0078d4;  /* Main Azure blue */
--primary-600: #106ebe;  /* Hover state */
--primary-700: #005a9e;  /* Active state */

/* Semantic Colors */
--success-main: #28a745;  /* Upload success */
--error-main: #dc3545;    /* Upload error */
--warning-main: #ffc107;  /* Processing */
--info-main: #17a2b8;     /* Info messages */

/* Neutral Colors */
--neutral-50: #f8f9fa;    /* Light backgrounds */
--neutral-900: #212529;   /* Primary text */

/* Background Colors */
--bg-upload-zone: #f0f7ff;        /* Light azure */
--bg-upload-zone-active: #d6eaff; /* Dragging state */
```

#### Typography
```css
/* Font Family */
--font-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

/* Font Sizes */
--text-base: 1rem;     /* 16px - Base size */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
```

#### Spacing
```css
/* Base unit: 8px */
--space-2: 0.5rem;   /* 8px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */

/* Touch Targets */
--space-touch-target: 44px;  /* Minimum */
--space-touch-gap: 8px;      /* Between targets */
```

#### Responsive Breakpoints
```css
/* Mobile-first approach */
--breakpoint-sm: 768px;   /* Tablet */
--breakpoint-md: 1024px;  /* Desktop */
--breakpoint-lg: 1440px;  /* Large desktop */
```

### Accessibility Standards
- **Color Contrast**: 7:1 for normal text (WCAG AAA)
- **Touch Targets**: 44px minimum height with 8px spacing
- **Keyboard Navigation**: All interactive elements accessible via Tab
- **Screen Reader**: Comprehensive ARIA labels and semantic HTML
- **Focus Indicators**: 3px solid outline in primary color

### Component Naming
- **Atoms**: Simple, descriptive names (UploadButton, StatusBadge)
- **Molecules**: Compound names (FileUploadInputGroup, VideoListItem)
- **Organisms**: Section-based names (UploadZone, VideosList)

## Code Style

### HTML/CSS
- Use semantic HTML5 elements (header, main, section, footer)
- BEM naming for custom CSS classes
- Mobile-first responsive design
- Accessibility attributes required (ARIA labels, roles)

### JavaScript
- ES6+ modern syntax (arrow functions, const/let, promises)
- Modular code organization
- JSDoc comments for functions
- Error handling with try/catch
- Async/await for promises

### Python (Flask)
- PEP 8 style guide
- Type hints for function parameters
- Docstrings for all functions
- Error handling with proper logging
- Environment variables for configuration

## Naming Conventions

### Files
- HTML: lowercase with hyphens (index.html)
- CSS: lowercase with hyphens (styles.css)
- JavaScript: camelCase (uploadHandler.js)
- Python: lowercase with underscores (app.py, upload_handler.py)

### Variables
- CSS: kebab-case (--primary-color)
- JavaScript: camelCase (uploadProgress)
- Python: snake_case (upload_progress)

### Functions
- JavaScript: camelCase (handleFileUpload)
- Python: snake_case (handle_file_upload)

## File Organization

```
/static/
  /css/
    styles.css          # Custom styles
  /js/
    app.js              # Main application
    upload.js           # Upload handling
  /icons/
    favicon.ico
    icon-192.png

/templates/
  index.html            # Main page

/app.py                 # Flask application
/requirements.txt       # Dependencies
/.env                   # Environment variables
/.env.example           # Template
/README.md              # Documentation
```

## Documentation Standards

### Code Comments
- Explain "why", not "what"
- Document complex logic
- Include examples for functions
- Keep comments up-to-date

### README Format
- Project overview
- Setup instructions
- Usage examples
- API documentation
- Troubleshooting guide

### API Documentation
- Endpoint description
- Request format
- Response format
- Error codes
- Examples

## Testing Standards

### Frontend Testing
- Test all user interactions
- Verify file validation
- Check responsive behavior
- Test keyboard navigation
- Screen reader compatibility

### Backend Testing
- Unit tests for functions
- Integration tests for API endpoints
- Test error handling
- Test Azure Storage integration
- Load testing for uploads

### Accessibility Testing
- WCAG AAA compliance verification
- Keyboard navigation testing
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Color contrast verification
- Touch target size verification

## Git Workflow

### Branch Naming
- feature/feature-name
- bugfix/bug-description
- hotfix/urgent-fix

### Commit Messages
- Use conventional commits format
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests

### Pull Requests
- Clear description
- Link to related issues
- Screenshots for UI changes
- Tests passing
- Reviewed by at least one person

## Review Process

### Code Review Checklist
- [ ] Code follows style guide
- [ ] Tests are passing
- [ ] Documentation updated
- [ ] Accessibility requirements met
- [ ] Performance acceptable
- [ ] Security considerations addressed
- [ ] No console errors or warnings
