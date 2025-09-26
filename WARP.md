# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Django-based Academic Journal Management System designed for publishing and managing academic articles. The system supports Turkish language content and provides features for authors, editors, and readers.

## Development Commands

### Environment Setup
```powershell
# Create and activate virtual environment (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```powershell
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```powershell
# Run development server
python manage.py runserver

# Run server on specific port
python manage.py runserver 8080
```

### Testing
```powershell
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test articles
python manage.py test users
python manage.py test pages
python manage.py test core
python manage.py test dashboard

# Run specific test class or method
python manage.py test articles.tests.MakaleModelTest
python manage.py test articles.tests.MakaleModelTest.test_slug_generation
```

### Data Management
```powershell
# Collect static files for production
python manage.py collectstatic

# Load/dump data
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json

# Django shell for debugging
python manage.py shell
```

## Architecture Overview

### Application Structure
- **users**: Custom user authentication with editor permissions and author profiles
- **articles**: Core article management (Makale, Yazar, DergiSayisi models)
- **pages**: Static pages (home, about, contact) and contact form handling
- **core**: Shared utilities, mixins, and context processors
- **dashboard**: Admin/editor dashboard for content management
- **academic_journal**: Main Django project configuration

### Key Models Architecture

#### User System
- Custom `User` model extends `AbstractUser` with academic-specific fields
- One-to-one relationship with `Yazar` (Author) model for article attribution
- Editor permissions system (`is_editor` flag)
- Profile management with resume uploads and biographical information

#### Article System
- `Makale` (Article): Main content model with slug-based URLs, PDF uploads, publication status
- `Yazar` (Author): Flexible author system supporting both registered users and external authors
- `DergiSayisi` (Journal Issue): Groups articles into journal issues/volumes
- Many-to-many relationship between articles and authors
- Automatic slug generation from Turkish titles
- View tracking and publication workflow

#### Content Management Flow
1. Authors create articles through dashboard or admin
2. Editors review and approve articles (`goster_makaleler_sayfasinda` flag)
3. Articles are organized into journal issues
4. Public article listing shows only approved articles
5. Admin notes system for editorial communication

### Template Structure
- Base template with Bootstrap 5 and modern styling
- Turkish language localization throughout
- Responsive design with mobile-first approach
- Static files organized in `/static/` directory
- Media uploads handled through `/media/` directory

### URL Architecture
```
/ - Homepage and static pages (pages app)
/kullanici/ - User authentication and profiles (users app)  
/makaleler/ - Article listings and details (articles app)
/dashboard/ - Editor/admin dashboard (dashboard app)
/admin/ - Django admin interface
```

### File Upload Strategy
- UUID-based file naming to prevent conflicts
- Organized into subfolders: `profile_pics/`, `resumes/`, `article_pdfs/`
- Image handling for profile pictures using Pillow
- PDF validation for article uploads

## Development Guidelines

### Language and Localization
- Primary language: Turkish (`LANGUAGE_CODE = 'tr-tr'`)
- Timezone: Europe/Istanbul
- All model verbose names and help texts in Turkish
- Template content and UI strings in Turkish

### Database Configuration
- SQLite for development (included in repository)
- Models use Turkish field names and verbose names
- Custom `AUTH_USER_MODEL` points to `users.User`

### Security Considerations
- DEBUG mode enabled for development
- Secret key hardcoded (change for production)
- ALLOWED_HOSTS configured for localhost
- CSRF protection enabled
- File upload security through UUID naming

### Key Django Apps Integration
- `django-widget-tweaks` for form styling
- Bootstrap 5 CDN for UI framework
- Bootstrap Icons for iconography
- Custom context processors for navigation

### Testing Strategy
- Each app includes `tests.py` for unit tests
- Models include validation testing
- Views tested for permission and functionality
- Forms tested for validation logic

## Common Development Patterns

### Model Patterns
- UUID-based file paths for security
- Automatic slug generation with conflict resolution
- Soft delete patterns (publication flags vs actual deletion)
- Admin notification system with read/unread tracking

### View Patterns
- Class-based views with Django's generic views
- Custom mixins for permission checking (`AdminRequiredMixin`, `AuthorRequiredMixin`)
- ListView with search and filtering capabilities
- Ajax endpoints for dynamic content

### Form Patterns
- ModelForm usage for database integration
- Custom validation in form classes
- Widget customization through django-widget-tweaks
- Multi-model form handling (User + Yazar relationship)

### Permission System
- Built-in Django auth system extended
- Custom `is_editor` flag for editorial permissions
- Object-level permissions through mixins
- Separation between authors and editors

## File and Directory Structure Notes

- Virtual environment in `.venv/` (excluded from git)
- Media files stored in `media/` directory
- Static files in `static/` directory  
- PyCharm IDE configuration in `.idea/` directory
- Database file `db.sqlite3` in root directory
- Main settings in `academic_journal/settings.py`