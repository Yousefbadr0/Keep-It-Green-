# Recycle System API

A RESTful Web API built with ASP.NET Core for managing recycling operations, user transactions, OTP verification, rewards, and machine interactions.

## Features

- User Registration and Login
- JWT Authentication
- Role-Based Authorization (Admin & User)
- OTP Generation & Verification
- Recycling Transactions Management
- Machine Management
- Reward Points System
- Admin Dashboard Operations
- Entity Framework Core Integration
- SQL Server Database
- Swagger API Documentation

## Technologies Used

- ASP.NET Core Web API
- Entity Framework Core
- SQL Server
- ASP.NET Core Identity
- JWT Authentication
- Swagger / OpenAPI
- LINQ
- Dependency Injection

## Authentication & Authorization

The API uses JWT Bearer Tokens for secure authentication.

### Roles
- Admin
- User

Example:

```csharp
[Authorize(Roles = "Admin")]
```

## OTP Verification

- Generate OTP Codes
- Verify OTP Before Completing Transactions
- Prevent Reuse of OTP Codes
- OTP Expiration Validation

## Main Modules

### Authentication
- Register
- Login
- JWT Token Generation

### Machines
- Add Machine
- Update Machine
- Delete Machine
- View Machines

### Transactions
- Create Recycling Transactions
- Validate OTP
- Store Transaction History

### Rewards
- Earn Points From Recycling
- Track User Rewards

### Admin Operations
- Manage Users
- Manage Machines
- Monitor Transactions

## Database

The project uses SQL Server with Entity Framework Core (Code First).

### Migration

```bash
Add-Migration InitialCreate
Update-Database
```

## API Documentation

Swagger is enabled for testing API endpoints.

```text
https://localhost:{port}/swagger
```

## Getting Started

```bash
git clone <repository-url>
dotnet restore
Update-Database
dotnet run
```

## Future Enhancements

- Analytics Dashboard
- Mobile Application Integration
- Notifications System
- Reports & Statistics

## Author

Shahd Younis
Backend .NET Developer
