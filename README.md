# Genesis Server - Synthetic Data Generator

A FastAPI-based server for automatically generating synthetic data through Generative AI models
and function-based generation. This server serves as the core component of a larger synthetic data generation
architecture, providing RESTful endpoints for training models, running inference, and generating data from scratch.

## Features

- **Model Training**: Train synthetic data generation models from datasets
- **Inference**: Generate synthetic data using pre-trained models
- **Function-based Generation**: Create synthetic data using custom functions and features
- **CouchDB Integration**: Persistent storage for job status and results
- **Garage Storage**: Object storage for model artifacts

## Architecture

The Genesis Server is built with:
- **GENESIS Core Lib**: Core library for synthetic data generation
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.12+**: Latest Python features and performance
- **CouchDB**: Document database for job tracking and results storage
- **Garage/MinIO**: S3-compatible object storage for model management

## Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Docker Installation from Git

1. **Clone the repository**:
   ```bash
   git clone https://github.com/eng-genesis/genesis_server.git
   cd genesis_server
   ```

2. **Build and run with Docker**:
   ```bash
   # Build the Docker image
   docker build -t genesis-server ./src
   
   # Run the container
   docker run -p 8010:8010 genesis-server
   ```


The server will be available at `http://localhost:8010`

### Local Development Setup

1. **Install dependencies with UV**:
   ```bash
   cd src
   uv sync --project pyproject.toml
   ```

2. **Run the server**:
   ```bash
   uv run fastapi run server/app.py --port 8010
   ```

## APIary (API Documentation)

The Genesis Server exposes a comprehensive REST API with the following endpoints:

### Base URL
```
http://localhost:8010
```

### Interactive Documentation
- **Swagger UI**: `http://localhost:8010/docs`


### Core Endpoints

#### 1. Train Model
```http
POST /train
```

Starts a new training process for synthetic data generation.

**Request Body**:
```json
{
  "model": {
    "algorithm_name": "string",
    "model_name": "string"
  },
  "dataset": [
    {
      "column_name": "string",
      "column_datatype": "float32|int32|str|bool",
      "column_type": "continuous|categorical|primary_key|group_index",
      "column_data": [...]
    }
  ],
  "functions": [
    {
      "feature": "string",
      "function_reference": "string",
      "parameters": [
        {
          "name": "string",
          "value": "string",
          "parameter_type": "string"
        }
      ]
    }
  ],
  "n_rows": 1000
}
```

**Response**: Returns a `doc_id` for tracking the training job status.

#### 2. Inference
```http
POST /infer
```

Generates synthetic data using a pre-trained model.

**Request Body**:
```json
{
  "model": {
    "algorithm_name": "string",
    "model_name": "string",
    "image": "string",
    "input_shape": "(3,4)",
    "training_data_info": [
       {
           "feature_name": "feature_name",
           "feature_position": 0,
           "feature_type": "continuous|categorical|primary_key|group_index",
           "type": "float64",
           "is_categorical": false,
           "feature_size": "1"
       }
  ]},
  "functions": [
    {
    "feature": "feature_name",           
    "function_name": "function.name.FunctionName",      
    "parameters": [
      {
        "name": "parameter_name",
        "value": "parameter_value",
        "parameter_type": "string"|"int64"|"float64"
      }
    ]
}
  ],
  "n_rows": 1000,
  "dataset": [...] // Optional
}
```

**Response**: Returns a `doc_id` for tracking the inference job.

#### 3. Function-based Generation
```http
POST /generate
```

Generates synthetic data using custom functions without requiring a trained model.

**Request Body**:
```json
{
  "functions": [
    {
      "feature": "string",
      "function_reference": "string",
      "parameters": {
        "name": "parameter_name",
        "value": "parameter_value",
        "parameter_type": "string"|"int64"|"float64"
      }
    }
  ],
  "n_rows": 1000
}
```

**Response**: Returns a `doc_id` for tracking the generation job.

### Data Types

The API supports the following data types:

#### Supported Data Types
- `float32`: Floating-point numbers
- `int32`: Integer numbers
- `str`: String values
- `bool`: Boolean values

#### Supported Feature Types
- `continuous`: Continuous numerical features
- `categorical`: Categorical features
- `primary_key`: Primary key columns
- `group_index`: Grouping/index columns

### Job Tracking

All operations return a `doc_id` that can be used to track job progress and retrieve results from CouchDB. The job status is updated in real-time as the processing continues.

### Error Handling

The API provides comprehensive error responses:
- `400`: Bad Request - Invalid input parameters
- `500`: Internal Server Error - Processing failures

## Configuration

The server requires configuration for:
- CouchDB connection settings
- MinIO/Garage storage credentials
- Model registry endpoints
- Logging configuration

Environment variables and configuration files should be set up according to your deployment environment.

## Development

### Running Tests
```bash
cd src
uv run pytest
```

### Code Quality
```bash
# Linting
uv run ruff check

# Formatting
uv run ruff format
```

## License

This project is licensed under the AGPL 3.0 open source license.

## Contributing

Please refer to the project's contribution guidelines for development practices and pull request processes.