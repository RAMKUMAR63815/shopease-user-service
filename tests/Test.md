# ShopEase – User Management Service
## Swagger / Postman API Testing Report

### 1. Testing Environment

| Item | Configuration |
|---|---|
| Service | ShopEase User Management Service |
| Framework | FastAPI |
| Database | MySQL 8 |
| Authentication | JWT |
| Testing Tools | Swagger UI / Postman |
| Base URL | http://localhost:8012 |
| Swagger URL | http://localhost:8012/docs |

### 2. Health Check Testing

| Method | Endpoint | Expected Status | Result |
|---|---|---:|---|
| GET | /health | 200 OK | PASS |

Response:

```json
{
  "status": "healthy",
  "service": "user-management"
}
```

### 3. Authentication Testing

| Test Scenario | Expected Status | Result |
|---|---:|---|
| Access API without JWT | 401 Unauthorized | PASS |
| Access API with invalid JWT | 401 Unauthorized | PASS |
| Access API with valid JWT | Authorized | PASS |

### 4. User Profile API Testing

| Method | Endpoint | Test | Result |
|---|---|---|---|
| POST | /api/users/profile | Create profile | Tested |
| GET | /api/users/profile | Retrieve own profile | Tested |
| PUT | /api/users/profile | Update complete profile | Tested |
| PATCH | /api/users/profile | Partially update profile | Tested |
| DELETE | /api/users/profile | Delete profile | Tested |
| PATCH | /api/users/profile/deactivate | Deactivate profile | Tested |

Additional test scenarios:

- Duplicate profile creation is prevented.
- Deactivated profiles cannot be used for normal active-profile operations.
- Another authenticated user cannot access a profile belonging to a different authentication user.

### 5. User Address API Testing

| Method | Endpoint | Test | Result |
|---|---|---|---|
| POST | /api/users/addresses | Create address | Tested |
| GET | /api/users/addresses | List addresses | Tested |
| GET | /api/users/addresses/{address_id} | Retrieve address | Tested |
| PUT | /api/users/addresses/{address_id} | Update complete address | Tested |
| PATCH | /api/users/addresses/{address_id} | Update individual fields | PASS |
| DELETE | /api/users/addresses/{address_id} | Delete address | Tested |
| PATCH | /api/users/addresses/{address_id}/default | Set default address | PASS |

### 6. Partial Address Update Test

Request:

```http
PATCH /api/users/addresses/4
```

Request Body:

```json
{
  "city": "Chennai"
}
```

Expected Result:

- Only the city field is updated.
- Other address fields remain unchanged.
- The updated address is returned in the response.

### 7. Authorization and Ownership Testing

| Test Scenario | Expected Behaviour | Result |
|---|---|---|
| User A accesses own profile | Allow access | PASS |
| User A accesses User B's profile | Reject access | PASS |
| User A accesses User B's address | Reject access | PASS |
| User A modifies User B's address | Reject modification | Pending confirmation |
| User A deletes User B's address | Reject deletion | Pending confirmation |

Another user's inaccessible profile/address returns 404 Not Found, according to the current service behaviour.

### 8. Default Address Testing

Test scenarios:

1. Create multiple addresses.
2. Mark one address as default.
3. Mark another address as default.
4. Verify the previous default address is no longer default.
5. Confirm that only one default address exists for the customer.

Result: Default address functionality tested successfully. Database verification should be included as evidence.

### 9. Docker and Database Testing

| Test | Result |
|---|---|
| User Service container startup | PASS |
| MySQL container startup | PASS |
| MySQL health check | PASS |
| Database connectivity | PASS |
| Health endpoint | PASS |
| Alembic migration status | PASS |
| Database tables created | PASS |

### 10. Testing Summary

The ShopEase User Management Service has been tested using Swagger UI and Docker-based API testing.

The tests cover:

- JWT authentication.
- Customer profile operations.
- Customer address operations.
- Individual address updates.
- Default address management.
- Profile deactivation.
- User-level access restrictions.
- Docker and database connectivity.

**Note:** Final Postman screenshots, remaining ownership modification/deletion tests, and database verification evidence should be attached before marking all test cases as completed.

### Testing Status

**Project:** ShopEase – User Management Microservice

**Testing Tools:** Swagger UI and Postman

**Status:** Core API functionality tested; final evidence collection and pending scenario confirmation required.
