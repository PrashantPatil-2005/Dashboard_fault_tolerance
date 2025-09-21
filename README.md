
# Factory Monitoring Backend

A comprehensive industrial data monitoring system built with FastAPI and MongoDB. This backend provides REST API endpoints for accessing machine sensor data, bearings information, and dashboard analytics.

## Architecture

```

/factory\_monitoring\_backend
├── /app
│   ├── **init**.py
│   ├── main.py           # FastAPI application with all API routes
│   ├── models.py         # Pydantic models for data validation
│   ├── database.py       # MongoDB connection and query logic
│   └── config.py         # Configuration management
├── /scripts
│   ├── **init**.py
│   └── ingest\_data.py    # Data ingestion script
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md

````

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
````

### 2. Run the Application

#### Development Mode

```bash
python run.py dev
```

#### Production Mode with Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### Machine Endpoints

* `GET /api/machines` - Get all machines
* `GET /api/machines/{machine_id}` - Get machine by ID
* `GET /api/machines/search` - Search machines with filters
* `GET /api/machines/{machine_id}/latest-readings` - Get latest readings for machine
* `GET /api/machines/{machine_id}/timeseries` - Get time series data

### Bearing Endpoints

* `GET /api/bearings?machine_id={machine_id}` - Get bearings for a machine

### Data Endpoints

* `GET /api/data/query` - Query sensor data with filters
* `GET /api/readings/{reading_id}/fft` - Get FFT data for a reading

### Dashboard Endpoints

* `GET /api/dashboard/kpis` - Get KPI statistics
* `GET /api/dashboard/trends/hourly` - Get hourly trends
* `GET /api/dashboard/trends/status` - Get status trends

### Utility Endpoints

* `GET /health` - Health check
* `GET /api/stats` - System statistics

## Data Ingestion

### Manual Ingestion

Run the ingestion script manually:

```bash
# Ingest data for today
python scripts/ingest_data.py

# Ingest data for a specific date
python scripts/ingest_data.py --date 2025-09-17

# Backfill data for the last 7 days
python scripts/ingest_data.py --backfill-days 7

# Run with debug logging
python scripts/ingest_data.py --log-level DEBUG
```

### Automated Ingestion (Cron Job)

Set up a daily cron job to run the ingestion script:

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM
0 2 * * * /usr/bin/python3 /path/to/factory_monitoring_backend/scripts/ingest_data.py >> /var/log/ingestion_cron.log 2>&1
```

## Security Considerations

### MongoDB Security

**Important**: When deploying to production, ensure MongoDB access is restricted using firewall rules:

1. **AWS Security Groups**: Configure security groups to allow connections only from the application server
2. **MongoDB bindIp**: If using external access (e.g., `bindIp: 127.0.0.1,203.0.113.25`), ensure proper firewall configuration
3. **Authentication**: Enable MongoDB authentication in production
4. **SSL/TLS**: Use encrypted connections for production deployments

### API Security

* Configure CORS appropriately for your frontend domain
* Implement authentication/authorization as needed
* Use HTTPS in production
* Rate limiting for API endpoints

## Monitoring and Logging

### Application Logs

* Main application logs: `app.log`
* Ingestion logs: `ingestion.log`
* Cron job logs: `/var/log/ingestion_cron.log`

### Health Monitoring

* Health check endpoint: `GET /health`
* System stats endpoint: `GET /api/stats`

## Development

### Running in Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
python run.py dev

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once the server is running, access the interactive API documentation:

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With configuration file
gunicorn app.main:app -c gunicorn.conf.py
```

### Example Gunicorn Configuration (gunicorn.conf.py)

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

## Data Models

### Machine

* `machine_name`: Name of the machine
* `customer`: Customer name
* `area`: Area location
* `subarea`: Subarea location
* `machine_type`: Type of machine
* `status`: Current status (Normal, Satisfactory, Alert, Unacceptable)

### Bearing

* `machine_id`: Reference to machine
* `bearing_location`: Location of the bearing
* `bearing_type`: Type of bearing
* `position`: Position information

### Reading

* `machine_id`: Reference to machine
* `bearing_id`: Reference to bearing
* `timestamp`: Reading timestamp
* `status`: Reading status
* `acceleration`: Acceleration data (RMS, peak, crest factor, kurtosis)
* `velocity`: Velocity data (RMS, peak, crest factor)
* `temperature`: Temperature reading
* `fft_data`: FFT analysis data

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**

   * Check MongoDB is running: `sudo systemctl status mongod`
   * Verify connection string in `.env`
   * Check firewall settings

2. **External API Timeouts**

   * Check network connectivity
   * Verify API endpoints are accessible
   * Review ingestion logs for specific errors

3. **High Memory Usage**

   * Limit query results using pagination
   * Monitor MongoDB memory usage
   * Consider indexing frequently queried fields

### Performance Optimization

1. **Database Indexing**

   ```javascript
   // MongoDB indexes for better performance
   db.machines.createIndex({"customer": 1})
   db.machines.createIndex({"area": 1, "subarea": 1})
   db.bearings.createIndex({"machineId": 1})
   db.data.createIndex({"machineId": 1, "timestamp": -1})
   db.data.createIndex({"bearingId": 1, "timestamp": -1})
   ```

2. **API Response Caching**

   * Implement Redis caching for frequently accessed data
   * Cache dashboard statistics

3. **Database Connection Pooling**

   * Configure appropriate connection pool size
   * Monitor connection usage

## Support

For issues and questions:

1. Check the logs for error details
2. Verify configuration settings
3. Test database connectivity
4. Review API documentation at `/docs`

