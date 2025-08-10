from docling.document_converter import DocumentConverter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import settings

converter = DocumentConverter()


class DocumentChunker:
    """A class to handle document chunking and summarization."""
    def __init__(self):
        self.converter = DocumentConverter()
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ],
            strip_headers=False,
        )
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0.5
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.GOOGLE_EMBEDDINGS_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
        )

    def pdf_to_markdown(self, document_path: str):
        """
        Convert a document to markdown format.

        Args:
            document_path (str): The path to the document file.

        Returns:
            str: The content of the document in markdown format.
        """
        result = converter.convert(document_path)
        markdown = result.document.export_to_markdown()
        md_header_splits = self.markdown_splitter.split_text(markdown)
        return md_header_splits

    def create_summary(self, chunks: list[str]):
        """
        Create a summary from a list of markdown chunks.

        Args:
            chunks (list): A list of markdown chunks.

        Returns:
            str: A summary of the content.
        """
        prompt_text = """
            You are an assistant tasked with processing text and tables.

            - For **plain text** input: return the text exactly as it is, but remove all markdown formatting (no headers, bold, italics, code blocks, or lists). Preserve the original wording and meaning 
            - For **tables**: generate a concise summary that preserves all key details, important headers, and critical data points from the table.

            Respond only with the requested output, without any additional comments or introductions.
            Do not start your message with phrases like "Here is" or "Summary:".
            Just provide the plain text or table summary as requested.

            Input chunk:
            {element}
            """
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm | StrOutputParser()
        summaries = [chain.invoke({"element": chunk}) for chunk in chunks]
        return summaries
