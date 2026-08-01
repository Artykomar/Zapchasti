from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import import_price_rows, parse_price_import_file


class PriceImportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        upload = request.FILES.get("file")

        if not upload:
            return Response({"error": "File is required"}, status=400)

        rows = parse_price_import_file(upload.name, upload.read())
        result = import_price_rows(upload.name, upload.name.rsplit(".", 1)[-1].lower(), rows)

        return Response(
            {
                "id": result.id,
                "importedRows": result.imported_rows,
                "skippedRows": result.skipped_rows,
            },
            status=201,
        )

# Create your views here.
