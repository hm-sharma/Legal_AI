import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_sample_contracts(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Master Services Agreement
    msa_path = os.path.join(output_dir, "Master_Services_Agreement_Draft.pdf")
    if not os.path.exists(msa_path):
        doc = SimpleDocTemplate(msa_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1E293B'), alignment=1)
        h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=8)

        story = []
        story.append(Paragraph("MASTER SERVICES AGREEMENT", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("This Master Services Agreement ('Agreement') is entered into between Client Enterprise Corp ('Client') and Vendor Solutions LLC ('Service Provider').", body_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=12))

        story.append(Paragraph("1. Services and Delivery Timelines", h2_style))
        story.append(Paragraph("Service Provider shall deliver all custom software modules and consulting services promptly and shall use best efforts to meet any delivery dates requested by Client, regardless of whether such delivery dates are mutually agreed upon in writing.", body_style))

        story.append(Paragraph("2. Fees, Invoicing and Payment Terms", h2_style))
        story.append(Paragraph("Client shall pay undisputed invoices within ninety (90) days following receipt of invoice. Client may withhold payment of any invoice, in whole or in part, if Client subjectively determines that services rendered do not meet Client's satisfaction.", body_style))

        story.append(Paragraph("3. Indemnification & Liability", h2_style))
        story.append(Paragraph("Service Provider shall indemnify, defend, and hold harmless Client, its affiliates, directors, officers, and employees from any and all damages, claims, losses, liabilities, costs, and expenses (including attorney fees) arising out of or related to performance under this Agreement.", body_style))
        story.append(Paragraph("Service Provider's indemnity obligations hereunder shall be unbounded, uncapped, and shall survive termination of this Agreement perpetually.", body_style))

        story.append(Paragraph("4. Limitation of Liability", h2_style))
        story.append(Paragraph("IN NO EVENT SHALL CLIENT BE LIABLE TO SERVICE PROVIDER FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, OR SPECIAL DAMAGES. CLIENT'S TOTAL AGGREGATE LIABILITY UNDER THIS AGREEMENT SHALL BE LIMITED TO $500. SERVICE PROVIDER AGREES THAT NO LIABILITY CAP SHALL APPLY TO SERVICE PROVIDER'S OBLIGATIONS.", body_style))

        story.append(Paragraph("5. Intellectual Property Rights", h2_style))
        story.append(Paragraph("Service Provider hereby irrevocably assigns to Client all right, title, and interest in and to all work product, tools, frameworks, and methodologies utilized or developed during the provision of services, including pre-existing background IP owned by Service Provider prior to the effective date.", body_style))

        story.append(Paragraph("6. Restrictive Covenants & Non-Compete", h2_style))
        story.append(Paragraph("During the term and for a period of five (5) years thereafter, Service Provider shall not directly or indirectly provide software development services to any entity in the technology sector worldwide.", body_style))

        doc.build(story)

    # 2. Non-Disclosure Agreement (NDA)
    nda_path = os.path.join(output_dir, "Mutual_NDA_Agreement.pdf")
    if not os.path.exists(nda_path):
        doc = SimpleDocTemplate(nda_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1E293B'), alignment=1)
        h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=8)

        story = []
        story.append(Paragraph("NON-DISCLOSURE AGREEMENT", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("This Non-Disclosure Agreement ('Agreement') is made effective as of the date of signing, by and between Disclosing Party and Receiving Party.", body_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=12))

        story.append(Paragraph("1. Definition of Confidential Information", h2_style))
        story.append(Paragraph("Confidential Information includes all proprietary software, trade secrets, customer lists, financial data, and operational plans disclosed by Disclosing Party, whether orally, visually, or in writing.", body_style))

        story.append(Paragraph("2. Obligations of Receiving Party", h2_style))
        story.append(Paragraph("Receiving Party shall hold Confidential Information in absolute strict confidence and shall not disclose such information to any third party without prior written authorization.", body_style))

        story.append(Paragraph("3. Term & Perpetual Confidentiality", h2_style))
        story.append(Paragraph("The confidentiality obligations under Section 2 shall continue in perpetuity for all trade secrets and technical specifications disclosed hereunder.", body_style))

        doc.build(story)

    # 3. Residential / Commercial Lease Agreement
    lease_path = os.path.join(output_dir, "Residential_Lease_Agreement_Draft.pdf")
    if not os.path.exists(lease_path):
        doc = SimpleDocTemplate(lease_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1E293B'), alignment=1)
        h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=8)

        story = []
        story.append(Paragraph("RESIDENTIAL LEASE AGREEMENT", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("This Lease Agreement ('Agreement') is made between Apex Realty Management LLC ('Landlord / Owner') and Resident Tenant ('Tenant').", body_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=12))

        story.append(Paragraph("1. Rent Payment & Security Deposit Forfeiture", h2_style))
        story.append(Paragraph("Tenant shall pay monthly rent in advance on the 1st of each month. Tenant agrees that Landlord may retain the entire security deposit as non-refundable liquidated damages upon any technical default, without providing itemized repair accounting.", body_style))

        story.append(Paragraph("2. Property Maintenance & Structural Repairs", h2_style))
        story.append(Paragraph("Tenant agrees to be solely responsible for all routine and structural repairs, HVAC maintenance, plumbing fixes, and roof repairs, regardless of pre-existing property conditions or structural wear.", body_style))

        story.append(Paragraph("3. Unilateral Entry & Immediate Eviction Rights", h2_style))
        story.append(Paragraph("Landlord reserves the right to enter the premises at any time without prior written notice to Tenant. Landlord may terminate this lease upon twenty-four (24) hours notice for convenience without cause.", body_style))

        doc.build(story)

    return {
        "msa": msa_path,
        "nda": nda_path,
        "lease": lease_path
    }
