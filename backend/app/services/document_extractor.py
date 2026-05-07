import io
import logging

try:
    import fitz # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from openpyxl import load_workbook
except ImportError:
    load_workbook = None

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """
    Servicio encargado de extraer texto de varios tipos de archivos (documentos y código).
    """

    @staticmethod
    def extract_text(filename: str, content_bytes: bytes) -> str:
        """
        Extrae el texto de un archivo dado su nombre (para inferir extensión) y sus bytes.
        Si es código o texto plano, lo decodifica.
        Si es PDF, Word o Excel, usa librerías específicas.
        Retorna el texto extraído o None si no es soportado/falla.
        """
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        # Archivos que sabemos seguro que son binarios y tienen extracción específica
        if ext == 'pdf':
            return DocumentExtractor._extract_pdf(content_bytes)
        elif ext in ['docx', 'doc']:
            return DocumentExtractor._extract_docx(content_bytes)
        elif ext in ['xlsx', 'xls']:
            return DocumentExtractor._extract_xlsx(content_bytes)
        
        # Archivos binarios ignorados por defecto (imágenes, audios, compilados)
        ignored_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4', 'exe', 'dll', 'zip', 'tar', 'gz', 'rar'}
        if ext in ignored_extensions:
            return None

        # Para cualquier otro archivo (asumimos que es código o texto plano, ej: .py, .java, .txt, o lenguajes raros)
        try:
            return content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Si falla la decodificación, probablemente sea un binario no reconocido, lo ignoramos.
            logger.warning(f"No se pudo decodificar el archivo {filename} como utf-8.")
            return None

    @staticmethod
    def _extract_pdf(content_bytes: bytes) -> str:
        if not fitz:
            logger.error("PyMuPDF (fitz) no está instalado.")
            return None
        
        try:
            text = ""
            # Cargar PDF desde memoria
            with fitz.open(stream=content_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extrayendo texto de PDF: {e}")
            return None

    @staticmethod
    def _extract_docx(content_bytes: bytes) -> str:
        if not Document:
            logger.error("python-docx no está instalado.")
            return None
        
        try:
            doc = Document(io.BytesIO(content_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extrayendo texto de DOCX: {e}")
            return None

    @staticmethod
    def _extract_xlsx(content_bytes: bytes) -> str:
        if not load_workbook:
            logger.error("openpyxl no está instalado.")
            return None
        
        try:
            # data_only=True para leer los valores, no las fórmulas
            wb = load_workbook(io.BytesIO(content_bytes), data_only=True)
            text_lines = []
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                for row in ws.iter_rows(values_only=True):
                    # Filtrar celdas vacías y unir con espacio
                    row_text = " ".join([str(cell) for cell in row if cell is not None])
                    if row_text.strip():
                        text_lines.append(row_text)
            return "\n".join(text_lines)
        except Exception as e:
            logger.error(f"Error extrayendo texto de XLSX: {e}")
            return None
