# Factory Monitoring Dashboard Frontend

A modern React-based dashboard for monitoring industrial machines and equipment, built with PrimeReact and TypeScript.

## Features

- **Real-time Monitoring**: Live data from industrial machines
- **Interactive Charts**: Status trends, customer trends, and hourly reading patterns
- **Advanced Filtering**: Search and filter machines by customer, area, subarea, and status
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Date-based Analysis**: Select specific dates to analyze machine data
- **Status Tracking**: Monitor machine status (Normal, Satisfactory, Alert, Unacceptable)

## Tech Stack

- **React 18** with TypeScript
- **PrimeReact** for UI components
- **Chart.js** for data visualization
- **Axios** for API communication
- **date-fns** for date manipulation
- **Vite** for build tooling

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/          # Main dashboard components
│   │   ├── Charts/            # Chart components
│   │   └── Layout/            # Layout components
│   ├── context/               # React context for state management
│   ├── services/              # API service layer
│   ├── types/                 # TypeScript type definitions
│   ├── constants/             # App constants (colors, etc.)
│   └── App.tsx               # Main app component
├── public/                    # Static assets
└── package.json
```

## API Integration

The frontend connects to the FastAPI backend with the following endpoints:

- `GET /api/machines` - Get all machines
- `GET /api/machines/search` - Search machines with filters
- `GET /api/dashboard/kpis` - Get KPI statistics
- `GET /api/dashboard/trends/status` - Get status trends
- `GET /api/dashboard/trends/hourly` - Get hourly trends

## Features Overview

### Dashboard Layout
- **Header**: Date filter for selecting analysis period
- **KPI Cards**: Total machines and status breakdown
- **Search & Filters**: Advanced filtering capabilities
- **Data Table**: Machine listing with sorting and pagination
- **Charts**: Three interactive charts for data visualization

### Charts
1. **Status Trend Chart**: Stacked bar chart showing machine status distribution over time
2. **Customer Trend Chart**: Stacked bar chart showing machine distribution by customer
3. **Hourly Trend Chart**: Line chart showing reading patterns throughout the day

### Filtering
- Search by machine name or ID
- Filter by customer, area, subarea
- Filter by machine status
- Real-time search results

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

The project uses ESLint for code quality and consistency. Make sure to run `npm run lint` before committing changes.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is part of the Factory Monitoring System.
