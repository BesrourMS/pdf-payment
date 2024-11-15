# FastAPI PDF Generation and Payment Integration

This is a backend application built with FastAPI that allows users to generate PDF documents with business information and process payments through Stripe. The project includes features such as rate limiting, error handling, logging, and integrates a simple pay-per-use model.

## Features

- **Generate PDFs**: Create elegant PDF files for company information such as business name, trade register, capital, headquarters, and more.
- **Stripe Payment Integration**: Secure payment processing via Stripe with payment intent creation and confirmation.
- **Rate Limiting**: Prevent abuse with rate limiting (10 requests per minute per user) using `slowapi`.
- **Logging**: All important actions and errors are logged using `loguru` for monitoring and debugging.
- **Error Handling**: Proper error responses and logging for any failure in payment or PDF generation processes.

## Prerequisites

To run this project, you will need the following:

- **Python 3.7+**
- **FastAPI**: A modern web framework for building APIs.
- **Stripe Account**: To handle payments and create payment intents.
- **Required Python Libraries**: Install all dependencies listed below.

## Installation

### Clone the repository

```bash
git clone https://github.com/BesrourMS/pdf-payment.git
cd pdf-generation-payment-fastapi
```

### Install dependencies

Create a virtual environment (optional but recommended) and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

Or simply install the required libraries directly:

```bash
pip install fastapi stripe reportlab slowapi loguru
```

### Stripe Configuration

Make sure to set your Stripe API key in the following section of the `main.py`:

```python
stripe.api_key = "your_stripe_secret_key"
```

You can obtain your Stripe secret key by logging into your [Stripe Dashboard](https://dashboard.stripe.com) and copying the key from the "API Keys" section.

## Running the Application

Once the dependencies are installed and your Stripe key is configured, you can run the FastAPI app using the `uvicorn` ASGI server:

```bash
uvicorn main:app --reload
```

The app will be available at `http://127.0.0.1:8000`. You can access the endpoints:

- `/create-payment-intent/`: Creates a payment intent via Stripe.
- `/generate-pdf/`: Generates a PDF with business information after successful payment.

## API Endpoints

### 1. **Create Payment Intent**

- **URL**: `/create-payment-intent/`
- **Method**: `POST`
- **Response**: JSON object containing the client secret needed for frontend Stripe integration.

#### Request Body
No body is required.

#### Example Response
```json
{
    "client_secret": "pi_1GqHrt2eZvKYlo2CwY9lmc1g_secret_JbP5gC3sIVhrTAtPQxqdfHfKvF"
}
```

### 2. **Generate PDF**

- **URL**: `/generate-pdf/`
- **Method**: `POST`
- **Request Body**: JSON object containing business details like name, trade register, capital, etc.

#### Example Request Body:
```json
{
    "Business Name": "ConvertY for Ecommerce",
    "Denomination": "convertY for ecommerce",
    "Capital": "50000 TND",
    "Start Date": "Tuesday, January 2, 2024",
    "Type": "Limited Liability Company (LLC)",
    "Headquarters": "Mnihla 2094"
}
```

#### Front End Implementation
```html
<!-- Add Stripe.js -->
<script src="https://js.stripe.com/v3/"></script>
<script>
    async function createPaymentIntent() {
        const response = await fetch("/create-payment-intent/", { method: "POST" });
        const { client_secret } = await response.json();

        const stripe = Stripe("your_stripe_publishable_key");
        const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
            payment_method: {
                card: stripe.elements().create("card"),
            }
        });

        if (error) {
            console.error("Payment failed:", error);
            alert("Payment failed. Please try again.");
        } else if (paymentIntent.status === "succeeded") {
            console.log("Payment succeeded");

            // After successful payment, generate the PDF
            const companyData = {
                "Unique Identifier": "1849721Z",
                "Trade Register": "C038862024",
                "Business Name": "Converty for Ecommerce",
                "Denomination": "Converty for Ecommerce",
                "Capital": "50000 TND",
                "Start Date": "Tuesday, January 2, 2024",
                "Type": "Limited Liability Company (LLC)",
                "Headquarters": "Mnihla 2094",
            };

            // Generate PDF after payment
            const pdfResponse = await fetch("/generate-pdf/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    company_data: companyData,
                    payment_intent_id: paymentIntent.id
                }),
            });

            // Handle the PDF response (could open as a new window or trigger download)
            if (pdfResponse.ok) {
                const blob = await pdfResponse.blob();
                const url = window.URL.createObjectURL(blob);
                window.open(url);
            } else {
                alert("Failed to generate PDF");
            }
        }
    }
</script>
```

#### Example Response
A PDF file will be returned if the payment is successful.

## Rate Limiting

The API uses `slowapi` to limit users to 10 requests per minute per endpoint. This helps prevent abuse and ensures fair use of the service.

## Logging

All important actions (e.g., payment creation, PDF generation) and errors are logged to a file `app.log`. You can view logs for debugging and monitoring purposes.

## Error Handling

The application provides detailed error responses if anything goes wrong. Errors are also logged for troubleshooting. Common errors include:

- **402 Payment Required**: The payment has not been completed successfully.
- **500 Internal Server Error**: Unexpected server issues during processing.

## License

This project is licensed under the MIT License.

---

Feel free to contribute to this project or use it for your own purposes. If you have any questions or suggestions, feel free to open an issue or contact me.