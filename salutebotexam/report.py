"""PDF report of a user's available slots (fpdf2).

Given the slot rows produced by ``Store.slots_for_user`` (which carry the
prestazione description and the is_new flag), build a printable PDF grouped by
prestazione, with newly-appeared slots marked.
"""

import os
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from config import REPORT_DIR


class SlotReport:
    """Builds a PDF slot report for one user. Fields are private (encapsulation)."""

    def __init__(self, cf: str, rows: list[dict]) -> None:
        """Build the report object.

        Args:
            cf: the user's codice fiscale.
            rows: slot dicts from Store.slots_for_user (with code, descrizione,
                date, time, struttura, cap, address, is_new).
        """
        self.__cf = cf
        self.__rows = rows

    def build(self, out_path: str | None = None) -> str:
        """Render the PDF to disk and return its path.

        Args:
            out_path: where to write the PDF; None writes a timestamped file into
                config.REPORT_DIR.
        Returns:
            The path of the written PDF file.
        """
        os.makedirs(REPORT_DIR, exist_ok=True)
        if out_path is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = os.path.join(REPORT_DIR, f"report_{self.__cf}_{stamp}.pdf")

        pdf = FPDF()
        pdf.add_page()
        self.__header(pdf)
        if not self.__rows:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 8, "Nessun posto disponibile per le prestazioni seguite.",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            self.__body(pdf)
        pdf.output(out_path)
        return out_path

    def __header(self, pdf: FPDF) -> None:
        """Write the title and the user/date lines."""
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "salute-bot - Report posti disponibili",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Utente (CF): {self.__cf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)

    def __body(self, pdf: FPDF) -> None:
        """Write the slots, grouped by prestazione, newly-appeared ones marked."""
        current_code = None
        for row in self.__rows:
            if row["code"] != current_code:
                current_code = row["code"]
                pdf.ln(2)
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, f"{row['code']} - {row['descrizione']}",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Helvetica", "", 10)
            where = row["struttura"] or "?"
            if row["address"]:
                where = f"{where}, {row['address']}"
            mark = "  [NUOVO]" if row["is_new"] else ""
            pdf.cell(0, 6, f"  {row['date']} {row['time']} - {where}{mark}",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
