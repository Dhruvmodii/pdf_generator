import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

def generate_pdf(name, products, grand_total):
    """Generates a PDF invoice with the given name and product details."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Write the customer's name
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.ln(5)
    
    # Table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, "Product Name", 1)
    pdf.cell(50, 10, "Weight", 1)
    pdf.cell(40, 10, "Price", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()
    
    # Table rows for each product
    pdf.set_font("Arial", size=12)
    for product in products:
        product_name = product.get("name", "")
        weight = product.get("weight", "")
        price = product.get("price", 0.0)
        
        pdf.cell(50, 10, product_name, 1)
        pdf.cell(50, 10, weight, 1)
        pdf.cell(40, 10, f"{price:.2f}", 1)
        pdf.cell(40, 10, f"{price:.2f}", 1)  # Here, price is used as the row total.
        pdf.ln()
    
    # Grand total row
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "Grand Total", 1)
    pdf.cell(40, 10, f"{grand_total:.2f}", 1)
    pdf.ln()
    
    # Save the PDF into an in-memory bytes buffer
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    return pdf_buffer.getvalue()

# Initialize session state for storing product entries.
if 'products' not in st.session_state:
    st.session_state.products = []

def add_product():
    """Adds a product from the form inputs to the session state list."""
    product_name = st.session_state.get("product_name_input", "").strip()
    weight = st.session_state.get("weight_input", "").strip()
    price_str = st.session_state.get("price_input", "").strip()
    
    if not product_name:
        st.error("Please enter a product name.")
        return
    if not weight:
        st.error("Please enter a weight.")
        return
    if not price_str:
        st.error("Please enter a price.")
        return
    
    try:
        price = float(price_str)
    except ValueError:
        st.error("Please enter a valid number for price.")
        return
    
    product = {
        "name": product_name,
        "weight": weight,
        "price": price,
    }
    st.session_state.products.append(product)
    st.success(f"Added product: {product_name}")

# App header and customer name input
st.title("Product Invoice Generator")
name = st.text_input("Enter your name:")

st.markdown("### Add Product Details")
# Form to add new product details; clear_on_submit resets the widget values automatically.
with st.form(key="product_form", clear_on_submit=True):
    st.text_input("Product Name", key="product_name_input")
    st.text_input("Weight (e.g., '2 kg 300 g' or '2.3 kg')", key="weight_input")
    # Use text_input for price so there is no default value prefilled.
    st.text_input("Price", key="price_input")
    
    submitted = st.form_submit_button("Add Product")
    if submitted:
        add_product()

# Display the list of added products (if any)
if st.session_state.products:
    st.markdown("### Products Added")
    df = pd.DataFrame(st.session_state.products)
    st.table(df)

# Generate the PDF when the button is clicked
if st.button("Generate PDF"):
    if not name.strip():
        st.error("Please enter your name.")
    elif not st.session_state.products:
        st.error("Please add at least one product.")
    else:
        # Compute the grand total by summing the product prices.
        grand_total = sum(product.get("price", 0) for product in st.session_state.products)
        pdf_data = generate_pdf(name, st.session_state.products, grand_total)
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name="invoice.pdf",
            mime="application/pdf"
        )
