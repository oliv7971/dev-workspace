from fpdf import FPDF

class PDFGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def add_page(self):
        self.pdf.add_page()

    def set_title(self, title):
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.cell(0, 10, title, ln=True, align='C')

    def add_table(self, header, data):
        self.pdf.set_font("Arial", 'B', 12)
        for col in header:
            self.pdf.cell(40, 10, col, border=1)
        self.pdf.ln()

        self.pdf.set_font("Arial", '', 12)
        for row in data:
            for item in row:
                self.pdf.cell(40, 10, str(item), border=1)
            self.pdf.ln()

    def save(self):
        self.pdf.output(self.output_path)

    def generate_report(self, title, header, data):
        self.add_page()
        self.set_title(title)
        self.add_table(header, data)
        self.save()