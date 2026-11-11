# ShopEase – User Management Microservice

## 1. Project Overview

The **ShopEase User Management Microservice** is an independent backend service developed using FastAPI to manage customer profiles, contact information, delivery addresses, and account-related operations.

This service integrates with the existing ShopEase Authentication Microservice using JWT authentication.

Users must authenticate through the Authentication Service before accessing profile and address management APIs.

### Main Features

- Customer profile creation and management.
- Profile retrieval, update, partial update, and deletion.
- User account deactivation.
- Delivery address management.
- Individual address partial updates.
- Default delivery address management.
- JWT-based authentication and authorization.
- User-level data ownership protection.
- Separate MySQL database.
- SQLAlchemy ORM integration.
- Alembic database migrations.
- Docker and Docker Compose support.
- API documentation using Swagger UI.

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Backend programming |
| FastAPI | REST API development |
| MySQL 8 | Database |
| SQLAlchemy | ORM and database operations |
| Alembic | Database migrations |
| Pydantic | Data validation |
| JWT | Authentication |
| HTTPX | Authentication Service communication |
| Docker | Containerization |
| Docker Compose | Multi-container management |
| Swagger UI | API documentation and testing |
| Postman | API testing |

---

## 3. Project Architecture

ShopEase follows a microservices architecture.

The Authentication Service and User Management Service operate independently and maintain separate responsibilities.

### Authentication Service

Responsible for:

- User registration.
- User login.
- Password verification.
- JWT access token generation.
- Token verification.

### User Management Service

Responsible for:

- Customer profile management.
- Contact information management.
- Delivery address management.
- Default address management.
- Profile deactivation.

The User Service does not store passwords or duplicate authentication credentials.

### Architecture Flow

```text
                CUSTOMER
                    |
                    v
          AUTHENTICATION SERVICE
                    |
          Register / Login
                    |
             JWT Generation
                    |
                    v
             ACCESS TOKEN
                    |
                    v
          USER MANAGEMENT SERVICE
                    |
             JWT Verification
                    |
          Extract Auth User ID
                    |
             Profile APIs
                    |
             Address APIs
                    |
                    v
              MYSQL DATABASE
             shopease_user_db
                    |
          +---------+----------+
          |                    |
          v                    v
     user_profiles       user_addresses
```

### Database Separation

The User Management Service maintains its own database:

`shopease_user_db`

Authentication credentials remain inside the Authentication Service database.

---

## 4. Project Folder Structure

```text
shopease-user-service/
│
├── app/
│   ├── main.py
│   │
│   ├── routers/
│   │   ├── user_routes.py
│   │   └── address_routes.py
│   │
│   ├── models/
│   │   ├── user_model.py
│   │   └── address_model.py
│   │
│   ├── schemas/
│   │   ├── user_schema.py
│   │   └── address_schema.py
│   │
│   ├── services/
│   │   ├── user_service.py
│   │   └── address_service.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   └── database/
│       └── connection.py
│
├── alembic/
│   └── versions/
│
├── tests/
│
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .env.example
├── .dockerignore
└── README.md
```

### Responsibilities

| Folder/File | Responsibility |
|---|---|
| main.py | FastAPI application entry point |
| routers/ | API endpoint definitions |
| models/ | SQLAlchemy database models |
| schemas/ | Pydantic request and response validation |
| services/ | Business logic |
| core/config.py | Application configuration |
| core/security.py | JWT authentication and verification |
| database/connection.py | Database engine and sessions |
| alembic/ | Database migration scripts |
| tests/ | API and application tests |

---

## 5. Database Configuration

### Database Name

```text
shopease_user_db
```

### Table 1: user_profiles

Stores customer profile information.

| Column | Description |
|---|---|
| id | Primary key |
| auth_user_id | User ID from Authentication Service |
| full_name | Customer name |
| phone_number | Contact number |
| date_of_birth | Date of birth |
| gender | Gender |
| profile_image | Profile image path or URL |
| is_active | Profile active status |
| created_at | Creation timestamp |
| updated_at | Last update timestamp |

**Important:** `auth_user_id` has a unique constraint to prevent duplicate profiles for the same authentication account.

### Table 2: user_addresses

Stores customer delivery addresses.

| Column | Description |
|---|---|
| id | Primary key |
| user_id | Foreign key referencing user_profiles.id |
| address_type | HOME, OFFICE, or OTHER |
| full_name | Recipient name |
| phone_number | Contact number |
| address_line_1 | Primary address |
| address_line_2 | Additional address |
| city | City |
| state | State |
| country | Country |
| postal_code | Postal code |
| is_default | Default address status |
| created_at | Creation timestamp |

### Database Relationship

One customer profile can have multiple delivery addresses.

```text
user_profiles
      |
      | One-to-Many
      |
      v
user_addresses
```

Each address belongs to one customer profile.

---

## 6. Authentication and Authorization

The User Management Service integrates with the existing Authentication Service using JWT access tokens.

### Authentication Workflow

1. Customer registers through the Authentication Service.
2. Customer logs in through the Authentication Service.
3. Authentication Service validates credentials.
4. Authentication Service generates a JWT access token.
5. Customer sends the JWT token in the Authorization header.
6. User Service verifies the token through the configured Authentication Service verification endpoint.
7. User Service extracts the authenticated user's ID.
8. User Service allows access only to the corresponding user's profile and addresses.

### Authorization Header

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Security Features

- JWT-based authentication.
- Missing token returns HTTP 401.
- Invalid token returns HTTP 401.
- Authenticated user ID is extracted from the verified token.
- Client-supplied user IDs are not trusted for ownership.
- Users can access only their own profiles.
- Users can manage only their own addresses.
- Access to another user's resources is rejected.
- Inaccessible or non-existent profile/address resources return HTTP 404 where appropriate.

### Important Security Rule

The User Service does not implement another registration or login system.

Authentication and credential management remain the responsibility of the Authentication Service.

---

## 7. User Profile APIs

Base URL:

```text
http://localhost:8012
```

All profile APIs require JWT authentication.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/users/profile | Create profile |
| GET | /api/users/profile | Retrieve profile |
| PUT | /api/users/profile | Update complete profile |
| PATCH | /api/users/profile | Partially update profile |
| DELETE | /api/users/profile | Delete profile |
| PATCH | /api/users/profile/deactivate | Deactivate profile |

### Profile Operations

**Create Profile**

Creates a profile for the authenticated user.

**Get Profile**

Retrieves the authenticated user's profile.

**Update Profile**

Updates the profile information.

**Partially Update Profile**

Updates only the fields supplied in the request.

**Delete Profile**

Deletes the current user's profile according to the configured deletion behaviour.

**Deactivate Profile**

Changes the profile's active status without silently deleting the Authentication Service account.

---

## 8. User Address Management APIs

All address APIs require JWT authentication.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/users/addresses | Add address |
| GET | /api/users/addresses | List all addresses |
| GET | /api/users/addresses/{address_id} | Retrieve specific address |
| PUT | /api/users/addresses/{address_id} | Update complete address |
| PATCH | /api/users/addresses/{address_id} | Partially update address |
| DELETE | /api/users/addresses/{address_id} | Delete address |
| PATCH | /api/users/addresses/{address_id}/default | Set default address |

### Address Management Features

- Add multiple delivery addresses.
- Retrieve all saved addresses.
- Retrieve a specific address.
- Update complete address information.
- Update individual address fields using PATCH.
- Delete saved addresses.
- Set a default delivery address.
- Maintain one default address per customer.
- Prevent access to another customer's addresses.

### Example: Partial Address Update

Request:

```http
PATCH /api/users/addresses/4
```

Request body:

```json
{
    "city": "Chennai"
}
```

Only the supplied city field is updated.

### Example: Set Default Address

```http
PATCH /api/users/addresses/4/default
```

The selected address becomes the default address, and the previous default address loses its default status.

---

## 9. Account Management

The User Management Service supports customer account and profile-related operations.

Features include:

- Retrieve profile information.
- Update customer contact information.
- Update profile information.
- View saved delivery addresses.
- Manage default delivery address.
- Delete saved addresses.
- Deactivate customer profile.

### Account Deactivation Behaviour

When a profile is deactivated:

- The profile's active status becomes false.
- The existing profile record is retained.
- Profile and address operations requiring an active profile are restricted.
- The Authentication Service account is not automatically deleted.
- A duplicate profile cannot be created using the same authentication user ID because of the unique constraint.

Account reactivation, if required, should operate on the existing profile rather than creating a duplicate.

---

## 10. Environment Variables

The application uses environment variables for database connectivity and Authentication Service configuration.

Example `.env.example`:

```env
APP_NAME=ShopEase User Management Service
APP_ENV=development

DB_HOST=user_mysql
DB_PORT=3306
DB_NAME=shopease_user_db
DB_USER=shopease_user
DB_PASSWORD=YOUR_DATABASE_PASSWORD

AUTH_SERVICE_VERIFY_URL=http://host.docker.internal:8011/api/auth/verify-token
AUTH_SERVICE_TIMEOUT_SECONDS=5.0
```

Use your actual local configuration values when creating `.env`.

**Security:**

- Never commit `.env` to GitHub.
- Never publish database passwords.
- Never publish JWT secrets or access tokens.
- Use `.env.example` to document required configuration.

---

## 11. Docker Configuration

The project uses Docker Compose to run the User Management Service and its separate MySQL database.

### Containers

| Container | Purpose |
|---|---|
| user_service | FastAPI application |
| user_mysql | MySQL database |

### Port Configuration

| Service | Host Port | Container Port |
|---|---:|---:|
| User Service | 8012 | 8000 |
| User MySQL | 3311 | 3306 |

### Start Containers

```powershell
docker compose up -d --build
```

### Check Container Status

```powershell
docker compose ps
```

### View User Service Logs

```powershell
docker compose logs user_service
```

### View MySQL Logs

```powershell
docker compose logs user_mysql
```

### Stop Containers

```powershell
docker compose down
```

### Stop Containers and Remove Volumes

```powershell
docker compose down -v
```

**Warning:** The `-v` option deletes the Compose-managed database volumes and their stored data. Do not use it unless you intentionally want to remove the database data.

---

## 12. Alembic Database Migrations

Alembic is used to manage database schema changes.

### Check Current Migration

```powershell
docker compose exec user_service python -m alembic current
```

### Apply Migrations

```powershell
docker compose exec user_service python -m alembic upgrade head
```

### View Migration History

```powershell
docker compose exec user_service python -m alembic history
```

### Generate a New Migration

After modifying SQLAlchemy models:

```powershell
docker compose exec user_service python -m alembic revision --autogenerate -m "describe schema change"
```

### Apply the New Migration

```powershell
docker compose exec user_service python -m alembic upgrade head
```

### Verify Database Tables

```powershell
docker compose exec user_mysql mysql -u shopease_user -p shopease_user_db
```

Inside MySQL:

```sql
SHOW TABLES;

DESCRIBE user_profiles;

DESCRIBE user_addresses;

SELECT * FROM alembic_version;
```

---

## 13. Running the Application

### Start the Application

```powershell
docker compose up -d --build
```

### Apply Database Migrations

```powershell
docker compose exec user_service python -m alembic upgrade head
```

### Check Application Status

```powershell
docker compose ps
```

### Health Check

```http
GET http://localhost:8012/health
```

Expected response:

```json
{
    "status": "healthy",
    "service": "user-management"
}
```

### Swagger API Documentation

Open the following URL in your browser:

```text
http://localhost:8012/docs
```

Swagger UI allows API exploration and testing.

---

## 14. API Testing

The APIs are tested using Swagger UI and can also be tested using Postman.

### Authentication Testing

| Test Scenario | Expected Result |
|---|---|
| Request without JWT | 401 Unauthorized |
| Request with invalid JWT | 401 Unauthorized |
| Request with valid JWT | Authorized |

### Profile Testing

| Test Scenario | Expected Result |
|---|---|
| Create profile | Success |
| Create duplicate profile | Rejected |
| Retrieve own profile | Success |
| Update profile | Success |
| Partially update profile | Success |
| Delete profile | Success |
| Deactivate profile | Success |
| Access another user's profile | Access rejected |

### Address Testing

| Test Scenario | Expected Result |
|---|---|
| Add address | Success |
| List addresses | Success |
| Retrieve address | Success |
| Update address | Success |
| Partially update address | Success |
| Set default address | Success |
| Delete address | Success |
| Access another user's address | Access rejected |
| Maintain only one default address | Verified through database testing |

### Testing Results

The implementation has been tested through Swagger UI and Docker-based API testing.

Record final test evidence and any remaining test results before submission.

---

## 15. Error Handling and Validation

The application uses Pydantic validation and appropriate HTTP status codes.

Common responses:

| HTTP Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 204 | Successful request with no response body, if configured |
| 400 | Invalid request or business rule violation |
| 401 | Missing or invalid authentication |
| 403 | Authenticated but forbidden operation |
| 404 | Resource not found or inaccessible |
| 422 | Request validation error |
| 500 | Internal server error |

The application also handles database transactions and rollbacks through SQLAlchemy session management.

---

## 16. Git and GitHub

### Initialize Git (if not already initialized)

```powershell
git init
```

### Check Repository Status

```powershell
git status
```

### Add Project Files

```powershell
git add .
```

### Commit Changes

```powershell
git commit -m "Complete ShopEase User Management Microservice"
```

### Configure Main Branch

```powershell
git branch -M main
```

### Add GitHub Remote

Replace the URL with your actual GitHub repository URL:

```powershell
git remote add origin YOUR_GITHUB_REPOSITORY_URL
```

If the remote already exists, check it first:

```powershell
git remote -v
```

### Push to GitHub

```powershell
git push -u origin main
```

---

## 17. Security and Best Practices

- Maintain independent Authentication and User Management Services.
- Never store passwords in the User Service.
- Validate JWT tokens before allowing protected operations.
- Identify users using authenticated JWT claims.
- Never trust client-provided user IDs for authorization.
- Prevent cross-user profile and address access.
- Use environment variables for sensitive configuration.
- Maintain database migrations with Alembic.
- Use persistent MySQL storage.
- Handle database errors and transaction rollbacks.
- Keep `.env` and other secrets out of GitHub.

---

## 18. Expected Deliverables

The completed project provides:

- Independent User Management Microservice.
- Separate MySQL database.
- SQLAlchemy models and relationships.
- Alembic migration configuration and scripts.
- JWT authentication integration.
- Customer profile CRUD APIs.
- Customer address CRUD APIs.
- Individual address PATCH functionality.
- Default address management.
- Profile deactivation.
- Dockerfile and Docker Compose configuration.
- Swagger API documentation.
- API testing support.
- README documentation.

---

## 19. Conclusion

The ShopEase User Management Microservice provides a secure and independent backend for managing customer profiles and delivery addresses.

It integrates with the existing Authentication Service through JWT authentication while maintaining its own database and business logic.

The service follows microservices architecture principles, uses FastAPI for REST API development, SQLAlchemy for database operations, Alembic for migrations, Pydantic for validation, and Docker for containerization.

The implementation supports secure customer profile management, address management, ownership validation, default delivery address handling, and account profile deactivation.

**Project: ShopEase – User Management Microservice**

**Backend: FastAPI | Database: MySQL 8 | ORM: SQLAlchemy | Migrations: Alembic | Authentication: JWT | Deployment: Docker**
