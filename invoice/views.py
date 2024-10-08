from django.shortcuts import render, redirect
from .models import Invoice
from .forms import InvoiceForm, InvoiceItemFormSet
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.forms import formset_factory
from .models import Invoice, InvoiceItem, Product
from .forms import ProductForm



def create_invoice(request):
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        print(request.POST, '==888888====')
        formset = InvoiceItemFormSet(request.POST)
        # print(formset, '==999999====')
        if invoice_form.is_valid() and formset.is_valid():
            invoice = invoice_form.save()
            items = formset.save(commit=False)
            # print(items, '==777777====')
            for item in items:
                item.invoice = invoice
                item.line_total = item.product.price * item.quantity
                item.save()
                # print(items, '======')
            # Update total cost
            invoice.total_cost = sum(item.line_total for item in invoice.items.all()) + invoice.delivery_cost
            invoice.save()

            # Generate PDF (placeholder)
            return redirect('invoice_list')
    else:
        invoice_form = InvoiceForm()
        formset = InvoiceItemFormSet()
    return render(request, 'create_invoice.html', {'invoice_form': invoice_form, 'formset': formset})



# from django.shortcuts import render, redirect
# from .models import Invoice, InvoiceItem
# from .forms import ItemInvoiceFormSet

# def create_invoice(request):
#     if request.method == 'POST':
#         # Create a new Invoice
#         invoice = Invoice.objects.create(
#             customer_name=request.POST['customer_name'],
#             delivery_cost=request.POST['delivery_cost']
#         )
       
#         formset = ItemInvoiceFormSet(request.POST, queryset=InvoiceItem.objects.none())

#         if formset.is_valid():
#             for form in formset:
#                 # Save each ItemInvoice, linking it to the created invoice
#                 item_invoice = form.save(commit=False)
#                 item_invoice.invoice = invoice
#                 item_invoice.save()
           
#             return redirect('invoice_list')
#     else:
#         formset = ItemInvoiceFormSet(queryset=InvoiceItem.objects.none())
   
#     return render(request, 'create_invoice.html', {'formset': formset})



from django.shortcuts import render
from .models import Invoice
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from datetime import datetime
from django.utils.timezone import localtime

def invoice_list(request):
    # Retrieve date range from request GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Filter invoices based on date range
    if start_date and end_date:
        invoices = Invoice.objects.filter(created_at__date__range=[start_date, end_date])
    else:
        invoices = Invoice.objects.all()
    
    return render(request, 'invoice_list.html', {'invoices': invoices, 'start_date': start_date, 'end_date': end_date})

from django.shortcuts import render
from .models import Invoice
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime
from django.utils.timezone import localtime

def export_invoices_to_excel(request):
    # Retrieve date range from request GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter invoices based on date range
    if start_date and end_date:
        invoices = Invoice.objects.filter(created_at__date__range=[start_date, end_date])
    else:
        invoices = Invoice.objects.all()

    # Create an Excel file
    wb = Workbook()
    ws = wb.active
    ws.title = 'Invoices'

    # Write header
    ws.append(['Invoice ID', 'Customer Name', 'Date', 'Delivery Cost', 'Total Cost'])

    # Write data rows
    for invoice in invoices:
        # Convert datetime to string format suitable for Excel
        created_at_str = localtime(invoice.created_at).strftime('%Y-%m-%d %H:%M:%S')
        ws.append([invoice.id, invoice.customer_name, created_at_str, invoice.delivery_cost, invoice.total_cost])

    # Set response headers
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=invoices.xlsx'
    
    # Save the workbook to the response
    wb.save(response)
    
    return response



# invoices/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Invoice
from weasyprint import HTML
from django.template.loader import render_to_string


def generate_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    html_content = render_to_string('invoice_pdf.html', {'invoice': invoice})
    pdf_file = HTML(string=html_content).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    return response





def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'invoice_detail.html', {'invoice': invoice})



def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to a page listing all products
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})