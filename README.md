# 10-Service AWS Serverless E-Commerce Platform

This is a full-stack, serverless e-commerce web application built entirely on AWS, integrating 10 distinct services. It features a modern React frontend, a serverless backend with AWS Lambda, and an event-driven, asynchronous architecture for order processing.

The application allows users to sign up, log in, browse products, and place orders. Orders are processed asynchronously—the user gets an instant response, and a background workflow handles database updates and sends an email confirmation.

-----

## 🚀 Core Functionalities

  * **Full User Authentication:** Secure sign-up, sign-in, and session management using AWS Cognito.
  * **Dynamic Product Catalog:** Products are fetched live from a DynamoDB NoSQL database.
  * **Secure API:** The API Gateway protects the ordering endpoint, only allowing requests from authenticated (logged-in) users.
  * **Asynchronous Order Processing:** When an order is placed, the API responds *instantly*. The order is put into an SQS queue for reliable, background processing.
  * **Email Notifications:** Users automatically receive an order confirmation email via SES after their order is confirmed.
  * **Health Monitoring:** A CloudWatch Dashboard provides a real-time view of the system's health, API errors, and queue depth.

-----

## 🏗️ Architecture & Services Used

This project uses **10 different AWS services** working together.

### Frontend & User Management

1.  **Amazon S3:** Hosts all the static files (HTML, CSS, JS) for the React frontend.
2.  **Amazon CloudFront:** Serves as the global Content Delivery Network (CDN) to provide a fast, secure (HTTPS) public URL for the website.
3.  **Amazon Cognito:** Handles all user authentication. Manages the sign-up/sign-in UI, user database, and secure token generation.

### Backend API & Logic

4.  **Amazon API Gateway:** Acts as the "front door" for the backend. It provides the public REST API endpoints (like `GET /products`) and connects them to Lambda.
5.  **AWS Lambda:** Provides all the serverless compute (backend logic). We used four functions:
      * `listProducts`: Fetches all products from DynamoDB.
      * `getProduct`: Fetches a single product (used for testing).
      * `createOrder`: Validates the user and places a "PENDING" order into DynamoDB and SQS.
      * `processOrder`: A background worker that confirms the order and sends the email.
6.  **AWS IAM (Identity & Access Management):** Secures the entire application by providing "Least Privilege" roles for every Lambda function, ensuring they can *only* access the resources they need.

### Database

7.  **Amazon DynamoDB:** The high-performance NoSQL database. We used two tables:
      * `Products`: Stores the product catalog.
      * `Orders`: Stores all customer order information.

### Asynchronous Processing & Notification

8.  **Amazon SQS (Simple Queue Service):** The message queue. This decouples the API from the heavy processing. The `createOrder` API just sends a message here, allowing for an instant user response.
9.  **Amazon SES (Simple Email Service):** The email delivery service. The `processOrder` function uses SES to send the final order confirmation email.

### Monitoring

10. **Amazon CloudWatch:** The monitoring and logging hub. It automatically collects logs from all Lambda functions and API Gateway. We used it to debug our app and built a dashboard to monitor its health.

-----

## 🔄 End-to-End Workflow (How an Order Works)

1.  A user visits the **CloudFront** URL, which serves the React app from **S3**.
2.  The user signs in using **Cognito**.
3.  The React app calls **API Gateway** (`GET /products`), which triggers the `listProducts` **Lambda** to fetch data from **DynamoDB**.
4.  The user clicks "Buy Now." The app sends the user's **Cognito** token to the secure `POST /orders` endpoint on **API Gateway**.
5.  **API Gateway** triggers the `createOrder` **Lambda**.
6.  The `createOrder` Lambda:
    a. Creates a new order in **DynamoDB** with a status of `PENDING`.
    b. Sends a message with the order details to the **SQS** queue.
    c. Returns an *immediate* "Order received\!" success message to the user.
7.  The **SQS** queue *automatically* triggers the `processOrder` **Lambda**.
8.  The `processOrder` Lambda:
    a. Reads the message.
    b. Updates the order in **DynamoDB** from `PENDING` to `CONFIRMED`.
    c. Uses **SES** to send a confirmation email to the user.
9.  This entire flow is monitored by **CloudWatch** and secured by **IAM**.

-----

## 🛠️ How to Run This Project Locally (Frontend)

This repository contains the code for the React frontend and the Python scripts for the Lambda functions.

### Prerequisites

  * [Node.js](https://nodejs.org/en) (v18+)
  * An AWS Account (to set up the backend)
  * [AWS CLI](https://aws.amazon.com/cli/) (optional, but recommended)

### Local Frontend Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name/my-ecommerce-app
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

3.  **Create your environment file:**
    Create a file in the `my-ecommerce-app` root named `.env`. This file holds all your AWS keys. **This file is in the .gitignore and will not be pushed to GitHub.**

    Paste the following into `.env` and fill it with the values from your AWS console:

    ```.env
    VITE_AWS_REGION=eu-north-1
    VITE_COGNITO_USER_POOL_ID=eu-north-1_xxxxxxxxx
    VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxx
    VITE_API_GATEWAY_URL=https://xxxxxxxxx.execute-api.eu-north-1.amazonaws.com/prod
    ```

4.  **Run the app:**

    ```bash
    npm run dev
    ```

    Open `http://localhost:5173` (or similar) in your browser.

### Backend Setup

The backend for this project was configured manually in the AWS Management Console. The Python code for all Lambda functions is provided in the `/lambda-functions` folder.

To build this yourself, you would need to:

1.  Create the S3 buckets, DynamoDB tables, Cognito User Pool, SQS Queue, and SES identity.
2.  Create the Lambda functions and paste the provided code.
3.  Manually configure the Environment Variables for the Lambdas (e.g., `QUEUE_URL`, `TABLE_NAME`).
4.  Create the API Gateway and manually link the endpoints to their respective Lambdas.
5.  Set the SQS queue as a trigger for the `processOrder` Lambda.
6.  Create a CloudFront distribution pointing to the S3 frontend bucket.