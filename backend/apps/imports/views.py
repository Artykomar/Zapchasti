from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import PriceImportParseError, import_price_rows, parse_price_import_file

ALLOWED_IMPORT_EXTENSIONS = {"csv", "xlsx"}


class PriceImportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        upload = request.FILES.get("file")

        if not upload:
            return Response({"error": "File is required"}, status=400)
        extension = upload.name.rsplit(".", 1)[-1].lower() if "." in upload.name else ""
        if extension not in ALLOWED_IMPORT_EXTENSIONS:
            return Response({"error": "Поддерживаются только CSV и XLSX файлы."}, status=400)
        if upload.size == 0:
            return Response({"error": "Файл пустой."}, status=400)

        try:
            rows = parse_price_import_file(upload.name, upload.read())
        except PriceImportParseError as exc:
            return Response({"error": str(exc)}, status=400)

        result = import_price_rows(upload.name, extension, rows)

        return Response(
            {
                "id": result.id,
                "importedRows": result.imported_rows,
                "skippedRows": result.skipped_rows,
            },
            status=201,
        )

# Create your views here.
