CREATE DATABASE KeepItGreenDB;

USE KeepItGreenDB

CREATE TABLE Users (
    UserId              INT IDENTITY(1,1) PRIMARY KEY,
    FullName            NVARCHAR(150) NOT NULL,
    Email               NVARCHAR(150) NOT NULL UNIQUE,
    PasswordHash        NVARCHAR(MAX) NOT NULL,
    PointsBalance       INT NOT NULL DEFAULT 0 CHECK (PointsBalance >= 0),
    ProfileImageUrl     NVARCHAR(255) NULL,
    CreatedAt           DATETIME2 NOT NULL DEFAULT SYSDATETIME()
)

CREATE TABLE Machines (
    MachineId       INT IDENTITY(1,1) PRIMARY KEY,
    LocationName    NVARCHAR(150) NOT NULL,
    Latitude        DECIMAL(9,6) NOT NULL,
    Longitude       DECIMAL(9,6) NOT NULL,
    Status          NVARCHAR(20) NOT NULL DEFAULT 'Active',
    CONSTRAINT CK_Machines_Status 
        CHECK (Status IN ('Active', 'Inactive', 'Maintenance'))
)

CREATE TABLE Sessions (
    SessionId           INT IDENTITY(1,1) PRIMARY KEY,
    UserId              INT NOT NULL,
    MachineId           INT NOT NULL,
    StartTime           DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    EndTime             DATETIME2 NULL,
    Status              NVARCHAR(20) NOT NULL DEFAULT 'Active',
    TotalItems          INT NOT NULL DEFAULT 0 CHECK (TotalItems >= 0),
    TotalPointsEarned   INT NOT NULL DEFAULT 0 CHECK (TotalPointsEarned >= 0),

    CONSTRAINT FK_Sessions_Users 
        FOREIGN KEY (UserId) REFERENCES Users(UserId),

    CONSTRAINT FK_Sessions_Machines 
        FOREIGN KEY (MachineId) REFERENCES Machines(MachineId),

    CONSTRAINT CK_Sessions_Status 
        CHECK (Status IN ('Active', 'Completed', 'Failed', 'Abandoned', 'Expired'))
)

CREATE TABLE Transactions (
    TransactionId       INT IDENTITY(1,1) PRIMARY KEY,
    SessionId           INT NOT NULL,
    UserId              INT NOT NULL,
    MachineId           INT NOT NULL,
    ItemType            NVARCHAR(20) NOT NULL,
    PointsEarned        INT NOT NULL CHECK (PointsEarned >= 0),
    ConfidenceScore     DECIMAL(4,3) NOT NULL CHECK (ConfidenceScore BETWEEN 0 AND 1),
    ImagePath           NVARCHAR(255) NULL,
    TimeStamp           DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Transactions_Sessions 
        FOREIGN KEY (SessionId) REFERENCES Sessions(SessionId),

    CONSTRAINT FK_Transactions_Users 
        FOREIGN KEY (UserId) REFERENCES Users(UserId),

    CONSTRAINT FK_Transactions_Machines 
        FOREIGN KEY (MachineId) REFERENCES Machines(MachineId),

    CONSTRAINT CK_Transactions_ItemType 
        CHECK (ItemType IN ('Plastic', 'Aluminum'))
)

CREATE TABLE Vendors (
    VendorId        INT IDENTITY(1,1) PRIMARY KEY,
    VendorName      NVARCHAR(150) NOT NULL,
    Description     NVARCHAR(500) NULL,
    Email           NVARCHAR(150) NOT NULL,
    IsActive        BIT NOT NULL DEFAULT 1
)

CREATE TABLE PromoCodes (
    PromoId             INT IDENTITY(1,1) PRIMARY KEY,
    VendorId            INT NOT NULL,
    Code                NVARCHAR(50) NOT NULL UNIQUE,
    RequiredPoints      INT NOT NULL CHECK (RequiredPoints > 0),
    ExpirationDate      DATETIME2 NOT NULL,
    UsageLimit          INT NOT NULL CHECK (UsageLimit > 0),
    RemainingUsage      INT NOT NULL CHECK (RemainingUsage >= 0),

    CONSTRAINT FK_PromoCodes_Vendors
        FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
)

CREATE TABLE Redemptions (
    RedemptionId        INT IDENTITY(1,1) PRIMARY KEY,
    UserId              INT NOT NULL,
    PromoId             INT NOT NULL,
    RedemptionDate      DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    PointsDeducted      INT NOT NULL CHECK (PointsDeducted > 0),
    Status              NVARCHAR(20) NOT NULL DEFAULT 'Completed',

    CONSTRAINT FK_Redemptions_Users
        FOREIGN KEY (UserId) REFERENCES Users(UserId),

    CONSTRAINT FK_Redemptions_PromoCodes
        FOREIGN KEY (PromoId) REFERENCES PromoCodes(PromoId),

    CONSTRAINT CK_Redemptions_Status
        CHECK (Status IN ('Completed', 'Failed', 'Cancelled'))
)

-- Transactions Indexes
CREATE INDEX IX_Transactions_UserId ON Transactions(UserId)
CREATE INDEX IX_Transactions_MachineId ON Transactions(MachineId)
CREATE INDEX IX_Transactions_TimeStamp ON Transactions(TimeStamp)

-- Sessions Indexes
CREATE INDEX IX_Sessions_UserId ON Sessions(UserId)
CREATE INDEX IX_Sessions_MachineId ON Sessions(MachineId)

-- Redemptions Index
CREATE INDEX IX_Redemptions_UserId ON Redemptions(UserId)

-- PromoCodes Index
CREATE INDEX IX_PromoCodes_VendorId ON PromoCodes(VendorId)

