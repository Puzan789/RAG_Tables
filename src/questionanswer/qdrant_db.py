from qdrant_client import QdrantClient, models
import uuid
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import settings

client = QdrantClient(settings.QDRANT_URL)


class QdrantConfig:
    """Configuration for Qdrant client."""

    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = "apple_collection"
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=settings.GOOGLE_EMBEDDINGS_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
        )
        self.__create_collection()

    def __create_collection(self):
        """Create a collection in Qdrant if it does not exist"""
        try:
            self.client.get_collection(self.collection_name)

        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=3072,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert_documents(self, summary_texts: list[str], md_header_splits: list):
        """
        Upsert documents into the Qdrant collection.

        Args:
            summary_texts (list[str]): List of documents to upsert.
            md_header_splits (list): List of metadata objects for each document.
        """
        points = []
        for i, text in enumerate(summary_texts):
            point_id = str(uuid.uuid4())
            vector = self.embedding_model.embed_query(text)
            # Loop through md_header_splits for each document
            header = (
                md_header_splits[i].metadata
                if hasattr(md_header_splits[i], "metadata")
                else None
            )
            page_content = (
                md_header_splits[i].page_content
                if hasattr(md_header_splits[i], "page_content")
                else None
            )
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "header": header,
                        "page_content": page_content,
                    },
                )
            )
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        return True

    def search_documents(self, query):
        """Search the  documents"""
        result = self.client.query_points(
            collection_name=self.collection_name,
            query=self.embedding_model.embed_query(query),
            query_filter=None,
            limit=3,
        )
        hits = result.points
        return hits
