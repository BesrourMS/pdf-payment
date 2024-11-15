from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger
import stripe
import os
import uuid

# Initialize FastAPI app
app = FastAPI()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Stripe configuration
stripe.api_key = "your_stripe_secret_key"
PAYMENT_AMOUNT_CENTS = 500  # Example cost in cents ($5.00)
CURRENCY = "usd"

# Configure logger
logger.add("app.log", rotation="500 MB")  # Rotate logs after they reach 500 MB

# PDF generation function
def generate_business_pdf(data: dict, output_filename: str):
    c = canvas.Canvas(output_filename, pagesize=A4)
    width, height = A4

    # Basic PDF content setup
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Business Information")
    c.setFont("Helvetica", 12)
    
    # Add details to PDF
    y_position = height - 150
    for label, value in data.items():
        c.drawString(100, y_position, f"{label}: {value}")
        y_position -= 20

    c.showPage()
    c.save()

# Create payment intent with rate limiting and logging
@app.post("/create-payment-intent/")
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute per user
async def create_payment_intent(request: Request):
    try:
        # Log request initiation
        logger.info("Creating payment intent...")

        # Create a payment intent for the charge
        payment_intent = stripe.PaymentIntent.create(
            amount=PAYMENT_AMOUNT_CENTS,
            currency=CURRENCY,
        )

        # Log successful creation of payment intent
        logger.info(f"Payment intent created: {payment_intent.id}")
        return JSONResponse(content={"client_secret": payment_intent.client_secret})
    except Exception as e:
        # Log the error
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Generate PDF after payment confirmation, with error handling and logging
@app.post("/generate-pdf/")
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute per user
async def generate_pdf(company_data: dict, payment_intent_id: str, request: Request):
    try:
        # Log request initiation
        logger.info("Generating PDF...")

        # Confirm that the payment intent is successful
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if payment_intent.status != "succeeded":
            logger.warning(f"Payment not successful for intent {payment_intent_id}")
            raise HTTPException(status_code=402, detail="Payment required")

        # Generate unique filename for the PDF
        filename = f"{uuid.uuid4()}_Business_Info.pdf"
        
        # Generate PDF with provided data
        generate_business_pdf(company_data, filename)
        
        # Check if PDF was created successfully
        if not os.path.exists(filename):
            logger.error("Failed to generate PDF")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")

        # Log successful PDF generation
        logger.info(f"PDF generated successfully: {filename}")
        return FileResponse(filename, media_type="application/pdf", filename=filename)
    except Exception as e:
        # Log the error
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")