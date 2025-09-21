# SSH Tunnel Setup Guide

This guide explains how to use the Factory Monitoring Backend with SSH tunnel for secure MongoDB connection.

## Overview

The backend now supports connecting to MongoDB through an SSH tunnel, which is useful when your MongoDB server is behind a firewall or in a secure environment.

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root with the following configuration:

```env
# Enable SSH tunnel
USE_SSH_TUNNEL=true

# SSH Connection Details
SSH_HOST=43.205.241.141
SSH_PORT=22
SSH_USERNAME=ubuntu
SSH_KEY_PATH=c:\Users\Prash\Desktop\abas\ssh.pem

# MongoDB Connection (on remote server)
REMOTE_MONGODB_HOST=localhost
REMOTE_MONGODB_PORT=27017

# Local tunnel port
LOCAL_MONGODB_PORT=27017

# Database name
DATABASE_NAME=factory_db
```

### 2. SSH Key Setup

Ensure your SSH key file exists and has the correct permissions:
- The key file should be accessible at the path specified in `SSH_KEY_PATH`
- On Windows, the key file should be readable by the application
- The key should be authorized on the remote server for the specified user

## Usage

### Starting the Application with SSH Tunnel

#### Option 1: Using the SSH Tunnel Startup Script
```bash
python scripts/start_with_ssh_tunnel.py
```

#### Option 2: Setting Environment Variable
```bash
# Windows PowerShell
$env:USE_SSH_TUNNEL="true"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Windows Command Prompt
set USE_SSH_TUNNEL=true
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Data Export with SSH Tunnel

#### Export All Data
```bash
python scripts/export_data.py --type all
```

#### Export Only Machines
```bash
python scripts/export_data.py --type machines
```

#### Export Only Sensor Data
```bash
python scripts/export_data.py --type data
```

## How It Works

1. **SSH Tunnel Establishment**: When `USE_SSH_TUNNEL=true`, the application creates an SSH tunnel from your local machine to the remote MongoDB server.

2. **Local Port Forwarding**: The tunnel forwards connections from `localhost:27017` (or your specified local port) to the remote MongoDB server.

3. **MongoDB Connection**: The application connects to MongoDB through the local tunnel endpoint, which appears as a regular local MongoDB connection.

4. **Automatic Cleanup**: When the application shuts down, the SSH tunnel is automatically closed.

## Manual SSH Tunnel (Alternative)

If you prefer to set up the SSH tunnel manually:

```bash
ssh -i c:\Users\Prash\Desktop\abas\ssh.pem -L 27017:localhost:27017 ubuntu@43.205.241.141
```

Then set `USE_SSH_TUNNEL=false` in your `.env` file and use the regular MongoDB URL.

## Troubleshooting

### Common Issues

1. **SSH Key Not Found**
   - Verify the path in `SSH_KEY_PATH` is correct
   - Ensure the file exists and is readable

2. **Connection Refused**
   - Check if the SSH host is accessible
   - Verify SSH port (default: 22)
   - Ensure the SSH key is authorized on the remote server

3. **MongoDB Connection Failed**
   - Verify MongoDB is running on the remote server
   - Check if the remote MongoDB port is correct
   - Ensure no firewall is blocking the connection

4. **Permission Denied**
   - Check SSH key permissions
   - Verify the username has access to the remote server

### Logs

Check the application logs for detailed error messages:
- SSH tunnel establishment status
- MongoDB connection attempts
- Any authentication or network errors

## Security Notes

- The SSH tunnel provides encrypted communication between your local machine and the remote server
- MongoDB credentials should still be properly configured on the remote server
- Consider using SSH key-based authentication instead of passwords
- Regularly rotate SSH keys for enhanced security
